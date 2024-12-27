import streamlit as st
import sqlite3
import boto3
import hashlib
import os

# AWS S3 の設定
BUCKET_NAME = "my-s3-bucket"
DB_FILENAME = "literary_app.db"         # S3上のファイル名
LOCAL_DB_PATH = "local_literary_app.db" # ローカルで操作する一時的なファイル名

# AWS S3 クライアントの初期化
s3 = boto3.client("s3", region_name="ap-northeast-1")  # リージョンは適宜変更

# ページの基本設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

# GitHubのリポジトリにある背景画像のURL
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image1.jpg"

# 背景画像の設定
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# === S3関連のユーティリティ関数 ===
def download_db_from_s3():
    """S3からSQLiteファイルをダウンロード"""
    try:
        s3.download_file(BUCKET_NAME, DB_FILENAME, LOCAL_DB_PATH)
        st.write("DBファイルをS3からダウンロードしました。")
    except Exception as e:
        st.error(f"DBファイルのダウンロードに失敗しました: {e}")


def upload_db_to_s3():
    """SQLiteファイルをS3にアップロード"""
    try:
        s3.upload_file(LOCAL_DB_PATH, BUCKET_NAME, DB_FILENAME)
        st.write("DBファイルをS3にアップロードしました。")
    except Exception as e:
        st.error(f"DBファイルのアップロードに失敗しました: {e}")


# === SQLite操作関連の関数 ===
def init_db():
    """ローカルのSQLiteファイルでDBを初期化"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
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
    """新規ユーザを登録"""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO USERS (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        st.success("登録に成功しました！ログインしてください。")
    except sqlite3.IntegrityError:
        st.error("このユーザ名は既に登録されています。")
    finally:
        conn.close()


def authenticate_user(username, password):
    """ユーザを認証"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM USERS WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = cur.fetchone()
    conn.close()
    return user


def fetch_titles_from_db():
    """BOTテーブルからタイトルを取得"""
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title FROM BOT")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def hash_password(password):
    """パスワードをハッシュ化"""
    return hashlib.sha256(password.encode()).hexdigest()


# === アプリ起動時にDBを準備 ===
# S3からダウンロード → SQLite初期化
if not os.path.exists(LOCAL_DB_PATH):
    download_db_from_s3()
init_db()

# === アプリケーションの実装 ===
# セッション状態管理
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ログイン・新規登録をタブで切り替え
tabs = st.tabs(["ログイン", "新規登録"])

# ログインフォーム
with tabs[0]:
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

# 新規登録フォーム
with tabs[1]:
    st.markdown("<h3>新規登録</h3>", unsafe_allow_html=True)
    new_username = st.text_input("新規ユーザ名")
    new_password = st.text_input("新規パスワード", type="password")
    if st.button("登録"):
        if new_username and new_password:
            register_user(new_username, new_password)
        else:
            st.error("ユーザ名とパスワードを入力してください。")

# ログイン後の画面
if st.session_state["logged_in"]:
    st.markdown(f"<h3>こんにちは、{st.session_state['username']}さん！</h3>", unsafe_allow_html=True)
    # ボット選択と開始ボタン
    bot_options = ["夏目漱石", "太宰治", "芥川龍之介"]
    selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")
    if selected_bot == "芥川龍之介":
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                upload_db_to_s3()
                url = f"https://example.com/akutagawa_bot?title={selected_title}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

