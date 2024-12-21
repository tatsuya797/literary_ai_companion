import streamlit as st
import sqlite3

def show_db_contents():
    """USERテーブルの全レコードをSELECTして表示"""
    db_file = "literary_app.db"  # 使っているDBファイル名を指定
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    # USERテーブルの内容をすべて取得
    cur.execute("SELECT id, conversation, summary FROM USER")
    rows = cur.fetchall()
    conn.close()
    
    # Streamlit上で見やすく表示
    st.write("### USERテーブル内容 (上書き方式)")
    for row in rows:
        record_id = row[0]
        conversation_json = row[1]
        summary_text = row[2]

        st.write(f"**ID**: {record_id}")
        st.write(f"**Conversation**: {conversation_json}")
        st.write(f"**Summary**: {summary_text}")
        st.write("---")

def main():
    st.title("Evaluation & DB確認ツール")

    # テーブルが無ければ作成（idをPRIMARY KEYとする）
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY,
            conversation TEXT,
            summary TEXT
        )
    """)
    conn.close()

    # ========== ① クエリパラメータ id をもとにレコードを表示/上書き ========== #
    st.subheader("Evaluation Page")
    query_params = st.experimental_get_query_params()
    conversation_id = query_params.get("id", [None])[0]  # idパラメータ取得
    
    if conversation_id:
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        # 既存レコードの有無を確認
        cur.execute("SELECT conversation, summary FROM USER WHERE id = ?", (conversation_id,))
        row = cur.fetchone()

        if row:
            conversation_json, summary_text = row
        else:
            conversation_json, summary_text = "", ""

        conn.close()

        st.write(f"**対象レコードID**: {conversation_id}")

        st.subheader("【会話履歴の編集 (JSONテキストなど)】")
        conversation_json = st.text_area(
            "Conversation",
            conversation_json,
            height=250
        )

        st.subheader("【サマリーの編集】")
        summary_text = st.text_area("Summary", summary_text, height=150)

        if st.button("この内容でDBに上書き保存"):
            # DBに上書き保存 (INSERT OR REPLACE)
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO USER (id, conversation, summary)
                VALUES (?, ?, ?)
            """, (conversation_id, conversation_json, summary_text))
            conn.commit()
            conn.close()
            st.success(f"ID={conversation_id} のレコードを上書き保存しました。")

    else:
        st.write("IDが指定されていません。クエリパラメータ ?id=○○ を付与してください。")

    st.write("---")

    # ========== ② ボタン押下でDBの全レコードを一覧表示 ========== #
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()

