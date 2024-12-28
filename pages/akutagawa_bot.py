from pathlib import Path
import pandas as pd
import sqlite3  # SQLite3を使用
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai
import json
import urllib.parse

author_id = '000879'
author_name = '芥川龍之介'

st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)

img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image2.jpg"
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# --- クエリパラメータ ---
query_params = st.experimental_get_query_params()
current_username = query_params.get("username", [None])[0]  # username
selected_title = query_params.get("title", [None])[0]       # title

# データベース接続
def fetch_text_content(title):
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT text_content FROM BOT WHERE title = ?", (title,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "該当する内容が見つかりません。"

# ---- ページ上部の表示 ----
if selected_title:
    text_content = fetch_text_content(selected_title)
    st.markdown(
        f"""
        <p style="
            font-size: 2.5rem; 
            font-weight: bold; 
            color: #8b4513; 
            font-family: 'Yu Mincho', serif;
            text-align: center; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        ">
            📚 作品名: 『{selected_title}』
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="
            padding: 20px; 
            margin: 20px 0; 
            background-color: #fffbea; 
            border: 2px solid #d4af37; 
            border-radius: 10px; 
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
            font-family: 'Yu Mincho', serif; 
            font-size: 1.1rem; 
            line-height: 1.8; 
            color: #333;
            text-align: justify;
            overflow: auto;
            height: 300px;
        ">
            {text_content}
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.write("作品が選択されていません。URLのクエリパラメータを確認してください。")

# --- OpenAI API キー設定 ---
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_state の初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting}
    ]
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0

# --- 対話関数 ---
def communicate():
    text_content_local = fetch_text_content(selected_title)
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)
    st.session_state["total_characters"] += len(user_message["content"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは熟練した文学解説者です。以下の文章を理解し、質問に答えてください。"},
            {"role": "user", "content": f"参考文章:\n\n{text_content_local}"},
        ] + messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)
    st.session_state["user_input"] = ""

def summarize_conversation(messages):
    """会話履歴を400文字にまとめた要約を作成"""
    summary_prompt = [
        {"role": "system", "content": "以下の会話履歴を400文字にまとめた要約を作成してください。"},
        {"role": "user", "content": json.dumps(messages, ensure_ascii=False)}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=summary_prompt
    )
    return response["choices"][0]["message"]["content"]

def update_conversation_and_summary(username, title, conversation_json, summary_text):
    """
    USERテーブルの (username, title) に合致する行を更新し、
    conversation と summary を上書きする
    """
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()

    # 必要ならUSERテーブルを拡張
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            author TEXT,
            title TEXT,
            conversation TEXT,
            summary TEXT,
            Relevance INTEGER,
            Creativity INTEGER,
            Flexibility INTEGER,
            Problem_Solving INTEGER,
            Insight INTEGER
        )
    """)

    # レコードが無い場合はINSERT、ある場合はUPDATEにするなら「UPSERT」か「SELECT→UPDATE or INSERT」などの方法も
    # ここではシンプルにUPDATEのみ実装（該当行がないと影響なし）
    cur.execute("""
        UPDATE USER
        SET conversation = ?, summary = ?
        WHERE username = ? AND title = ?
    """, (conversation_json, summary_text, username, title))

    # もし該当行が無かった場合にINSERTしたいなら、以下のようなロジックを追加:
    if cur.rowcount == 0:
        # 該当行が無かった -> 新規追加
        cur.execute("""
            INSERT INTO USER (username, title, conversation, summary)
            VALUES (?, ?, ?, ?)
        """, (username, title, conversation_json, summary_text))

    conn.commit()
    conn.close()

def finalize_conversation(messages, username, title):
    """
    会話の要約を生成し、(conversation, summary) を DB に保存する
    """
    # システムメッセージを除外
    filtered_messages = [m for m in messages if m["role"] in ("user", "assistant")]
    conversation_json = json.dumps(filtered_messages, ensure_ascii=False)
    summary_text = summarize_conversation(filtered_messages)

    # DBにUPDATE (無ければINSERT)
    update_conversation_and_summary(username, title, conversation_json, summary_text)

# --- 対話終了ボタン ---
if st.session_state["total_characters"] >= 10:
    if st.button("対話終了"):
        # 会話をDBに保存
        finalize_conversation(st.session_state["messages"], current_username, selected_title)

        # 次画面(evaluate) へ遷移
        evaluate_url = (
            "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/evaluate"
            f"?username={current_username}"
            f"&title={selected_title}"
        )
        st.markdown(f'<meta http-equiv="refresh" content="0; url={evaluate_url}">', unsafe_allow_html=True)

# --- 画面下部: ユーザー入力欄 ---
st.markdown(
    f"""
    <label style="
        font-size: 1rem; 
        font-weight: bold; 
        color: white; 
        display: block; 
        margin-bottom: 10px;
    ">
        『{selected_title or "未指定"}』を読んだ感想を聞かせてください！
    </label>
    """,
    unsafe_allow_html=True,
)

user_input = st.text_area(
    "",
    key="user_input",
    height=100,
    on_change=communicate
)

# --- 対話履歴の表示 ---
st.markdown(
    """
    <style>
    .user-message {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 10px 0;
    }
    .bot-message {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin: 10px 0;
    }
    .message-content {
        background-color: #dcf8c6;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        text-align: left;
        white-space: pre-wrap;
    }
    .bot-content {
        background-color: #f1f0f0;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        text-align: left;
        white-space: pre-wrap;
    }
    .icon {
        font-size: 1.5rem;
        margin: 0 10px;
    }
    .red-button {
        background-color: white;
        color: red;
        font-size: 16px;
        font-weight: bold;
        border: 2px solid red;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
    }
    .red-button:hover {
        background-color: red;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("messages"):
    messages = st.session_state["messages"]
    for message in reversed(messages[1:]):  # システムメッセージは除く
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class="user-message">
                    <span class="icon">😊</span>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"""
                <div class="bot-message">
                    <div class="bot-content">{message["content"]}</div>
                    <span class="icon">🤖</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
