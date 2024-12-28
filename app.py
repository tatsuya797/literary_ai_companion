import streamlit as st
import sqlite3  # SQLite3を使用
import hashlib

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
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
    .title {{
        font-size: 3rem;
        color: #ffe4b5;
        text-align: center;
        font-family: 'Yu Mincho', serif;
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
        margin-top: 80px;
        text-align: center;
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

# ユーティリティ関数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DBがなければ作成
def init_db():
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS BOT (
            title TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ユーザの新規登録
def register_user(username, password):
    """
    新規ユーザーを登録し、AUTO INCREMENTされたidを返す
    """
    some_id = None
    try:
        conn = sqlite3.connect("literary_app.db")
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO USER (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()

        some_id = cur.lastrowid  # 自動採番されたID
        st.success("登録に成功しました！ログインしてください。")
    except sqlite3.IntegrityError:
        st.error("このユーザ名は既に登録されています。")
    finally:
        conn.close()

    return some_id

# ユーザが存在するかどうかを確認（認証）
def authenticate_user(username, password):
    """
    ログイン時にid, username, passwordの行を取り出し、
    該当すれば(idを返す)、なければNoneを返す
    """
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password FROM USER WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    user = cur.fetchone()
    conn.close()

    if user:
        # user[0] がid, user[1]がusername, user[2]がpassword
        return user[0]  # idを返す
    else:
        return None

def fetch_titles_from_db():
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("SELECT title FROM BOT")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

# データベース初期化
init_db()

# セッション状態管理
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None  # ここにAUTO INCREMENTされたIDを保持

# ログイン・新規登録をタブで切り替え
tabs = st.tabs(["ログイン", "新規登録"])

# ログインフォーム
with tabs[0]:
    st.markdown("<h3>ログイン</h3>", unsafe_allow_html=True)
    username = st.text_input("ユーザ名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        found_id = authenticate_user(username, password)
        if found_id is not None:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["user_id"] = found_id
            st.success(f"ようこそ、{username}さん！ (ID: {found_id})")
        else:
            st.error("ユーザ名またはパスワードが間違っています。")

# 新規登録フォーム
with tabs[1]:
    st.markdown("<h3>新規登録</h3>", unsafe_allow_html=True)
    new_username = st.text_input("新規ユーザ名")
    new_password = st.text_input("新規パスワード", type="password")
    if st.button("登録"):
        if new_username and new_password:
            new_id = register_user(new_username, new_password)
            # 新規登録のあと自動ログインさせたい場合は、以下のようにする
            if new_id is not None:
                st.session_state["logged_in"] = True
                st.session_state["username"] = new_username
                st.session_state["user_id"] = new_id
        else:
            st.error("ユーザ名とパスワードを入力してください。")

# ログイン後の画面
if st.session_state["logged_in"]:
    st.markdown(f"<h3>こんにちは、{st.session_state['username']}さん！</h3>", unsafe_allow_html=True)
    st.write(f"あなたのID: {st.session_state['user_id']}")
    
    # ボット選択と開始ボタン
    st.markdown("<div class='bot-section'>読書の対話相手を選んでください</div>", unsafe_allow_html=True)
    bot_options = ["夏目漱石", "太宰治", "芥川龍之介"]
    selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")
    st.markdown("</div>", unsafe_allow_html=True)

    # 芥川龍之介ボットの選択に応じた処理
    if selected_bot == "芥川龍之介":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                # ページ遷移
                user_id = st.session_state["user_id"]  # ログイン時に取得したID
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/akutagawa_bot"
                    f"?id={user_id}"
                    f"&username={st.session_state['username']}"
                    f"&author={selected_bot}"
                    f"&title={selected_title}"
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        else:
            st.write("作品リストを取得できませんでした。データベースを確認してください。")
    
    # 他のボットが選択された場合の処理
    elif selected_bot in ["夏目漱石", "太宰治"]:
        st.write(f"{selected_bot}との対話を開始する準備が整いました。")
        if st.button("会話を始める", key="start_conversation_others"):
            st.write(f"{selected_bot}との対話画面に遷移します。")
