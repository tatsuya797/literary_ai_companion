import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai
import os
from pathlib import Path
import zipfile
import chardet  # エンコーディング自動検出ライブラリ
from aozora_preprocess import save_cleanse_text  # 前処理の関数をインポート

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
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image2.jpg"

# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");  /* 和風な背景画像 */
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

# ZIPファイルを解凍してテキストデータを読み込む関数
@st.cache_data
def load_all_texts_from_zip(zip_file):
    all_texts = ""
    unzip_dir = Path("unzipped_files")
    unzip_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)  # 解凍先のディレクトリ

    text_files = list(unzip_dir.glob('**/*.txt'))
    for file_path in text_files:
        # まずバイト形式でファイルを読み込み、エンコーディングを検出
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']  # 検出されたエンコーディングを取得

        try:
            with open(file_path, "r", encoding=encoding) as f:
                all_texts += f.read() + "\n"
        except UnicodeDecodeError:
            st.warning(f"ファイル {file_path} の読み込みに失敗しました。")

    return all_texts

# テキストデータを処理する関数
def process_text_files():
    processed_texts = []  # 処理後のテキストを格納するリスト
    unzip_dir = Path("unzipped_files")
    text_files = list(unzip_dir.glob('**/*.txt'))  # サブフォルダも含む

    for text_file in text_files:
        cleaned_df = save_cleanse_text(text_file, unzip_dir)  # 前処理関数を呼び出し
        if cleaned_df is not None:
            # 整形後のテキストをリストに追加
            processed_texts.append(cleaned_df.to_string(index=False))

    return processed_texts

# すべてのZIPファイルを指定したディレクトリから読み込む
zip_files_directory = Path(f"{author_id}/files")
zip_files = list(zip_files_directory.glob('*.zip'))  # ZIPファイルを取得

# 全テキストデータを読み込む（すべてのZIPファイルに対して処理を行う）
all_processed_texts = []
for zip_file_path in zip_files:
    load_all_texts_from_zip(zip_file_path)  # ZIPファイルの読み込み
    processed_texts = process_text_files()  # テキストの処理
    all_processed_texts.clear()
    all_processed_texts.extend(processed_texts)  # すべての処理されたテキストを追加

# 整形後のテキストを表示
st.text_area("整形後のテキストデータ", "\n\n".join(all_processed_texts), height=300)

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting} 
    ]
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0  # 合計文字数を初期化

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    # 入力文字数をカウント
    st.session_state["total_characters"] += len(user_message["content"])

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄をクリア

# ユーザーインターフェイス
st.title(author_name + "チャットボット")
st.write(author_name + "の作品に基づいたチャットボットです。")

# 対話終了ボタンの表示
if st.session_state["total_characters"] >= 10:
    if st.button("対話終了"):
        st.write("対話を終了しました。")
        # 必要に応じて処理を追加

# メッセージ入力欄
user_input = st.text_area(
    "メッセージを入力してください（改行可能）。",
    key="user_input",
    height=100,
    on_change=communicate
)

# 対話履歴を表示（最新のメッセージを上に）
if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    # 最新のメッセージが上に来るように逆順にループ
    for message in reversed(messages[1:]):  # システムメッセージをスキップ
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class="user-message">
                    <span class="icon">😊</span>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"""
                <div class="bot-message">
                    <div class="bot-content">{message["content"]}</div>
                    <span class="icon">🤖</span>
                </div>
                """,
                unsafe_allow_html=True,
            )




# 整形後のテキストを表示
processed_texts = process_text_files()
for i, text in enumerate(processed_texts):
    st.text_area(f"整形後のテキスト {i+1}", text, height=300)


# 評価データ
criteria = ["独創性", "柔軟性", "関連性", "問題解決能力", "洞察力"]
scores = [15, 17, 18, 16, 18]

# レーダーチャートを描画する関数
def plot_radar_chart(criteria, scores):
    num_vars = len(criteria)

    # 角度を計算
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    scores += scores[:1]  # スコアを閉じるために最初の値を再度追加
    angles += angles[:1]  # グラフを閉じるための角度

    # プロット
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, scores, color='blue', alpha=0.25)
    ax.plot(angles, scores, color='blue', linewidth=2)
    ax.set_yticks(range(0, 21, 5))  # メモリを設定
    ax.set_yticklabels(map(str, range(0, 21, 5)), fontsize=10, color="gray")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, fontsize=12, color="black")
    ax.set_title("創造性ポイント", fontsize=16, fontweight="bold")

    return fig

# レーダーチャートを作成
st.title("創造性評価の結果")
st.write("以下のレーダーチャートは、あなたの創造性の評価結果を示しています。")

fig = plot_radar_chart(criteria, scores)

# Streamlit 上に表示
st.pyplot(fig)
