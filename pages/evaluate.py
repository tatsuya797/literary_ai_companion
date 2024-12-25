import streamlit as st
import sqlite3
import pandas as pd

########################
# DB関連の関数
########################
def init_db():
    """USERテーブルを作成（必要なら）"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    # 例として、usernameをキーにして、conversation/summaryを1ユーザ1レコードで保持
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            conversation TEXT,
            summary TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_user_record(username: str):
    """username をキーに USERテーブルから1件取得"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT conversation, summary FROM USER WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    # 見つかったら (conversation, summary) のタプル、無ければ None
    return row

def upsert_user_record(username: str, conversation: str, summary: str):
    """
    usernameをキーとして、conversation/summaryを上書き保存。
    該当ユーザがいなければINSERT、存在すればUPDATE。
    """
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # まず既存レコードがあるか確認
    cur.execute("SELECT id FROM USER WHERE username = ?", (username,))
    existing = cur.fetchone()

    if existing:
        # UPDATE
        cur.execute("""
            UPDATE USER
            SET conversation = ?, summary = ?
            WHERE username = ?
        """, (conversation, summary, username))
    else:
        # INSERT (usernameにUNIQUE制約を付けてある想定)
        cur.execute("""
            INSERT INTO USER (username, conversation, summary)
            VALUES (?, ?, ?)
        """, (username, conversation, summary))

    conn.commit()
    conn.close()

def show_db_contents():
    """USERテーブルの全レコードをSELECTして表示（全カラム）"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT * FROM USER")  # 全カラム取得
    rows = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]  # カラム名
    conn.close()

    st.write("### USERテーブル内容（全カラム表示）")
    df = pd.DataFrame(rows, columns=column_names)
    st.dataframe(df)


########################
# メインアプリ
########################
def main():
    st.title("ログインユーザの会話履歴管理ツール")

    # DB初期化（必要なら最初に実行）
    init_db()

    # --- 1) ログインフォームで username を入力 ---
    st.subheader("ユーザのログイン/選択")
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    with st.form(key="login_form"):
        input_username = st.text_input("ユーザ名を入力", st.session_state["username"])
        submitted = st.form_submit_button("ログイン/変更")
        if submitted:
            st.session_state["username"] = input_username
            st.success(f"ユーザ名を {st.session_state['username']} に設定しました。")

    current_user = st.session_state["username"]

    if not current_user:
        st.warning("ユーザ名が未設定です。上のフォームに入力してください。")
        return

    st.write(f"現在のユーザ: **{current_user}**")

    st.write("---")

    # --- 2) 現在のユーザについてDBから conversation, summary を取得&表示 ---
    st.subheader("会話履歴とサマリーを確認/編集")
    record = get_user_record(current_user)
    if record:
        conversation_db, summary_db = record
        st.write("**既存の conversation:**")
        st.text_area("conversation_db", conversation_db, height=150)
        st.write("**既存の summary:**")
        st.text_area("summary_db", summary_db, height=100)
    else:
        st.info("まだこのユーザのレコードは存在しません。")

    # --- 3) conversation, summary を上書き保存する ---
    st.write("#### 新しい会話履歴とサマリーを入力して上書き")
    new_conv = st.text_area("新しいConversationを入力", height=100)
    new_sum = st.text_area("新しいSummaryを入力", height=80)
    if st.button("上書き保存"):
        upsert_user_record(current_user, new_conv, new_sum)
        st.success("DBに上書き保存しました。再読み込みすると反映が見られます。")

    st.write("---")

    # --- 4) DBの全レコードを一覧表示 ---
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
