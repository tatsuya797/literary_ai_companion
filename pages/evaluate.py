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

    # ========== クエリパラメータ username をもとにレコードを表示 ========== #
    st.subheader("Evaluation Page")
    query_params = st.experimental_get_query_params()
    current_username = query_params.get("username", [None])[0]  # usernameパラメータ取得
    
    if current_username:
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        # 該当usernameのconversation, summaryを取得
        cur.execute("SELECT conversation, summary FROM USER WHERE username = ?", (current_username,))
        row = cur.fetchone()

        if row:
            conversation_json, summary_text = row  # タプルを展開
            st.write(f"**対象ユーザー名**: {current_username}")

            st.subheader("【会話履歴】")
            # 既存データを初期値にセットしてテキストエリア表示
            updated_conversation = st.text_area("Conversation", conversation_json, height=250)

            st.subheader("【サマリー】")
            # 既存データを初期値にセットしてテキストエリア表示
            updated_summary = st.text_area("Summary", summary_text, height=150)

            # 更新ボタンを押したときにUPDATE文を実行
            if st.button("Update"):
                cur.execute("""
                    UPDATE USER
                    SET conversation = ?, summary = ?
                    WHERE username = ?
                """, (updated_conversation, updated_summary, current_username))
                conn.commit()
                st.success("レコードが更新されました。")
        else:
            st.write("該当するユーザー名が見つかりません。")

        conn.close()
    else:
        st.write("username が指定されていません。クエリパラメータ ?username=○○ を付与してください。")

    st.write("---")


    # ========== ②の機能: ボタン押下でDBの全レコードを一覧表示 ========== #
    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
