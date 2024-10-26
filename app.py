import streamlit as st
import openai
from pathlib import Path
import zipfile
import chardet
from aozora_preprocess import save_cleanse_text

author_name = '芥川龍之介'

# ZIPファイルを解凍してテキストデータを読み込む関数
def load_all_texts_from_zip(zip_file):
    all_texts = ""
    unzip_dir = Path("unzipped_files")
    unzip_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)

    text_files = list(unzip_dir.glob('**/*.txt'))
    for file_path in text_files:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        try:
            with open(file_path, "r", encoding=encoding) as f:
                all_texts += f.read() + "\n"
        except UnicodeDecodeError:
            st.warning(f"ファイル {file_path} の読み込みに失敗しました。")

    return all_texts

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

# 全テキストデータを読み込む
zip_files_directory = Path("000879/files")
zip_files = list(zip_files_directory.glob('*.zip'))
all_processed_texts = []
for zip_file_path in zip_files:
    load_all_texts_from_zip(zip_file_path)
all_processed_texts = process_text_files()

# 整形後のテキストを表示
st.text_area("整形後のテキストデータ", "\n\n".join(all_processed_texts), height=300)
