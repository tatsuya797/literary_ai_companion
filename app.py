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

    # USER テーブル作成
    cur.execute('''
        CREATE TABLE IF NOT EXISTS USER (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            author TEXT,
            title TEXT,
            conversation TEXT,
            summary TEXT,
            Relevance INTEGER,
            Creativity INTEGER,
            Flexibility INTEGER,
            Problem_Solving INTEGER,
            Insight INTEGER
        )
    ''')

    # BOT テーブル作成
    cur.execute('''
        CREATE TABLE IF NOT EXISTS BOT (
            author TEXT,
            title TEXT,
            text_content TEXT
        )
    ''')

    conn.commit()
    conn.close()

def store_author_and_title(username, author_value, title_value):
    """
    ログイン中のユーザー(username)のレコードを探して、
    authorカラムとtitleカラムをUPDATEする
    """
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE USER
        SET author = ?, title = ?
        WHERE username = ?
        """,
        (author_value, title_value, username)
    )
    conn.commit()
    conn.close()

def drop_user_table():
    """USERテーブルを削除"""
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS USER")
    conn.commit()
    conn.close()

# username から id を取得する関数
def get_user_id_by_username(username):
    """
    USERテーブルから、指定されたusernameに対応するidを取得
    """
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM USER WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# ユーザの新規登録
def register_user(username, password):
    try:
        conn = sqlite3.connect("literary_app.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO USER (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        st.success("登録に成功しました！ログインしてください。")
    except sqlite3.IntegrityError:
        st.error("このユーザ名は既に登録されています。")
    finally:
        conn.close()

# ユーザが存在するかどうかを確認（認証）
def authenticate_user(username, password):
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM USER WHERE username = ? AND password = ?", (username, hash_password(password)))
    user = cur.fetchone()
    conn.close()
    return user

def fetch_titles_from_db():
    conn = sqlite3.connect("literary_app.db")
    cur = conn.cursor()
    cur.execute("SELECT title FROM BOT WHERE author = ?", (selected_bot,))
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

# データベース初期化
init_db()

# DB削除ボタン
if st.button("DB削除"):
    drop_user_table()
    st.success("USERテーブルを削除しました。")

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
    st.markdown("<div class='bot-section'>読書の対話相手を選んでください</div>", unsafe_allow_html=True)
    bot_options = ["夏目漱石", "太宰治", "芥川龍之介", "森鴎外", "宮沢賢治"]
    selected_bot = st.selectbox("ボット選択", bot_options, key="bot_selectbox")
    st.markdown("</div>", unsafe_allow_html=True)

    # 夏目漱石ボットの選択に応じた処理
    if selected_bot == "夏目漱石":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                current_user = st.session_state["username"]  
                # USERテーブルに author=selected_bot と title=selected_title をUPDATE
                store_author_and_title(current_user, selected_bot, selected_title)

                # DBからユーザーIDを取得
                user_id = get_user_id_by_username(current_user)
                
                # ページ遷移: クエリパラメータに id, username, author, title を付与
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/"
                    "akutagawa_bot"
                    f"?id={user_id}"                # ① DB上のid
                    f"&username={current_user}"     # ② ログイン中のusername
                    f"&author={selected_bot}"      # ③ ボット（著者）
                    f"&title={selected_title}"      # ④ 選択した作品タイトル
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

    
    # 太宰治ボットの選択に応じた処理
    if selected_bot == "太宰治":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                current_user = st.session_state["username"]  
                # USERテーブルに author=selected_bot と title=selected_title をUPDATE
                store_author_and_title(current_user, selected_bot, selected_title)

                # DBからユーザーIDを取得
                user_id = get_user_id_by_username(current_user)
                
                # ページ遷移: クエリパラメータに id, username, author, title を付与
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/"
                    "akutagawa_bot"
                    f"?id={user_id}"                # ① DB上のid
                    f"&username={current_user}"     # ② ログイン中のusername
                    f"&author={selected_bot}"      # ③ ボット（著者）
                    f"&title={selected_title}"      # ④ 選択した作品タイトル
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

    
    # 芥川龍之介ボットの選択に応じた処理
    if selected_bot == "芥川龍之介":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                current_user = st.session_state["username"]  
                # USERテーブルに author=selected_bot と title=selected_title をUPDATE
                store_author_and_title(current_user, selected_bot, selected_title)

                # DBからユーザーIDを取得
                user_id = get_user_id_by_username(current_user)
                
                # ページ遷移: クエリパラメータに id, username, author, title を付与
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/"
                    "akutagawa_bot"
                    f"?id={user_id}"                # ① DB上のid
                    f"&username={current_user}"     # ② ログイン中のusername
                    f"&author={selected_bot}"      # ③ ボット（著者）
                    f"&title={selected_title}"      # ④ 選択した作品タイトル
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

    # 森鴎外ボットの選択に応じた処理
    if selected_bot == "森鴎外":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                current_user = st.session_state["username"]  
                # USERテーブルに author=selected_bot と title=selected_title をUPDATE
                store_author_and_title(current_user, selected_bot, selected_title)

                # DBからユーザーIDを取得
                user_id = get_user_id_by_username(current_user)
                
                # ページ遷移: クエリパラメータに id, username, author, title を付与
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/"
                    "akutagawa_bot"
                    f"?id={user_id}"                # ① DB上のid
                    f"&username={current_user}"     # ② ログイン中のusername
                    f"&author={selected_bot}"      # ③ ボット（著者）
                    f"&title={selected_title}"      # ④ 選択した作品タイトル
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)

    # 宮沢賢治ボットの選択に応じた処理
    if selected_bot == "宮沢賢治":
        # タイトルリストを取得
        titles = fetch_titles_from_db()
        if titles:
            selected_title = st.selectbox("対話したい作品を選んでください:", titles, key="title_selectbox")
            if st.button("会話を始める", key="start_conversation"):
                current_user = st.session_state["username"]  
                # USERテーブルに author=selected_bot と title=selected_title をUPDATE
                store_author_and_title(current_user, selected_bot, selected_title)

                # DBからユーザーIDを取得
                user_id = get_user_id_by_username(current_user)
                
                # ページ遷移: クエリパラメータに id, username, author, title を付与
                url = (
                    "https://literaryaicompanion-prg5zuxubou7vm6rxpqujs.streamlit.app/"
                    "akutagawa_bot"
                    f"?id={user_id}"                # ① DB上のid
                    f"&username={current_user}"     # ② ログイン中のusername
                    f"&author={selected_bot}"      # ③ ボット（著者）
                    f"&title={selected_title}"      # ④ 選択した作品タイトル
                )
                st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
                
