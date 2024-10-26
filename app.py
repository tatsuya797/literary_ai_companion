import streamlit as st
import openai
from pathlib import Path
import zipfile
import chardet  # エンコーディング自動検出ライブラリ
from aozora_preprocess import save_cleanse_text  # 前処理の関数をインポート

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

# ZIPファイルを解凍してテキストデータを読み込む関数
def load_all_texts_from_zip(zip_file):
    unzip_dir = Path("unzipped_files")
    unzip_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)  # 解凍先のディレクトリ

# テキストデータを処理する関数
def process_text_files():
    processed_texts = []
    unzip_dir = Path("unzipped_files")
    text_files = list(unzip_dir.glob('**/*.txt'))

    for text_file in text_files:
        cleaned_df = save_cleanse_text(text_file, unzip_dir)
        if cleaned_df is not None:
            processed_texts.append(cleaned_df.to_string(index=False))

    return processed_texts

# すべてのZIPファイルを指定したディレクトリから読み込む
zip_files_directory = Path("000879/files")
zip_files = list(zip_files_directory.glob('*.zip'))

# 全テキストデータを読み込む（すべてのZIPファイルに対して処理を行う）
all_processed_texts = []
for zip_file_path in zip_files:
    load_all_texts_from_zip(zip_file_path)  # ZIPファイルの読み込み
    processed_texts = process_text_files()  # テキストの処理
    all_processed_texts.extend(processed_texts)

# テキストデータが空でないか確認し、整形後のテキストを一つのテキストエリアにまとめて表示
if all_processed_texts:
    st.text_area("整形後のテキストデータ", "\n\n".join(all_processed_texts), height=300)
else:
    st.warning("整形後のテキストデータが表示できませんでした。データが存在するか確認してください。")

# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting} 
    ]

# チャットボットとやりとりする関数
def communicate():
    messages = st.session_state["messages"]
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    st.session_state["user_input"] = ""  # 入力欄をクリア

# ユーザーインターフェース
st.title(author_name + "チャットボット")
st.write(author_name + "の作品に基づいたチャットボットです。")

# ユーザーのメッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]
    for message in reversed(messages[1:]):
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(speaker + ": " + message["content"])
