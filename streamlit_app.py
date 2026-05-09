import streamlit as st
import pandas as pd
import datetime
import os

# --- [1] UI/UX 극강 처방 (하얀 바/툴바/헤더 완전 박멸) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 스트림릿 내부 시스템이 만든 모든 상단 요소 물리적 삭제 */
    /* 클래스 이름과 상관없이 최상단에 고정된 모든 바를 타겟팅합니다. */
    [data-testid="stHeader"], 
    header, 
    .st-emotion-cache-18ni7ap, 
    .st-emotion-cache-z5fcl4,
    [data-testid="stToolbar"] {
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 2. 본문 영역을 강제로 위로 끌어올림 (여백 절대 허용 안 함) */
    .main .block-container {
        padding-top: 55px !important; /* 커스텀 헤더만큼만 띄움 */
        max-width: 500px !important;
        margin: 0 auto;
    }
    
    /* 3. 우리가 만든 이쁜 민트-핑크 커스텀 바 (이걸로 대체) */
    .custom-top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 50px;
        background: linear-gradient(90deg, #B5FFFC 0%, #FFDEE9 100%);
        z-index: 999999; /* 모든 시스템 요소보다 위에 위치 */
    }

    /* 4. 전체 디자인 세팅 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', sans-serif; 
        color: #1e293b; 
    }
    
    .stApp { 
        background-color: #ffffff;
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.3) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.3) 0, transparent 50%); 
    }

    /* 메인 카드 디자인 */
    .main-card { 
        background: rgba(255, 255, 255, 0.95); 
        border-radius: 30px; 
        padding: 40px 30px; 
        box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; 
        width: 100%;
        text-align: center;
    }
    
    h1 { font-size: 32px !important; font-weight: 800 !important; margin-bottom: 5px !important; }
    .sub-title { font-size: 15px; color: #64748b; margin-bottom: 25px; }
    
    label { font-size: 15px !important; font-weight: 600 !important; text-align: left !important; display: block !important; margin-top: 15px !important; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: #B5FFFC; border: none; color: #334155; transition: 0.3s; margin-top: 25px;
        box-shadow: 0 4px 15px rgba(181,255,252,0.3);
    }
    .stButton>button:hover { background: #FFDEE9; transform: translateY(-2px); }

    /* 푸터 및 기타 불필요 요소 제거 */
    footer, .stDeployButton { display: none !important; }
    </style>
    
    <div class="custom-top-bar"></div>
    """, unsafe_allow_html=True)

# --- [2] 데이터 및 로직 처리 ---
@st.cache_data
def load_db():
    f = "DreamNavi_Job_DB_v2_20240509.xlsx"
    return pd.read_excel(f) if os.path.exists(f) else None

df = load_db()

# 세션 상태 초기화
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"정보통신":0, "문화/예술":0, "경영/회계":0, "보건/의료":0, "교육/법률":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

# --- [3] 화면 구현 ---

# 인트로 화면
if st.session_state.page == 'intro':
    st.markdown("<h1>꿈네비</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-title">나만의 미래 지도를 그리는 시간</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("이름이 뭐야?", placeholder="이름을 입력해줘")
    birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1))
    region = st.selectbox("사는 지역", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학에 관심이 있니?", ["국내가 좋아", "고민 중이야", "세계로 가고 싶어"])

    if st.button("내 꿈 찾으러 출발! ✨"):
        if name:
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.error("이름을 입력해줘!")
    st.markdown('</div>', unsafe_allow_html=True)

# (중략: 심리 파악 및 12문항 로직은 v18.0과 동일하게 유지됩니다.)
