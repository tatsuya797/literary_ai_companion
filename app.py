import streamlit as st
import openai
import os
from pathlib import Path
import zipfile
import chardet  # エンコーディング自動検出ライブラリ
from aozora_preprocess import save_cleanse_text  # 前処理の関数をインポート

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

# ZIPファイルを解凍し、テキストデータを読み込む関数
@st.cache_data
def load_and_process_texts(zip_files_directory):
    all_processed_texts = []
    zip_files = list(zip_files_directory.glob('*.zip'))

    for zip_file_path in zip_files:
        unzip_dir = Path("unzipped_files")
        unzip_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_dir)

        text_files = list(unzip_dir.glob('**/*.txt'))
        for file_path in text_files:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']

            try:
                with open(file_path, "r", encoding=encoding) as f:
                    cleaned_df = save_cleanse_text(file_path, unzip_dir)
                    if cleaned_df is not None:
                        all_processed_texts.append(cleaned_df.to_string(index=False))
            except UnicodeDecodeError:
                st.warning(f"ファイル {file_path} の読み込みに失敗しました。")

    return all_processed_texts

# テキストを読み込み整形後のデータを表示
zip_files_directory = Path("000879/files")
all_processed_texts = load_and_process_texts(zip_files_directory)

# 整形後のテキストデータを表示
st.text_area("整形後のテキストデータ", "\n\n".join(all_processed_texts), height=300)

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
st.title(author_name+"チャットボット")
st.write(author_name+"の作品に基づいたチャットボットです。")

# ユーザーのメッセージ入力
user_input = st.text_input("メッセージを入力してください。", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    messages = st.session_state["messages"]
    for message in reversed(messages[1:]):  # 直近のメッセージを上に
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(speaker + ": " + message["content"])
