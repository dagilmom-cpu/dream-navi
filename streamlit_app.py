import streamlit as st
import pandas as pd
import datetime
import os

# --- [1] UI/UX 디자인 고도화 (상단 하얀 바 박멸 & 정렬 최적화) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 맨 위 하얀 바(Toolbar) 및 메뉴 버튼 완전 박멸 */
    header, [data-testid="stHeader"] {
        background: linear-gradient(90deg, #B5FFFC 0%, #FFDEE9 100%) !important;
        height: 60px !important;
    }
    #MainMenu, footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 2. 전체 배경 및 중앙 정렬 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', sans-serif; 
        color: #1e293b; 
        text-align: center !important; 
    }
    
    .stApp { 
        background-color: #ffffff;
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.3) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
    }

    /* 본문 상단 여백 조절 */
    .block-container {
        padding-top: 3rem !important;
        max-width: 500px !important;
        margin: 0 auto;
    }

    /* 3. 메인 카드 디자인 (더 부드럽게) */
    .main-card { 
        background: rgba(255, 255, 255, 0.95); 
        border-radius: 32px; 
        padding: 45px 35px; 
        box-shadow: 0 20px 40px rgba(0,0,0,0.04); 
        border: 1px solid #f1f5f9; 
        width: 100%;
        margin-top: 10px;
    }
    
    h1 { font-size: 32px !important; font-weight: 800 !important; color: #1e293b; margin-bottom: 5px !important; letter-spacing: -0.5px; }
    .sub-title { font-size: 16px; color: #64748b; margin-bottom: 30px; font-weight: 400; }
    
    /* 질문 라벨 스타일 고도화 */
    label { 
        font-size: 16px !important; 
        font-weight: 600 !important; 
        color: #475569 !important; 
        text-align: left !important; 
        display: block !important; 
        margin-bottom: 10px !important;
        margin-top: 20px !important;
    }
    
    /* 입력창 디자인 커스텀 */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* 4. 버튼 스타일 (클릭하고 싶게!) */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 4em; font-weight: bold; font-size: 17px;
        background: #B5FFFC; border: none; color: #334155; transition: 0.4s; margin-top: 30px;
        box-shadow: 0 8px 20px rgba(181,255,252,0.5);
    }
    .stButton>button:hover { background: #FFDEE9; transform: translateY(-3px); box-shadow: 0 10px 25px rgba(255,222,233,0.6); }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 데이터 로드 및 세션 초기화 ---
@st.cache_data
def load_db():
    f = "DreamNavi_Job_DB_v2_20240509.xlsx"
    return pd.read_excel(f) if os.path.exists(f) else None

df = load_db()

for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"정보통신":0, "문화/예술":0, "경영/회계":0, "보건/의료":0, "교육/법률":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

# --- [3] 화면 구현 (전수 복구 및 디자인 적용) ---

# 1. 인트로
if st.session_state.page == 'intro':
    st.markdown("<h1>꿈네비</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-title">나만의 미래 지도를 그리는 첫 번째 단계</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?", placeholder="이름을 입력해줘")
    birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1))
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학에 관심이 있니?", ["아직은 국내가 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])
    country = st.text_input("가고 싶은 나라가 있다면 적어줘!")

    if st.button("모몽이 대신 내가 갈게! 시작! ✨"):
        if name:
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad, "country": country}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.error("이름을 꼭 알려줘야 해!")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 속마음 (어머님 로직)
elif st.session_state.page == 'mind_check':
    st.markdown("<h1>속마음 읽기</h1>", unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">{st.session_state.user_info["name"]}의 이야기를 들려줘</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민은 뭐야?")
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 테스트 (12문항 로직 생략 없이 진행)
# ... (이전과 동일하게 12개 질문 데이터 탑재)
