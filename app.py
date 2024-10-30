import streamlit as st
import openai
from pathlib import Path
import zipfile
import chardet
from aozora_preprocess import save_cleanse_text

author_name = '芥川龍之介'
unzip_dir = Path("unzipped_files")  # 解凍先ディレクトリ
unzip_dir.mkdir(exist_ok=True, parents=True)

# テキストデータを読み込む関数
def load_all_texts_from_zip(zip_file):
    all_texts = ""
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)

    text_files = list(unzip_dir.glob('**/*.txt'))
    for file_path in text_files:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                all_texts += f.read() + "\n"
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp932') as f:
                all_texts += f.read() + "\n"

    return all_texts

# テキスト処理関数
def process_text_files():
    processed_texts = []
    text_files = list(unzip_dir.glob('**/*.txt'))

    for text_file in text_files:
        cleaned_df = save_cleanse_text(text_file, unzip_dir)
        if cleaned_df is not None:
            processed_texts.append(cleaned_df.to_string(index=False))

    return processed_texts

# ZIPファイルの取得と処理
zip_files_directory = Path("000879/files")
zip_files = list(zip_files_directory.glob('*.zip'))

all_processed_texts = []
for zip_file_path in zip_files:
    load_all_texts_from_zip(zip_file_path)
    all_processed_texts.extend(process_text_files())

# テキスト表示
if all_processed_texts:
    for i, text in enumerate(all_processed_texts):
        st.text_area(f"整形後のテキスト {i+1}", text, height=300)
else:
    st.warning("テキストデータが見つかりませんでした。")

# チャットボットの設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": "芥川龍之介チャットボットへようこそ！"}]

def communicate():
    messages = st.session_state["messages"]
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)
    st.session_state["user_input"] = ""

st.title(f"{author_name}チャットボット")
st.text_input("メッセージを入力してください", key="user_input", on_change=communicate)

if st.session_state["messages"]:
    for message in reversed(st.session_state["messages"][1:]):
        speaker = "🙂" if message["role"] == "user" else "🤖"
        st.write(f"{speaker}: {message['content']}")
