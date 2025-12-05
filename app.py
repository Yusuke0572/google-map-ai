import streamlit as st
import google.generativeai as genai
import os

# --- UI設定 ---
st.set_page_config(page_title="口コミ返信AI", page_icon="💬")
st.title("💬 Google Map 口コミ自動返信生成 AI")
st.markdown("丁寧さとMEO対策を兼ね備えた返信を生成します。")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("設定")
    
    # Secretsから安全にキーを読み込む
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        st.error("APIキーが設定されていません。")
        api_key = None

    st.markdown("---")
    st.write("開発者が利用料を負担していますので、無料で使い放題です。")

# --- 入力エリア ---
col1, col2 = st.columns(2)
with col1:
    store_name = st.text_input("店舗名", placeholder="例：〇〇屋")
    tone = st.selectbox("返信トーン", ["丁寧・フォーマル", "親しみやすい", "簡潔・ビジネス"])

with col2:
    rating = st.slider("評価 (星の数)", 1, 5, 5)

review_text = st.text_area("お客様の口コミ内容", height=150, placeholder="ここに口コミをコピペしてください。")

# --- 生成ボタンとロジック ---
if st.button("返信を生成する", type="primary"):
    if not api_key:
        st.error("⚠️ 左のサイドバーにGemini APIキーを入力してください。")
    elif not review_text:
        st.warning("⚠️ 口コミ内容が入力されていません。")
    else:
        try:
            # Geminiの設定
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            # プロンプト設計（ここが品質の肝）
            system_instruction = """
            あなたは「熟練の店舗マネージャー」兼「MEOマーケティング専門家」です。
            以下のルールでGoogleマップの口コミ返信を作成してください：
            1. 高評価には感謝、低評価には真摯な謝罪と改善提案（言い訳禁止）。
            2. 定型文感を消すため、口コミ内の「具体的な単語（商品名や状況）」を必ず引用する。
            3. MEO対策として、店舗名や地域名（例: 京都の〜）を自然に混ぜる。
            4. 150〜250文字程度。
            """
            
            user_prompt = f"""
            店舗名: {store_name}
            トーン: {tone}
            評価: 星{rating}
            口コミ内容:
            {review_text}
            """

            with st.spinner('AIが最適な返信を考案中...'):
                response = model.generate_content([system_instruction, user_prompt])
            
            st.success("生成完了")
            st.text_area("生成された返信文", value=response.text, height=250)
            st.info("💡 ヒント: 事実と異なる内容がないか確認してから投稿してください。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")