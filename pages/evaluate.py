import streamlit as st
import sqlite3
import pandas as pd
import openai
import matplotlib.pyplot as plt
import numpy as np
import json
import os


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
    """GPT-APIを使用して創造性評価を行い、スコアと説明を返す"""
    prompt = f"""
    You are an expert evaluator specializing in assessing creativity and cognitive performance.
    Evaluate the following summary based on the criteria below. Provide a score (0-10) for each, and include a brief explanation for each score to justify your assessment.

    ### Criteria:
    1. **Relevance**: How well does the summary align with the core idea or purpose it is meant to convey?
    2. **Creativity**: To what extent does the summary demonstrate original or innovative thinking?
    3. **Flexibility**: Does the summary show adaptability or the ability to approach the subject matter from multiple perspectives?
    4. **Problem-Solving**: How effectively does the summary address challenges or provide solutions within the context it describes?
    5. **Insight**: Does the summary reflect deep understanding, analysis, or unique perspectives about the topic?

    ### Summary to Evaluate:
    "{summary}"

    ### Instructions:
    - Assign a score from 0 (poor) to 10 (excellent) for each criterion.
    - Provide scores in JSON format and include brief explanations for each criterion to clarify the rationale behind your evaluation.

    ### Output Format:
    {{
      "Relevance": {{ "score": 0, "explanation": "..." }},
      "Creativity": {{ "score": 0, "explanation": "..." }},
      "Flexibility": {{ "score": 0, "explanation": "..." }},
      "Problem_Solving": {{ "score": 0, "explanation": "..." }},
      "Insight": {{ "score": 0, "explanation": "..." }}
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an evaluation assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # JSONレスポンスを解析
        scores = json.loads(response['choices'][0]['message']['content'])
        return scores  # スコアと説明が含まれるJSON
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        st.error(f"Error parsing GPT response: {e}")
        return None

def display_scores_and_explanations(scores):
    """スコアと説明をStreamlit画面に表示"""
    st.subheader("【評価結果】")
    results = []
    for key, value in scores.items():
        score = value['score']
        explanation = value['explanation']
        results.append({"Criteria": key, "Score": score, "Explanation": explanation})

    # DataFrameとして結果を表示
    df_results = pd.DataFrame(results)
    st.write(df_results)

def plot_radar_chart(scores):
    """レーダーチャート描画（スコアのみを使用）"""
    labels = [key for key in scores.keys()]
    values = [value['score'] for value in scores.values()]

    # レーダーチャート用にデータを閉じる
    values += values[:1]  # 最初の値を追加して閉じる
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # 和風配色
    colors = ["#8b4513", "#556b2f", "#2e8b57", "#6a5acd", "#cd5c5c"]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    fig.patch.set_facecolor("#fff5e1")  # 背景色

    ax.fill(angles, values, color="gold", alpha=0.3, linewidth=2, linestyle="--")
    ax.plot(angles, values, color="#8b0000", linewidth=3)
    ax.set_facecolor("#fff5e1")  # レーダーチャートの背景色

    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=12, fontweight="bold", color="#6b4226")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=14, fontweight="bold", color="#8b4513")

    st.pyplot(fig)

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
            st.markdown(
                f"""<div class="text-box">{summary_text}</div>""",
                unsafe_allow_html=True
            )

            if st.button("創造性評価を実行"):
                scores = evaluate_creativity(summary_text)
                if scores:
                    update_user_scores(conversation_id, {key: value['score'] for key, value in scores.items()})

                    st.success("創造性評価が完了し、スコアと説明がデータベースに保存されました！")

                    # スコアと説明を表示
                    display_scores_and_explanations(scores)

                    st.subheader("【レーダーチャート】")
                    plot_radar_chart(scores)
            else:
                st.write("評価を実行してください。")
        else:
            st.error("該当するレコードが見つかりません。")
    else:
        st.error("IDが指定されていません。クエリパラメータ ?id=○○ を付与してください。")

    st.write("---")

    st.subheader("DB確認ツール")
    if st.button("DBの内容を表示"):
        show_db_contents()

if __name__ == "__main__":
    main()
