import streamlit as st
import pandas as pd
import base64
import os
import plotly.graph_objects as go

# --- [1] UI/UX 극강 처방 (상단 바/여백 완전 박멸 & 중앙 정렬) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 상단 바 및 모든 여백 물리적 제거 (가장 강력한 설정) */
    header, [data-testid="stHeader"], .st-emotion-cache-18ni7ap {
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        display: none !important;
    }
    #MainMenu, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
    
    /* 본문 위쪽 빈 공간 제거 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 550px !important;
    }

    /* 2. 전체 중앙 정렬 및 폰트 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', sans-serif; 
        color: #1e293b; 
        text-align: center !important; 
    }
    
    .stApp { 
        background-color: #ffffff; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
    }

    /* 3. 모몽이 둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 60px auto 20px auto; /* 상단 여백 확보 */
    }
    
    /* 4. 메인 카드 디자인 */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; margin: 0 auto;
        text-align: center;
    }
    
    /* 5. 버튼 및 라벨 스타일링 */
    h1 { font-size: 28px !important; font-weight: 700 !important; margin-top: 0 !important; }
    label { font-size: 16px !important; font-weight: 600 !important; text-align: left !important; display: block !important; margin-bottom: 8px !important; }
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 4em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; margin-top: 20px;
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 사운드 엔진 (JS 강제 재생) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            audio_id = "bgm" if is_bgm else "effect"
            md = f"""
                <audio id="{audio_id}" autoplay="true" {loop} style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>document.getElementById("{audio_id}").play();</script>
            """
            st.markdown(md, unsafe_allow_html=True)

# --- [3] 엑셀 데이터 로드 (어머님의 DB) ---
@st.cache_data
def load_db():
    f = "DreamNavi_Job_DB_v2_20240509.xlsx"
    return pd.read_excel(f) if os.path.exists(f) else None

df = load_db()

# --- [4] 세션 및 로직 복구 (심리분석 + 4대엔진) ---
for k in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if k not in st.session_state:
        if k == 'scores': st.session_state[k] = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0, "AI":0}
        elif k == 'step': st.session_state[k] = 0
        elif k == 'page': st.session_state[k] = 'intro'
        else: st.session_state[k] = {}

questions = [
    {"q": "기계나 로봇을 직접 조립하고 원리를 파악하는 게 즐겁니?", "type": "R"},
    {"q": "데이터 속에서 논리적인 패턴을 찾는 일이 흥미로워?", "type": "I"},
    {"q": "새로운 AI 도구를 남들보다 빠르게 써보는 걸 좋아해?", "type": "AI"},
    {"q": "친구들의 의견을 조율하고 이끄는 리더 역할이 편안해?", "type": "S"},
    {"q": "글이나 그림으로 내 생각을 창의적으로 표현하는 게 좋아?", "type": "A"},
    {"q": "정해진 규칙에 따라 꼼꼼하게 일하는 게 편안하니?", "type": "C"},
    {"q": "미래 기술이 우리 삶에 어떤 영향을 줄지 고민해봤어?", "type": "AI"},
    {"q": "낯선 곳에서도 빠르게 적응하고 문제를 해결할 수 있니?", "type": "Game"},
    {"q": "어려울 때 데이터와 직관으로 결정을 내리는 편이야?", "type": "Game"},
    {"q": "누군가를 돕거나 가르쳐줄 때 에너지가 생기니?", "type": "S"},
    {"q": "목표를 위해 끝까지 파고들어 결과를 내는 편이야?", "type": "I"},
    {"q": "새로운 걸 기획하고 사람들에게 알리는 게 설레니?", "type": "E"}
]

# --- [5] 화면 단계별 구현 (무생략) ---

# 1. 인트로
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=220)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "region": region}
            st.session_state.page = 'mind_check'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 심리 파악
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}의 속마음")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민은 뭐야?")
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 결과 페이지 (어머님 엑셀 데이터 매칭)
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 꿈 지도")
    best_type = max(st.session_state.scores, key=st.session_state.scores.get)
    if df is not None:
        matched = df[df['유형'] == best_type].iloc[0] if not df[df['유형'] == best_type].empty else df.iloc[0]
        st.success(f"추천 직업: {matched['직업명']}")
        st.info(f"💡 모몽이의 한마디: {matched['모몽이의 한마디']}")
        st.error(f"⚠️ 성장 가이드: {matched['성장 가이드']}")
    st.markdown('</div>', unsafe_allow_html=True)
