import streamlit as st
import sqlite3  # SQLite3を使用
import hashlib  # パスワードのハッシュ化に使用

# ページの基本設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# パスワードをハッシュ化する関数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# データベースの初期化
def init_db():
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    # ユーザ情報を保存するテーブルの作成
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ユーザ登録の処理
def register_user(username, password):
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cur.execute("INSERT INTO USERS (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("このユーザ名は既に登録されています。別の名前をお試しください。")
    finally:
        conn.close()

# ログイン認証の処理
def authenticate_user(username, password):
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    hashed_password = hash_password(password)
    cur.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, hashed_password))
    user = cur.fetchone()
    conn.close()
    return user

# データベース初期化
init_db()

# ログイン状態をセッションで管理
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ログイン機能
if not st.session_state["logged_in"]:
    st.markdown("<h3>ログイン</h3>", unsafe_allow_html=True)

    # ログインフォーム
    username = st.text_input("ユーザ名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        user = authenticate_user(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"ようこそ、{username}さん！")
        else:
            st.error("ユーザ名またはパスワードが間違っています。")

    # ユーザ登録フォーム
    st.markdown("<h4>新規登録</h4>", unsafe_allow_html=True)
    new_username = st.text_input("新規ユーザ名")
    new_password = st.text_input("新規パスワード", type="password")
    if st.button("登録"):
        if new_username and new_password:
            register_user(new_username, new_password)
            st.success("登録に成功しました！ログインしてください。")
        else:
            st.error("ユーザ名とパスワードを入力してください。")

# ログイン後の処理
if st.session_state["logged_in"]:
    st.markdown(f"<h3>こんにちは、{st.session_state['username']}さん！</h3>", unsafe_allow_html=True)
    st.markdown("<h4>読書の対話相手を選んでください</h4>", unsafe_allow_html=True)
    bot_options = ["夏目漱石", "太宰治", "芥川龍之介"]
    selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")

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
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                # ページ遷移
                url = f"https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/akutagawa_bot?title={selected_title}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        else:
            st.write("作品リストを取得できませんでした。データベースを確認してください。")

    elif selected_bot in ["夏目漱石", "太宰治"]:
        st.write(f"{selected_bot}との対話を開始する準備が整いました。")
        if st.button("会話を始める", key="start_conversation_others"):
            st.write(f"{selected_bot}との対話画面に遷移します。")

    # ログアウト機能
    if st.button("ログアウト"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.experimental_rerun()
