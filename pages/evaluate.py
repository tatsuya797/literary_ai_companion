import streamlit as st

# クエリパラメータから会話履歴を取得
query_params = st.experimental_get_query_params()
messages_param = query_params.get("messages", [""])[0]

# 会話履歴を整形
if messages_param:
    messages = messages_param.split("|")
    st.title("これまでの会話のまとめ")
    st.write("以下があなたとAIの会話履歴です:")

    for message in messages:
        if message.startswith("user:"):
            st.markdown(f"**ユーザー:** {message[5:]}")
        elif message.startswith("assistant:"):
            st.markdown(f"**AI:** {message[10:]}")
else:
    st.write("会話履歴がありません。")

