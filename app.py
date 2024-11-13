import streamlit as st
import base64

# ページの基本設定
st.set_page_config(page_title="文学の読書コンパニオン", page_icon="📚", layout="centered")

# ローカル画像ファイルをbase64でエンコードして背景に挿入
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_file = "吾輩は猫である.jpg.webp"  # ローカル画像ファイル名
img_base64 = get_base64_of_bin_file(img_file)

# CSSで背景画像を設定
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("data:image/webp;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.write("Streamlitアプリに和風の背景が設定されています")


# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg = """
<style>
    
    .title {
        font-size: 3rem;
        color: #ffe4b5;
        text-align: center;
        font-family: 'Yu Mincho', serif;  /* 日本語の雰囲気があるフォント */
        margin-top: 20px;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #d2b48c;
        text-align: center;
        font-family: 'Yu Mincho', serif;
        margin-top: -10px;
    }
    .btn-start {
        display: block;
        margin: 20px auto;
        padding: 10px 50px;
        background-color: #8b4513;
        color: #fff;
        font-size: 1.2rem;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# タイトルと説明
st.markdown("<div class='title'>文学と共に歩む対話の世界</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>感想を語り合い、作家の息吹に触れるひとときを</div>", unsafe_allow_html=True)

# ボット選択と開始ボタン
st.write("**読書の対話相手を選んでください**")
bot_options = ["夏目漱石ボット", "太宰治ボット", "芥川龍之介ボット"]
selected_bot = st.selectbox("対話したいボットを選択:", bot_options)

# 開始ボタン
if st.button("会話を始める"):
    st.session_state["selected_bot"] = selected_bot
    st.session_state["page"] = "chat"
    st.write(f"{selected_bot}と対話を開始します。")

# トップページから対話ページへの遷移
if "page" in st.session_state and st.session_state["page"] == "chat":
    st.write("対話画面に移動中...")  # 実際のアプリでは対話ページに移行します
