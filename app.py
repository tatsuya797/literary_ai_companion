import streamlit as st
import sqlite3
import hashlib

# ページ設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed"
)

# 背景画像設定
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image1.jpg"
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            color: #f4f4f4;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ユーティリティ関数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
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

def register_user(username, password):
    try:
        conn = sqlite3.connect("literary_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO USERS (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        st.success("登録に成功しました！ログインしてください。")
    except sqlite3.IntegrityError:
        st.error("このユーザ名は既に登録されています。")
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = cur.fetchone()
    conn.close()
    return user

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

# ログイン・登録フォーム
if not st.session_state["logged_in"]:
    st.markdown("<h3>ログイン</h3>", unsafe_allow_html=True)
    username = st.text_input("ユーザ名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if authenticate_user(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"ようこそ、{username}さん！")
        else:
            st.error("ユーザ名またはパスワードが間違っています。")

    st.markdown("<h4>新規登録</h4>", unsafe_allow_html=True)
    new_username = st.text_input("新規ユーザ名", key="register_username")
    new_password = st.text_input("新規パスワード", type="password", key="register_password")
    if st.button("登録"):
        if new_username and new_password:
            register_user(new_username, new_password)
        else:
            st.error("ユーザ名とパスワードを入力してください。")

# ログイン後の画面
if st.session_state["logged_in"]:
    st.markdown(f"<h3>こんにちは、{st.session_state['username']}さん！</h3>", unsafe_allow_html=True)
    st.markdown("<h4>読書の対話相手を選んでください</h4>", unsafe_allow_html=True)
    
    bot_options = ["夏目漱石", "太宰治", "芥川龍之介"]
    selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")

    if selected_bot == "芥川龍之介":
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める"):
                url = f"https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/akutagawa_bot?title={selected_title}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        else:
            st.error("作品リストを取得できませんでした。")
    else:
        st.write(f"{selected_bot}との対話を開始する準備が整いました。")

    if st.button("ログアウト"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.experimental_rerun()
