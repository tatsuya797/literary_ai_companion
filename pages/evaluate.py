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

    ### Output Format (return only JSON):
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

        # GPTのレスポンスをJSONとして解析
        scores = json.loads(response['choices'][0]['message']['content'])

        # スコアのみを抽出して整数値に変換し、辞書形式で返す
        for key, value in scores.items():
            value['score'] = int(value['score'])  # スコアを整数化

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

def translate_to_japanese(text):
    """英語の説明を日本語に翻訳"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Translate the following text into Japanese."},
                {"role": "user", "content": text}
            ]
        )
        translation = response['choices'][0]['message']['content'].strip()
        st.write(f"【翻訳結果】: {translation}")  # デバッグ用に翻訳結果を表示
        return translation
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text  # 翻訳が失敗した場合は元のテキストを返す

def display_scores_and_explanations(scores):
    """スコアと説明をStreamlit画面に表示（説明は日本語翻訳）"""
    st.subheader("【評価結果】")
    for key, value in scores.items():
        score = value['score']
        explanation = value['explanation']

        # 説明を日本語に翻訳
        translated_explanation = translate_to_japanese(explanation)

        # スコアと説明を表示
        st.markdown(f"### {key} (スコア: {score}/10)")
        st.markdown(
            f"""
            <div style="
                background-color:#f8f0e3; 
                padding:15px; 
                border-radius:10px; 
                border: 2px solid #d4af37; 
                margin-bottom:15px;
                font-size: 1.1rem;
                line-height: 1.5;
                color: #5b4636;
            ">
                {translated_explanation}
            </div>
            """,
            unsafe_allow_html=True
        )

def plot_radar_chart(scores):
    """レーダーチャートを描画（スコアのみ使用）"""
    # スコアのみを抽出
    labels = list(scores.keys())
    values = [scores[key]['score'] for key in labels]  # スコアを抽出

    # レーダーチャート用にデータを閉じる
    values += values[:1]  # 最初の値を追加して閉じる
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # 最初の角度を追加して閉じる

    # 和風の配色
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    fig.patch.set_facecolor("#fff5e1")  # 背景色

    # レーダーチャートの塗りつぶしと線の設定
    ax.fill(angles, values, color="gold", alpha=0.3, linewidth=2, linestyle="--")
    ax.plot(angles, values, color="#8b0000", linewidth=3)

    # 軸と背景色の設定
    ax.set_facecolor("#fff5e1")
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=12, fontweight="bold", color="#6b4226")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=14, fontweight="bold", color="#8b4513")

    # 装飾用の枠線
    for spine in ax.spines.values():
        spine.set_edgecolor("#8b0000")
        spine.set_linewidth(1.5)

    # 中央から広がる線のスタイル
    for line in ax.yaxis.get_gridlines():
        line.set_linestyle("dotted")
        line.set_color("#cd5c5c")

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
    st.markdown(
        """<style>
        .stApp {
            font-family: 'Yu Mincho', serif;
            background-color: #fffaf0;
            color: #5b4636;
        }
        .text-box {
            background-color: #f8f0e3;
            border: 2px solid #d4af37;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1);
            font-size: 1.2rem;
            font-family: 'Yu Mincho', serif;
            color: #5b4636;
        }
        </style>""",
        unsafe_allow_html=True
    )

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

                    # スコアと説明を表示（日本語翻訳含む）
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
    main()
