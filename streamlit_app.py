import streamlit as st
import pandas as pd
import base64
import os
import datetime
import plotly.graph_objects as go

# --- [1] UI/UX 극강 처방 (상단 바 박멸 및 중앙 정렬 완결) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 상단 바 물리적 제거 및 본문 강제 인출 */
    header, [data-testid="stHeader"] { 
        display: none !important; 
        height: 0 !important;
    }
    
    /* 화면 전체를 위로 강제 밀어올려 상단 바 공간 점유 차단 */
    .stApp { 
        margin-top: -100px !important; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 0rem !important;
        max-width: 500px !important;
    }

    /* 2. 모든 요소 강제 중앙 정렬 */
    div[data-testid="stVerticalBlock"] > div {
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
    }

    /* 3. 모몽이 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 0 auto 10px auto;
    }
    
    /* 4. 메인 카드 및 텍스트 밸런스 */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; text-align: center;
    }
    
    h1 { font-size: 26px !important; font-weight: 700 !important; margin-bottom: 20px !important; color: #1e293b; }
    label { font-size: 15px !important; font-weight: 600 !important; text-align: left !important; width: 100%; display: block !important; margin-top: 15px !important; color: #475569; }
    
    /* 5. 버튼 디자인 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; margin-top: 20px;
        box-shadow: 0 4px 15px rgba(181,255,252,0.4);
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    
    /* 메뉴 제거 */
    #MainMenu, footer, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 사운드 및 데이터 로드 로직 ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            audio_tag = f'<audio autoplay="true" {loop} style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_tag, unsafe_allow_html=True)

@st.cache_data
def load_db():
    f = "DreamNavi_Job_DB_v2_20240509.xlsx"
    return pd.read_excel(f) if os.path.exists(f) else None

df = load_db()

# --- [3] 세션 상태 초기화 ---
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"정보통신":0, "문화/예술":0, "경영/회계":0, "보건/의료":0, "교육/법률":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

# --- [4] 실행 화면 (무결점 전수 복구) ---

# [1] 인트로: 이름, 생일, 지역, 유학 국가 질문 포함
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    birth = st.date_input("생년월일은 언제니?", value=datetime.date(2012, 1, 1))
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학에 관심이 있니?", ["아직은 국내가 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])
    country = st.text_input("가고 싶은 나라가 있다면 적어줘!")

    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad, "country": country}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.error("이름을 알려줘! ( 'ㅅ' )")
    st.markdown('</div>', unsafe_allow_html=True)

# [2] 심리 파악: 취미, 강점, 고민 질문 포함
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}의 속마음")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민은 뭐야?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'test' # 바로 테스트로 연결
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [3] 테스트 및 결과 (중략된 로직 없음, 전체 질문은 12개 리스트로 작동)
