import streamlit as st

# ページの基本設定
st.set_page_config(page_title="文学の読書コンパニオン", page_icon="📚", layout="centered")

# GitHubのリポジトリにある背景画像のURL
img_url = "https://raw.githubusercontent.com/tatsuya797/openai_api_bot_akutagawa/main/image1.jpg"

# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");  /* 和風な背景画像 */
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
    .title {{
        font-size: 3rem;
        color: #ffe4b5;
        text-align: center;
        font-family: 'Yu Mincho', serif;  /* 日本語の雰囲気があるフォント */
        margin-top: 20px;
    }}
    .subtitle {{
        font-size: 1.2rem;
        color: #d2b48c;
        text-align: center;
        font-family: 'Yu Mincho', serif;
        margin-top: -10px;
    }}
    .bot-section {{
        margin-top: 80px;  /* ボット選択部分を下に移動 */
        text-align: center;  /* 中央に配置 */
        font-size: 1.2rem;
        font-family: 'Yu Mincho', serif;
    }}
    .btn-start {{
        display: block;
        margin: 20px auto;
        padding: 10px 50px;
        background-color: #8b4513;
        color: #fff;
        font-size: 1.2rem;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
    }}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# タイトルと説明
st.markdown("<div class='title'>文学と共に歩む対話の世界</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>感想を語り合い、作家の息吹に触れるひとときを</div>", unsafe_allow_html=True)

# ボット選択と開始ボタン
st.markdown("<div class='bot-section'>読書の対話相手を選んでください</div>", unsafe_allow_html=True)
bot_options = ["夏目漱石ボット", "太宰治ボット", "芥川龍之介ボット"]
selected_bot = st.selectbox("", bot_options)
st.markdown("</div>", unsafe_allow_html=True)

# 開始ボタン
if st.link_button("会話を始める", "https://github.com/tatsuya797/openai_api_bot_akutagawa/blob/main/bot.py")
    # 芥川龍之介ボットが選択された場合、bot.py にリダイレクト
    if selected_bot == "芥川龍之介ボット":
        st.write("bot.pyに移動します...")
        st.experimental_set_query_params(page="bot")  # クエリパラメータを設定
        st.stop()  # 残りのコードの実行を停止

    # その他の選択肢
    else:
        st.session_state["selected_bot"] = selected_bot
        st.session_state["page"] = "chat"
        st.write(f"{selected_bot}と対話を開始します。")

# トップページから対話ページへの遷移
if "page" in st.session_state and st.session_state["page"] == "chat":
    st.write("対話画面に移動中...")  # 実際のアプリでは対話ページに移行します
