import pandas as pd
from pathlib import Path
import zipfile

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

write_title = True  # 2カラム目に作品名を入れるか
write_header = True  # 1行目をカラム名にするか（カラム名「text」「title」）
save_utf8_org = True  # 元データをUTF-8にしたテキストファイルを保存するか

out_dir = Path(f'./out_{author_id}/')  # ファイル出力先
tx_org_dir = Path(out_dir / './org/')  # 元テキストのUTF-8変換ファイルの保存先
tx_edit_dir = Path(out_dir / './edit/')  # テキスト整形後のファイル保存先


def text_cleanse_df(df):
    head_tx = list(df[df['text'].str.contains(
        '-------------------------------------------------------')].index)
    atx = list(df[df['text'].str.contains('底本：')].index)
    if head_tx == []:
        head_tx = list(df[df['text'].str.contains(author_name)].index)
        head_tx_num = head_tx[0] + 1
    else:
        head_tx_num = head_tx[1] + 1
    df_e = df[head_tx_num:atx[0]]

    df_e = df_e.replace({'text': {'《.*?》': ''}}, regex=True)
    df_e = df_e.replace({'text': {'［.*?］': ''}}, regex=True)
    df_e = df_e.replace({'text': {'｜': ''}}, regex=True)

    df_e = df_e.replace({'text': {'　': ''}}, regex=True)

    df_e = df_e.replace({'text': {'^.$': ''}}, regex=True)
    df_e = df_e.replace({'text': {'^―――.*$': ''}}, regex=True)
    df_e = df_e.replace({'text': {'^＊＊＊.*$': ''}}, regex=True)
    df_e = df_e.replace({'text': {'^×××.*$': ''}}, regex=True)

    df_e = df_e.replace({'text': {'―': ''}}, regex=True)
    df_e = df_e.replace({'text': {'…': ''}}, regex=True)
    df_e = df_e.replace({'text': {'※': ''}}, regex=True)
    df_e = df_e.replace({'text': {'「」': ''}}, regex=True)

    df_e['length'] = df_e['text'].map(lambda x: len(x))
    df_e = df_e[df_e['length'] > 1]

    df_e = df_e.reset_index().drop(['index'], axis=1)
    df_e = df_e[~(df_e['text'] == '')]

    df_e = df_e.reset_index().drop(['index', 'length'], axis=1)
    return df_e


def save_cleanse_text(target_file, zip_extract_dir):
    try:
        print(target_file)
        df_tmp = pd.read_csv(target_file, encoding='cp932', names=['text'])
        if save_utf8_org:
            out_org_file_nm = Path(target_file.stem + '_org_utf-8.tsv')
            df_tmp.to_csv(Path(zip_extract_dir / out_org_file_nm), sep='\t',
                          encoding='utf-8', index=None)
        df_tmp_e = text_cleanse_df(df_tmp)
        if write_title:
            df_tmp_e['title'] = df_tmp['text'][0]
        out_edit_file_nm = Path(target_file.stem + '_clns_utf-8.txt')
        df_tmp_e.to_csv(Path(zip_extract_dir / out_edit_file_nm), sep='\t',
                        encoding='utf-8', index=None)
        return df_tmp_e

    except Exception as e:
        print(e)
        return None
