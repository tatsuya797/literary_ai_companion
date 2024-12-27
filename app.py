import streamlit as st
import sqlite3  # SQLite3を使用
import hashlib
import boto3
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


def register_user(username, password):
    """新規ユーザを登録"""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO USER (username, password) VALUES (?, ?)", (username, hash_password(password)))
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
    cur.execute("SELECT * FROM USER WHERE username = ? AND password = ?", (username, hash_password(password)))
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


# ユーティリティ関数
def hash_password(password):
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
                url = f"https://example.com/akutagawa_bot?title={selected_title}"
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

# 終了時にS3へアップロード
if st.button("データを保存して終了"):
    upload_db_to_s3()

