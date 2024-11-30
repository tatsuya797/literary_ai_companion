from pathlib import Path
import pandas as pd
import sqlite3  # SQLite3を使用
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai

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

# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");  /* 和風な背景画像 */
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# クエリパラメータを取得
query_params = st.experimental_get_query_params()
selected_title = query_params.get("title", [None])[0]  # クエリパラメータ "title" を取得

if selected_title:
    def fetch_text_content(title):
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT text_content FROM BOT WHERE title = ?", (title,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "該当する内容が見つかりません。"

    if "text_content" not in st.session_state:
        st.session_state["text_content"] = fetch_text_content(selected_title)
    text_content = st.session_state["text_content"]

    st.write(f"選択された作品: 『{selected_title}』")
    st.text_area("作品の内容", text_content, height=300)
else:
    st.error("作品が選択されていません。URLにクエリパラメータ 'title' を含めてください。")
    st.stop()

# ChatGPTの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting}
    ]
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0

def communicate():
    text_content = st.session_state["text_content"]
    messages = st.session_state["messages"]
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)
    st.session_state["total_characters"] += len(user_message["content"])

    max_length = 2000  # トークン制限対策
    if len(text_content) > max_length:
        text_content = text_content[:max_length] + "..."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": st.secrets.AppSettings.chatbot_setting},
            {"role": "user", "content": f"参考文章:\n\n{text_content}"},
        ] + messages
    )
    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)
    st.session_state["user_input"] = ""

# ユーザーインターフェイス
st.title(author_name + "チャットボット")
st.write(author_name + "の作品に基づいたチャットボットです。")

if st.text_area("メッセージを入力してください", key="user_input", height=100, on_change=communicate):
    pass

if st.button("対話終了"):
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting}
    ]
    st.session_state["total_characters"] = 0
    st.success("対話が終了しました。リセットしました。")


# カスタム CSS を追加して左右分割のスタイルとアイコンを設定
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
        white-space: pre-wrap; /* 改行をサポート */
    }
    .bot-content {
        background-color: #f1f0f0;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        text-align: left;
        white-space: pre-wrap; /* 改行をサポート */
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

                </div>
                """,
                unsafe_allow_html=True,
            )
