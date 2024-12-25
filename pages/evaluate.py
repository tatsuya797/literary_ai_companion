import streamlit as st
import sqlite3

def show_db_contents():
    """USERテーブルの全レコードをSELECTして表示"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    # USERテーブルの内容をすべて取得 (SELECT *)
    cur.execute("SELECT * FROM USER")
    rows = cur.fetchall()

    # 取得したカラム名をリスト化（テーブル定義の順番通り）
    column_names = [description[0] for description in cur.description]
    
    conn.close()
    
    st.write("### USERテーブル内容（全カラム表示）")

    # すべてのカラムをまとめて表示したい場合は、PandasのDataFrameにして表示すると見やすい
    import pandas as pd
    df = pd.DataFrame(rows, columns=column_names)
    st.dataframe(df)


def main():
    st.title("Evaluation & DB確認ツール")

    # ========== ①の機能: クエリパラメータ id をもとにレコードを表示 ========== #
    st.subheader("Evaluation Page")
    query_params = st.experimental_get_query_params()
    conversation_id = query_params.get("id", [None])[0]  # idパラメータ取得
    
    if conversation_id:
        # id が取得できた場合
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT * FROM USER WHERE id = ?", (conversation_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            conversation_json, summary_text = row[0], row[1]
            st.write(f"**対象レコードID**: {conversation_id}")

            st.subheader("【会話履歴】")
            st.text_area("Conversation", conversation_json, height=250)

            st.subheader("【サマリー】")
            st.text_area("Summary", summary_text, height=150)
        else:
            st.write("該当するレコードが見つかりません。")
    else:
        st.write("IDが指定されていません。クエリパラメータ ?id=○○ を付与してください。")

    st.write("---")

    # ========== ②の機能: ボタン押下でDBの全レコードを一覧表示 ========== #
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
