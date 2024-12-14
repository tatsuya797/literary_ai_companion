import streamlit as st

# クエリパラメータから会話履歴を取得
query_params = st.experimental_get_query_params()
messages_param = query_params.get("messages", [""])[0]

# 会話履歴をまとめるプロンプトを生成
        summarize_prompt = "これまでの会話を以下の形式で要約してください:\n\n"
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                summarize_prompt += f"ユーザー: {msg['content']}\n"
            elif msg["role"] == "assistant":
                summarize_prompt += f"AI: {msg['content']}\n"

        # OpenAI API に要約をリクエスト
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは熟練した会話の要約者です。"},
                    {"role": "user", "content": summarize_prompt}
                ]
            )
            summary = response["choices"][0]["message"]["content"]

            # 要約を表示
            st.markdown("### これまでの会話のまとめ")
            st.markdown(f"{summary}")
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

