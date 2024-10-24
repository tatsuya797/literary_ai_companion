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
    all_processed_texts = ""  # 処理後のテキストデータを保存する変数
    unzip_dir = Path("unzipped_files")
    text_files = list(unzip_dir.glob('**/*.txt'))  # サブフォルダも含む
    
    for text_file in text_files:
        st.write(f"Processing file: {text_file}")  # デバッグ: 処理中のファイル名を表示
        save_cleanse_text(text_file)  # 前処理関数を呼び出し
        # 前処理後のファイルパスを取得
        processed_file = Path('unzipped_files/out_edit/') / f"{text_file.stem}_clns_utf-8.txt"
        if processed_file.exists():
            processed_texts.append(processed_file)
            # 整形後のテキストを読み込み、変数に追加
            with open(processed_file, "r", encoding="utf-8") as f:
                content = f.read()
                all_processed_texts += content + "\n"  # 処理後のテキストを変数に追加
                # デバッグ用に整形後のテキスト内容を一時的に表示
                st.text_area(f"整形後のテキスト: {processed_file.name}", content, height=200)
        else:
            st.warning(f"処理後のファイル {processed_file} が存在しません。")
            st.write(f"Error processing file: {text_file}")

    return all_processed_texts, processed_texts

# すべてのZIPファイルを指定したディレクトリから読み込む
zip_files_directory = Path("000879/files")
zip_files = list(zip_files_directory.glob('*.zip'))  # ZIPファイルを取得

# 全テキストデータを読み込む（すべてのZIPファイルに対して処理を行う）
all_akutagawa_ryunosuke_texts = ""
for zip_file_path in zip_files:
    st.write(f"Loading ZIP file: {zip_file_path}")  # デバッグ: ZIPファイル読み込み中の表示
    all_akutagawa_ryunosuke_texts += load_all_texts_from_zip(zip_file_path) + "\n"

st.text_area("ZIPファイルからのテキストデータ", all_akutagawa_ryunosuke_texts, height=300)

# テキストファイルを処理するボタン
if st.button("テキストファイルを処理する"):
    with st.spinner("テキストファイルを処理中..."):
        all_processed_texts, processed_files = process_text_files()  # テキストファイルの処理を実行
    st.success("テキストファイルの処理が完了しました。")
    
    # 処理後のテキストを表示
    st.subheader("処理後のテキスト内容")
    st.text_area("整形後の全テキストデータ", all_processed_texts, height=300)  # 全処理後のテキストを表示

    for processed_file in processed_files:
        try:
            with open(processed_file, "r", encoding="utf-8") as f:
                content = f.read()
                st.text_area(f"{processed_file.name}", content, height=200)
        except Exception as e:
            st.warning(f"ファイル {processed_file} の読み込みに失敗しました。")
