import streamlit as st
import openai
import ast  # 文字列を辞書形式に変換するために使用
import urllib.parse  # クエリパラメータのデコード用
import json


# Streamlit Community Cloud の「Secrets」から OpenAI API キーを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# ページ設定
st.set_page_config(
    page_title="会話の要約",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("会話の要約ページ")



# セッションステートから会話履歴を取得
if "messages" in st.session_state and st.session_state["messages"]:
    messages = st.session_state["messages"]

    # 会話履歴をまとめるプロンプトを生成
    summarize_prompt = "これまでの会話を以下の形式で要約してください:\n\n"
    full_history = ""
    for msg in messages:
        if msg["role"] == "user":
            summarize_prompt += f"ユーザー: {msg['content']}\n"
            full_history += f"ユーザー: {msg['content']}\n"
        elif msg["role"] == "assistant":
            summarize_prompt += f"AI: {msg['content']}\n"
            full_history += f"AI: {msg['content']}\n"

    # 会話履歴を表示
    st.text_area("これまでの会話履歴", full_history, height=300)

    # OpenAI API を使って会話の要約を生成
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは熟練した会話の要約者です。"},
            {"role": "user", "content": summarize_prompt}
        ]
    )
    summary = response["choices"][0]["message"]["content"]

    # 要約を表示
    st.text_area("会話の要約", summary, height=200)
else:
    st.write("会話履歴が見つかりませんでした。")

# 「再開する」ボタン
if st.button("再開する"):
    st.experimental_rerun()
