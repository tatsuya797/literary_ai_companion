import streamlit as st
import sqlite3

def main():
    st.title("Evaluation Page")

    query_params = st.experimental_get_query_params()
    conversation_id = query_params.get("id", [None])[0]  # idパラメータ取得

    if conversation_id is None:
        st.write("IDが指定されていません。")
        return

    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT conversation, summary FROM USER WHERE id = ?", (conversation_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        conversation_json, summary_text = row[0], row[1]

        st.subheader("【会話履歴】")
        st.text_area("Conversation", conversation_json, height=250)

        st.subheader("【サマリー】")
        st.text_area("Summary", summary_text, height=150)
    else:
        st.write("該当するレコードが見つかりません。")

if __name__ == "__main__":
    main()


