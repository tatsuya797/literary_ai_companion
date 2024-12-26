import streamlit as st
import sqlite3
import json

def show_db_contents():
    """USERテーブルの全レコードをSELECTして表示"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    # USERテーブルの内容をすべて取得 (SELECT *)
    cur.execute("SELECT * FROM USER")
    rows = cur.fetchall()

    # 取得したカラム名をリスト化
    column_names = [description[0] for description in cur.description]
    
    conn.close()
    
    st.write("### USERテーブル内容（全カラム表示）")
    import pandas as pd
    df = pd.DataFrame(rows, columns=column_names)
    st.dataframe(df)


def update_or_insert_conversation(username, title, conversation_json, summary_text):
    """
    ログイン中のユーザーとタイトルに対応するレコードがあればUPDATE、なければINSERTする
    """
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # 1) (username, title) に対応するレコードが既にあるか確認
    cur.execute("""
        SELECT id FROM USER 
        WHERE username = ? AND title = ?
    """, (username, title))
    row = cur.fetchone()

    if row:
        # 既にレコードがある → UPDATE
        user_id = row[0]
        cur.execute("""
            UPDATE USER
            SET conversation = ?, summary = ?
            WHERE id = ?
        """, (conversation_json, summary_text, user_id))
    else:
        # まだレコードが無い → INSERT
        cur.execute("""
            INSERT INTO USER (username, title, conversation, summary)
            VALUES (?, ?, ?, ?)
        """, (username, title, conversation_json, summary_text))

    conn.commit()
    conn.close()


def main():
    st.title("Evaluation & DB確認ツール")
    st.write("DEBUG: username =", st.session_state.get("username"))

    # ========== ① 会話履歴＆サマリーを更新する処理 ========== #
    st.subheader("会話履歴の保存・更新テスト")

    # ログイン中のユーザー名 (セッションに格納済みとして仮定)
    # 実際は「st.session_state['username']」を使うことを想定
    if "username" not in st.session_state:
        st.session_state["username"] = "sample_user"  # テスト用ダミー
    username = st.session_state["username"]

    # "title" はページ遷移などで保持している想定
    # ここではクエリパラメータ "title" から取得する例
    query_params = st.experimental_get_query_params()
    current_title = query_params.get("title", [None])[0]

    if not current_title:
        st.info("title パラメータが指定されていないため、DB更新は行えません。")
    else:
        st.write(f"**ログインユーザー名**: {username}")
        st.write(f"**作品タイトル**: {current_title}")

        # ここでは会話JSON／サマリーを適当に記入 or 取得して更新する想定
        conversation_json = st.text_area(
            "会話JSON（例: [{'role': 'user', 'content': '...'}, ...]）",
            value='[{"role": "user", "content": "こんにちは"}, {"role": "assistant", "content": "いらっしゃいませ"}]',
            height=150
        )
        summary_text = st.text_area(
            "サマリーテキスト",
            value="ユーザーとの対話をまとめました。",
            height=80
        )

        if st.button("DBに保存 / 更新"):
            update_or_insert_conversation(username, current_title, conversation_json, summary_text)
            st.success("USERテーブルを更新しました。")

    st.write("---")

    # ========== ② DBの全レコードを一覧表示 ========== #
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()


if __name__ == "__main__":
    main()
