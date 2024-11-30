import streamlit as st
import sqlite3  # SQLite3を使用

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
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image1.jpg"

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
bot_options = ["夏目漱石", "太宰治", "芥川龍之介"]
selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")  # keyを追加
st.markdown("</div>", unsafe_allow_html=True)

# 芥川龍之介ボットの選択に応じた処理
if selected_bot == "芥川龍之介":
    # データベースから作品リストを取得
    def fetch_titles_from_db():
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT title FROM BOT")
        rows = cur.fetchall()
        conn.close()
        return [row[0] for row in rows]

    # タイトルリストを取得
    titles = fetch_titles_from_db()
    if titles:
        selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")  # keyを追加
        if st.button("会話を始める", key="start_conversation"):  # keyを追加
           url = "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/akutagawa_bot"
           st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
           st.markdown(
               f'<a href="https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/akutagawa_bot" class="btn-start">会話を始める</a>',
               unsafe_allow_html=True,
            )
           
    else:
        st.write("作品リストを取得できませんでした。データベースを確認してください。")

else:
    # 他のボットが選択された場合の処理
    st.write(f"{selected_bot}との対話を開始する準備が整いました。")
    if st.button("会話を始める", key="start_conversation_others"):  # keyを追加
        st.write(f"{selected_bot}との対話画面に遷移します。")

# トップページから対話ページへの遷移
if "page" in st.session_state and st.session_state["page"] == "chat":
    st.write("対話画面に移動中...")  # 実際のアプリでは対話ページに移行します

# 芥川ボットの選択に応じてリンクボタンを表示
if selected_bot == "芥川龍之介":
    st.write("会話を始めるボタンを押すと bot.py に移動します。")
    
