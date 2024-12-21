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
    st.write("### USERテーブル内容")
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

    # ========== ①の機能: クエリパラメータ id をもとにレコードを表示 ========== #
    st.subheader("Evaluation Page")
    query_params = st.experimental_get_query_params()
    conversation_id = query_params.get("id", [None])[0]  # idパラメータ取得
    
    if conversation_id:
        # id が取得できた場合
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT conversation, summary FROM USER WHERE id = ?", (conversation_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            conversation_json, summary_text = row[0], row[1]
            st.write(f"**対象レコードID**: {conversation_id}")

            st.subheader("【会話履歴】")
            st.text_area("Conversation", conversation_json, height=250)

            st.subheader("【サマリー】")
            st.text_area("Summary", summary_text, height=150)
        else:
            st.write("該当するレコードが見つかりません。")
    else:
        st.write("IDが指定されていません。クエリパラメータ ?id=○○ を付与してください。")

    st.write("---")

    # ========== ②の機能: ボタン押下でDBの全レコードを一覧表示 ========== #
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
