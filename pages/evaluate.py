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


# クエリパラメータから会話履歴を取得
query_params = st.experimental_get_query_params()
messages_query = query_params.get("messages", [None])[0]

if messages_query:
    # デコード後に JSON を解析
    decoded_query = urllib.parse.unquote(messages_query)
    try:
        messages = json.loads(decoded_query)

        # 会話履歴をまとめるプロンプトを生成
        summarize_prompt = "これまでの会話を以下の形式で要約してください:\n\n"
        full_history = ""  # 会話履歴を文字列として格納

        for msg in messages:
            if msg["role"] == "user":
                summarize_prompt += f"ユーザー: {msg['content']}\n"
                full_history += f"ユーザー: {msg['content']}\n"
            elif msg["role"] == "assistant":
                summarize_prompt += f"AI: {msg['content']}\n"
                full_history += f"AI: {msg['content']}\n"

        # OpenAI API に要約をリクエスト
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは熟練した会話の要約者です。"},
                {"role": "user", "content": summarize_prompt}
            ]
        )
        summary = response["choices"][0]["message"]["content"]

        # 会話履歴をテキストボックスに表示
        st.text_area("これまでの会話履歴", full_history, height=300)

        # 要約をテキストボックスに表示
        st.text_area("会話の要約", summary, height=300)

    except json.JSONDecodeError as e:
        st.error(f"クエリパラメータのデコードに失敗しました: {e}")
else:
    st.write("会話履歴が見つかりませんでした。")

