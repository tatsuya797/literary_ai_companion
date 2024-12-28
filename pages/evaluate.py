import streamlit as st
import sqlite3
import pandas as pd
import openai
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from matplotlib.patches import Polygon
from matplotlib.colors import to_rgba

# ページの基本設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",  # サイドバーを非表示
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)
# GitHubのリポジトリにある背景画像のURL
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image4.jpg"

# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");  /* 和風な背景画像 */
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# GPT-APIキーを設定
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

def evaluate_creativity(summary):
    """GPT-APIを使用して創造性評価を行い、スコアを返す"""
    prompt = f"""
    Evaluate the following summary based on the following criteria and give a score (0-10) for each:
    1. Relevance
    2. Creativity
    3. Flexibility
    4. Problem-Solving
    5. Insight
    Summary: "{summary}"
    Provide the scores in JSON format as:
    {{"Relevance": 0, "Creativity": 0, "Flexibility": 0, "Problem_Solving": 0, "Insight": 0}}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an evaluation assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Use json.loads to safely parse JSON response
        scores = json.loads(response['choices'][0]['message']['content'])
        # Ensure all scores are integers
        for key in scores:
            scores[key] = int(scores[key])
        return scores
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        st.error(f"Error parsing GPT response: {e}")
        return None

def update_user_scores(conversation_id, scores):
    """USERテーブルに評価スコアを更新する"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE USER
        SET Relevance = ?, Creativity = ?, Flexibility = ?, Problem_Solving = ?, Insight = ?
        WHERE id = ?
        """,
        (scores["Relevance"], scores["Creativity"], scores["Flexibility"], scores["Problem_Solving"], scores["Insight"], conversation_id)
    )

    conn.commit()
    conn.close()

def plot_radar_chart(scores):
    """レーダーチャートを古風な感じで作成して描画する"""
    labels = list(scores.keys())
    values = list(scores.values())

    # レーダーチャート用にデータを閉じる
    values += values[:1]  # 閉じるために最初の値を追加
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # 閉じるために最初の角度を追加

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})

    # 古風な色合い
    fill_color = to_rgba("#b08968", alpha=0.5)
    edge_color = "#805d3a"
    bg_color = "#fff5e6"

    ax.set_facecolor(bg_color)
    ax.fill(angles, values, color=fill_color, linewidth=2, edgecolor=edge_color)
    ax.plot(angles, values, color=edge_color, linewidth=2)

    # メモリラベルを和風のフォント風に
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["二", "四", "六", "八", "十"], fontsize=12, color=edge_color)

    ax.set_xticks(angles[:-1])  # 最後の角度はラベル付けしない
    ax.set_xticklabels(labels, fontsize=12, color=edge_color)

    # 外枠のデザインを変更
    for spine in ax.spines.values():
        spine.set_edgecolor(edge_color)

    # 多角形の外枠を追加して、古風な感じに
    polygon = Polygon(
        np.c_[np.cos(angles) * 10, np.sin(angles) * 10],
        closed=True, edgecolor=edge_color, facecolor="none", linewidth=2
    )
    ax.add_patch(polygon)

    st.pyplot(fig)

def show_db_contents():
    """USERテーブルの全レコードをSELECTして表示"""
    db_file = "literary_app.db"
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("SELECT * FROM USER")
    rows = cur.fetchall()
    column_names = [description[0] for description in cur.description]
    conn.close()

    st.write("### USERテーブル内容（全カラム表示）")
    df = pd.DataFrame(rows, columns=column_names)
    st.dataframe(df)

def main():
    st.title("Evaluation & DB確認ツール")

    st.subheader("Evaluation Page")
    query_params = st.experimental_get_query_params()
    conversation_id = query_params.get("id", [None])[0]

    if conversation_id:
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT summary, Relevance, Creativity, Flexibility, Problem_Solving, Insight FROM USER WHERE id = ?", (conversation_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            summary_text = row[0]
            st.write(f"**対象レコードID**: {conversation_id}")
            st.subheader("【サマリー】")
            st.text_area("Summary", summary_text, height=150)

            if st.button("創造性評価を実行"):
                scores = evaluate_creativity(summary_text)
                if scores:
                    update_user_scores(conversation_id, scores)

                    st.success("創造性評価が完了し、スコアがデータベースに保存されました！")
                    st.write("**更新されたスコア**")
                    updated_scores_df = pd.DataFrame([scores], index=["Updated Scores"])
                    st.write(updated_scores_df)

                    st.subheader("【レーダーチャート】")
                    plot_radar_chart(scores)
            else:
                st.write("**現在のスコア**")
                current_scores = {
                    "Relevance": row[1],
                    "Creativity": row[2],
                    "Flexibility": row[3],
                    "Problem_Solving": row[4],
                    "Insight": row[5]
                }
                
                # USERテーブルの5つのスコアをDataFrameとして表示
                st.write(pd.DataFrame([current_scores], index=["Current Scores"]))

                st.subheader("【レーダーチャート】")
                plot_radar_chart(current_scores)
        else:
            st.write("該当するレコードが見つかりません。")
    else:
        st.write("IDが指定されていません。クエリパラメータ ?id=○○ を付与してください。")

    st.write("---")

    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
