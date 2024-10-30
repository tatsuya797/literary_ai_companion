import streamlit as st
import openai
from pathlib import Path
import zipfile
import chardet  # エンコーディング自動検出ライブラリ
from aozora_preprocess import save_cleanse_text  # 前処理の関数をインポート

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 作家名

# ZIPファイルのパスと解凍先の指定
zip_files_directory = Path("000879/files")
unzip_dir = Path("unzipped_files")  # 解凍先ディレクトリ
unzip_dir.mkdir(exist_ok=True, parents=True)  # ディレクトリを作成

# 解凍したテキストファイルを再帰的に探し、ファイル一覧を取得する関数
def get_text_files():
    return list(unzip_dir.glob("**/*.txt"))  # サブディレクトリも含む

# ZIPファイルを解凍する関数
def extract_zip_files():
    zip_files = list(zip_files_directory.glob("*.zip"))
    if not zip_files:
        st.warning("ZIPファイルが見つかりません。")
        return

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(unzip_dir)  # 解凍先ディレクトリ

# テキストファイルを読み込む関数
def load_text(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)  # エンコーディングを検出
        encoding = result['encoding']

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        st.warning(f"ファイル {file_path} の読み込みに失敗しました。")
        return ""

# テキストファイルを処理する関数
def process_text_files():
    processed_texts = []
    text_files = get_text_files()

    if not text_files:
        st.warning("解凍後のテキストファイルが見つかりませんでした。")
        return []

    for text_file in text_files:
        cleaned_df = save_cleanse_text(text_file, unzip_dir)
        if cleaned_df is not None:
            processed_texts.append(cleaned_df.to_string(index=False))

    return processed_texts

# メインの実行フロー
extract_zip_files()  # ZIPファイルを解凍

all_texts = ""  # 全テキストを格納
for text_file in get_text_files():
    all_texts += load_text(text_file) + "\n"

# テキストデータを表示
if all_texts:
    st.text_area("解凍されたテキストデータ", all_texts, height=300)
else:
    st.warning("テキストデータが見つかりませんでした。")

# 整形後のテキストデータを処理・表示
processed_texts = process_text_files()
if processed_texts:
    for i, text in enumerate(processed_texts):
        st.text_area(f"整形後のテキスト {i+1}", text, height=300)
else:
    st.warning("整形後のテキストデータがありません。")

# チャットボット設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": f"{author_name} チャットボットへようこそ！"}
    ]

def communicate():
    messages = st.session_state["messages"]
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages)
    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)
    st.session_state["user_input"] = ""

# チャットボットのUI
st.title(f"{author_name} チャットボット")
st.text_input("メッセージを入力してください", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    for message in reversed(st.session_state["messages"][1:]):
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(f"{speaker}: {message['content']}")
