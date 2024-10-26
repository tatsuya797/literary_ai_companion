import streamlit as st
import openai
import os
from pathlib import Path
import zipfile
import requests
import chardet  # エンコーディング自動検出ライブラリ
from aozora_preprocess import save_cleanse_text  # 前処理の関数をインポート

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名
github_url = "https://github.com/tatsuya797/openai_api_bot_akutagawa/blob/main/000879.zip?raw=true"

# GitHubからZIPファイルをダウンロードして解凍する関数
def download_and_extract_zip():
    zip_file_path = Path("000879.zip")
    unzip_dir = Path("unzipped_files")

    # 古いファイルやディレクトリがある場合は削除してから再取得
    if zip_file_path.exists():
        zip_file_path.unlink()
    if unzip_dir.exists():
        for file in unzip_dir.glob("*"):
            file.unlink()

    # ZIPファイルをダウンロード
    response = requests.get(github_url)
    with open(zip_file_path, "wb") as f:
        f.write(response.content)

    # ZIPファイルを解凍
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)

    return unzip_dir

# テキストデータを読み込む関数
@st.cache_data
def load_all_texts_from_extracted_dir(extracted_dir):
    all_texts = ""
    text_files = list(extracted_dir.glob('**/*.txt'))

    for file_path in text_files:
        # ファイルをバイトで読み込み、エンコーディングを検出
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']  # 検出されたエンコーディング

        # テキストを読み込む
        try:
            with open(file_path, "r", encoding=encoding) as f:
                all_texts += f.read() + "\n"
        except UnicodeDecodeError:
            st.warning(f"ファイル {file_path} の読み込みに失敗しました。")

    return all_texts

# テキストファイルを処理する関数
def process_text_files():
    processed_texts = []
    extracted_dir = download_and_extract_zip()
    text_files = list(extracted_dir.glob('**/*.txt'))

    for text_file in text_files:
        cleaned_df = save_cleanse_text(text_file, extracted_dir)
        if cleaned_df is not None:
            processed_texts.append(cleaned_df.to_string(index=False))

    return processed_texts

# 整形後のテキストを表示
st.title(author_name + "チャットボット")
st.write(author_name + "の作品に基づいたチャットボットです。")

all_texts = load_all_texts_from_extracted_dir(download_and_extract_zip())
st.text_area("テキストデータ", all_texts, height=300)
