import streamlit as st
import sqlite3
import json

# データベースから直近で保存した会話履歴とサマリーを取得する関数
def get_last_conversation_and_summary():
    db_file = "literary_app.db"  # データベースファイルのパス
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # id が最大（最後にINSERTされた）レコードを1件取得
    cur.execute("SELECT conversation, summary FROM USER ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if row:
        conversation_json = row[0]
        summary_text = row[1]
        return conversation_json, summary_text
    else:
        return None, None

def main():
    st.set_page_config(
        page_title="Evaluation Page",
        page_icon="🔍",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    st.title("対話の評価ページ")

    # データベースから最後に保存した会話履歴と要約を取得
    conversation_json, summary_text = get_last_conversation_and_summary()

    if conversation_json and summary_text:
        st.subheader("【保存された会話履歴（JSON形式）】")
        st.text_area(
            label="Conversation",
            value=conversation_json,
            height=250
        )

        st.subheader("【保存されたサマリー】")
        st.text_area(
            label="Summary",
            value=summary_text,
            height=150
        )
    else:
        st.write("データが存在しません。対話を終了していないか、DBに保存されていません。")

if __name__ == "__main__":
    main()

