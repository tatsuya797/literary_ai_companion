import streamlit as st
import openai

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

# 会話履歴を取得
if "conversation_summary" not in st.session_state:
    st.write("会話履歴が見つかりません。元のページから再試行してください。")
    st.stop()

# 会話履歴をプロンプトに整形
conversation_history = st.session_state["conversation_summary"]
summarize_prompt = "これまでの会話を以下の形式で要約してください:\n\n"
for msg in conversation_history:
    if msg["role"] == "user":
        summarize_prompt += f"ユーザー: {msg['content']}\n"
    elif msg["role"] == "assistant":
        summarize_prompt += f"AI: {msg['content']}\n"

# 会話履歴を要約
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは熟練した会話の要約者です。"},
            {"role": "user", "content": summarize_prompt}
        ]
    )
    summary = response["choices"][0]["message"]["content"]
except openai.error.OpenAIError as e:
    summary = f"要約の取得中にエラーが発生しました: {str(e)}"

# 結果を表示
st.text_area("会話の要約", summary, height=300)


