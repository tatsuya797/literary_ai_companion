from pathlib import Path
import pandas as pd
import sqlite3  # SQLite3を使用
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai
import json
import urllib.parse

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

# ページの基本設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",  # サイドバーを非表示
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)

# GitHubのリポジトリにある背景画像のURL
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image2.jpg"

# 背景画像の設定
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

# クエリパラメータを取得
query_params = st.experimental_get_query_params()
current_id = query_params.get("id", [""])[0]       # ユーザーを識別するID (user_id)
current_username = query_params.get("username", [""])[0]
selected_author = query_params.get("author", [""])[0]
selected_title = query_params.get("title", [""])[0]

# データベース接続用関数
def fetch_text_content(title):
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    # BOT テーブルからタイトルに対応する text_content を取得
    cur.execute("SELECT text_content FROM BOT WHERE title = ?", (title,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "該当する内容が見つかりません。"

# テキスト内容を取得＆表示
if selected_title:
    text_content = fetch_text_content(selected_title)

    # 作品名
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

    # 作品内容
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

# OpenAIキーの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# セッション初期化
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting} 
    ]
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0

# 対話用関数
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

    # 入力欄をクリア
    st.session_state["user_input"] = ""

# 画面タイトル
st.markdown(
    f"""
    <div style="
        display: flex; 
        align-items: center; 
        justify-content: center; 
        margin-top: 20px;
    ">
        <span style="
            font-size: 2.5rem; 
            margin-right: 10px;
        ">🖋</span>
        <h1 style="
            font-size: 2.5rem; 
            font-family: 'Yu Mincho', serif; 
            font-weight: bold; 
            color: #8b4513; 
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        ">{author_name}チャットボット</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

def summarize_conversation(messages):
    """会話履歴を400文字にまとめる"""
    summary_prompt = [
        {"role": "system", "content": "以下の会話履歴を400文字にまとめた要約を作成してください。"},
        {"role": "user", "content": json.dumps(messages, ensure_ascii=False)}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=summary_prompt
    )
    return response["choices"][0]["message"]["content"]

def save_conversation_and_summary_to_db(
    messages, user_id_value, username_value, author_value, title_value
):
    """
    USERテーブルに以下のカラムをINSERT:
      - id: AUTOINCREMENT (会話記録固有)
      - user_id: クエリパラメータで受け取ったユーザーID
      - username
      - author
      - title
      - conversation
      - summary
    """
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()

    # テーブル定義
    cur.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            username TEXT,
            author TEXT,
            title TEXT,
            conversation TEXT,
            summary TEXT
        )
    """)

    # システムメッセージ以外を抽出
    filtered_messages = [m for m in messages if m["role"] in ("user", "assistant")]
    conversation_json = json.dumps(filtered_messages, ensure_ascii=False)
    summary_text = summarize_conversation(filtered_messages)

    # INSERT (id は自動採番される)
    cur.execute(
        """
        INSERT INTO USER (user_id, username, author, title, conversation, summary)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id_value, username_value, author_value, title_value, conversation_json, summary_text)
    )
    conn.commit()
    conn.close()

    return conversation_json, summary_text

# 対話終了ボタン
if st.session_state["total_characters"] >= 10:
    if st.button("対話終了"):
        # DBに保存 (idはAUTOINCREMENT、 user_id= current_id)
        conversation_json, summary_text = save_conversation_and_summary_to_db(
            st.session_state["messages"],
            current_id,      # user_id
            current_username,
            selected_author,
            selected_title
        )

        # URLへ遷移パラメータに conversation, summary
        conversation_encoded = urllib.parse.quote(conversation_json)
        summary_encoded = urllib.parse.quote(summary_text)

        evaluate_url = (
            "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/evaluate"
            f"?id={current_id}"             # user_id
            f"&username={current_username}"
            f"&author={selected_author}"
            f"&title={selected_title}"
            f"&conversation={conversation_encoded}"
            f"&summary={summary_encoded}"
        )
        st.markdown(f'<meta http-equiv="refresh" content="0; url={evaluate_url}">', unsafe_allow_html=True)

# ラベルをカスタマイズして表示
st.markdown(
    f"""
    <label style="
        font-size: 1rem; 
        font-weight: bold; 
        color: white; 
        display: block; 
        margin-bottom: 10px;
    ">
        『{selected_title}を読んだ感想を聞かせてください！』
    </label>
    """,
    unsafe_allow_html=True,
)

# ユーザーのメッセージ入力欄
user_input = st.text_area(
    "",
    key="user_input",
    height=100,
    on_change=communicate
)

# カスタムCSS
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

# 対話履歴を表示
if st.session_state.get("messages"):
    messages = st.session_state["messages"]
    # 最新メッセージを上にするために逆順にループ
    for message in reversed(messages[1:]):  # システムメッセージを除く
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
