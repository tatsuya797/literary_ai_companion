import streamlit as st
import openai
import os
from pathlib import Path
import zipfile
from text_preprocessing import save_cleanse_text  # 前処理の関数をインポート

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
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                all_texts += f.read() + "\n"
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="shift_jis") as f:
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
        save_cleanse_text(text_file)  # 前処理関数を呼び出し
        # 前処理後のファイルパスを取得
        processed_file = Path(f'unzipped_files/out_{author_id}/edit/{text_file.stem}_clns_utf-8.txt')
        if processed_file.exists():
            processed_texts.append(processed_file)
        else:
            st.warning(f"処理後のファイル {processed_file} が存在しません。")

    return processed_texts

# すべてのZIPファイルを指定したディレクトリから読み込む
zip_files_directory = Path("000879/files")
zip_files = list(zip_files_directory.glob('*.zip'))  # ZIPファイルを取得

# 全テキストデータを読み込む（すべてのZIPファイルに対して処理を行う）
all_akutagawa_ryunosuke_texts = ""
for zip_file_path in zip_files:
    all_akutagawa_ryunosuke_texts += load_all_texts_from_zip(zip_file_path) + "\n"

st.text_area("テキストデータ", all_akutagawa_ryunosuke_texts, height=300)

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

# ユーザーインターフェイス
st.title("芥川龍之介 チャットボット")
st.write("芥川龍之介の作品に基づいたチャットボットです。")

# ユーザー入力
st.text_input("メッセージを入力してください", key="user_input", on_change=communicate)

# チャット履歴を表示
messages = st.session_state.get("messages", [])
for message in messages:
    if message["role"] == "system":
      # st.write("システム: " + message["content"])
    elif message["role"] == "user":
        st.write("ユーザー: " + message["content"])
    else:
        st.write("チャットボット: " + message["content"])
