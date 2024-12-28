import streamlit as st
import sqlite3
import pandas as pd
import openai
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from matplotlib.patches import FancyBboxPatch

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
    {{"Relevance": 0, "Creativity": 0, "Flexibility": 0, "Problem-Solving": 0, "Insight": 0}}
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
    """さらに装飾された古風なデザインのレーダーチャートを作成して描画する"""
    labels = list(scores.keys())
    values = list(scores.values())

    # レーダーチャート用にデータを閉じる
    values += values[:1]  # 閉じるために最初の値を追加
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # 閉じるために最初の角度を追加

    # 和風の配色
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    fig.patch.set_facecolor("#fff5e1")  # 背景を和風の色に設定

    # レーダーチャートのエリア塗りつぶし
    ax.fill(angles, values, color="gold", alpha=0.4, linewidth=1.5, linestyle="--")
    ax.plot(angles, values, color="#8b0000", linewidth=2, marker="o", markersize=10, markerfacecolor="crimson")
    ax.set_facecolor("#f8e8d8")  # 内側背景を淡い和風の色に設定

    # ラベルと目盛りの設定
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=12, fontweight="bold", color="#6b4226")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=14, fontweight="bold", color="#8b4513")

    # 装飾用の枠線
    for spine in ax.spines.values():
        spine.set_edgecolor("#8b4513")
        spine.set_linewidth(2)

    # 中央から広がる線のスタイル
    for line in ax.yaxis.get_gridlines():
        line.set_linestyle("dashed")
        line.set_color("#d2b48c")

    # 和風装飾：枠を追加
    bbox = FancyBboxPatch((-1.1, -1.1), 2.2, 2.2,
                          boxstyle="round,pad=0.1",
                          edgecolor="#8b4513",
                          facecolor="none",
                          linewidth=3,
                          transform=ax.transAxes, clip_on=False)
    ax.add_patch(bbox)

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
