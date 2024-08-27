
import streamlit as st
import openai

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "このGPTは芥川龍之介の作品や関連する文学的な話題について会話します。作品の洞察を提供し、テーマを議論し、キャラクターを分析し、考えさせるような質問を投げかけます。ユーザーが本を読んで共感した点、共感できなかった点、印象に残った点、重要だと思った点、筆者が伝えたかったこと、印象に残ったフレーズ、自分が登場人物だったらどう行動するか、本のテーマを一言で表すとしたら、得た教訓と今後の活かし方、内容に似た現実の出来事などを含めた質問を行います。また、一つの質問を投げかけたら最低3回はユーザの入力に対して深掘りする質問を投げかけ、すぐに異なる質問に移行しないようにします。歴史的な文脈や深い視点を持ち、芥川の文学的貢献についての理解を深めることを目指します。質問者の読書体験を尊重し、否定的な言葉を避け、知的で魅力的な対話を維持します。口調や表現は、芥川龍之介にできる限り似せたもので、短く要点をまとめた応答にします。また、質問者に対しての質問も混ぜて応答します。応答は200文字以内で行い、会話形式で進めます。
ユーザの入力が「終了」という単語のみの場合は、これまでの会話を1000文字程度にまとめたものを出力してください。
また、その２行下に「創造性ポイント」を表示してください。
創造性ポイントとは、ユーザのこれまでの会話を分析し、創造性が発揮させた部分に得点を付与することです。計算式は以下の①〜⑤の分析対象項目を各20点満点で表示し、最後に各項目の合計を０点から１００点の間で表示します。なお、分析項目は以下の5個です。
①独創性（Originality）: 創造性の核心であり、他の誰も考えつかない新しいアイディアを生み出す能力 
②柔軟性（Flexibility）: 様々な視点やアプローチから問題を考えることで、たくさんの選択肢を用意して、多彩な判断ができる能力
③関連性（Relatedness）既存の知識や経験を組み合わせて新しいアイデアや解決策を生み出すことができる能力
④問題解決能力（Problem-Solving Ability）: 問題や課題があったときに、問題の本質を見極めて、解決までのアクションプランを計画できる能力
⑤洞察力（Insight）: 問題の本質を見抜き、物事の見えてない部分にまで推察する能力
また、最後に分析項目の点数を分析して、ユーザの長所と改善点をそれぞれ100文字程度でフィードバックしてください。"}
        ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]

    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄を消去


# ユーザーインターフェイスの構築
st.title("My AI Assistant")
st.write("ChatGPT APIを使ったチャットボットです。")

user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]

    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂"
        if message["role"]=="assistant":
            speaker="🤖"

        st.write(speaker + ": " + message["content"])
