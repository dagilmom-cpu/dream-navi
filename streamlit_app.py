import streamlit as st
import pandas as pd
import datetime
import os

# --- [1] UI/UX 극강 처방 (하얀 바/툴바 완전 박멸) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 상단 툴바(Deploy, Manage app 등) 물리적 박멸 */
    div[data-testid="stToolbar"], .stDeployButton, header, [data-testid="stHeader"] {
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
    }
    
    /* 민트-핑크 그라데이션 헤더 직접 구현 (기본 헤더 대신 사용) */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: linear-gradient(90deg, #B5FFFC 0%, #FFDEE9 100%);
        z-index: 999;
    }

    /* 2. 전체 중앙 정렬 및 배경 */
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

    /* 본문 상단 여백 (커스텀 헤더 높이만큼 띄움) */
    .block-container {
        padding-top: 5rem !important;
        max-width: 520px !important;
        margin: 0 auto;
    }

    /* 3. 메인 카드 디자인 */
    .main-card { 
        background: rgba(255, 255, 255, 0.95); border-radius: 32px; 
        padding: 45px 35px; box-shadow: 0 20px 40px rgba(0,0,0,0.04); 
        border: 1px solid #f1f5f9; width: 100%; margin-top: 10px;
    }
    
    h1 { font-size: 32px !important; font-weight: 800 !important; margin-bottom: 5px !important; }
    .sub-title { font-size: 16px; color: #64748b; margin-bottom: 30px; }
    
    label { font-size: 16px !important; font-weight: 600 !important; text-align: left !important; display: block !important; margin-top: 20px !important; }
    
    /* 4. 버튼 스타일링 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: #B5FFFC; border: none; color: #334155; transition: 0.4s; margin-top: 30px;
        box-shadow: 0 8px 20px rgba(181,255,252,0.5);
    }
    .stButton>button:hover { background: #FFDEE9; transform: translateY(-3px); }

    footer { display: none !important; }
    </style>
    
    <div class="custom-header"></div>
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

# 12문항 전수 등록 (데이터 기반)
questions = [
    {"q": "컴퓨터 프로그램이나 앱이 어떻게 만들어지는지 궁금하고 직접 만들고 싶니?", "type": "정보통신"},
    {"q": "그림을 그리거나 영상을 편집해서 나만의 작품을 만드는 게 즐겁니?", "type": "문화/예술"},
    {"q": "용돈을 계획적으로 관리하거나 물건을 사고파는 경제 활동에 관심이 있니?", "type": "경영/회계"},
    {"q": "아픈 사람이나 동물을 도와주고 치료하는 일에 보람을 느끼니?", "type": "보건/의료"},
    {"q": "친구들에게 새로운 지식을 알려주거나 법과 규칙을 지키는 게 중요하다고 생각하니?", "type": "교육/법률"},
    {"q": "새로운 스마트 기기가 나오면 먼저 써보고 원리를 파악하는 걸 좋아하니?", "type": "정보통신"},
    {"q": "무대에서 공연하거나 전시회에서 작품을 보여주는 상상을 자주 하니?", "type": "문화/예술"},
    {"q": "복잡한 문제를 효율적으로 해결하기 위해 계획을 세우는 걸 잘하니?", "type": "경영/회계"},
    {"q": "생명과학 실험이나 우리 몸의 구조를 탐구하는 수업이 재미있니?", "type": "보건/의료"},
    {"q": "어려운 처지에 놓인 사람들을 위해 목소리를 내고 돕고 싶니?", "type": "교육/법률"},
    {"q": "방대한 데이터를 분석해서 미래를 예측하는 일이 멋져 보이니?", "type": "정보통신"},
    {"q": "팀 프로젝트를 할 때 창의적인 아이디어를 내서 분위기를 이끄니?", "type": "문화/예술"}
]

# --- [3] 화면 구현 ---

# 1. 인트로 (정보 수집)
if st.session_state.page == 'intro':
    st.markdown("<h1>꿈네비</h1>", unsafe_allow_html=True)
    st.markdown('<p class="sub-title">나만의 미래 지도를 그리는 시간</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1))
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학에 관심이 있니?", ["아직은 국내가 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])
    country = st.text_input("가고 싶은 나라가 있다면 적어줘!")

    if st.button("내 꿈 찾으러 출발! ✨"):
        if name:
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad, "country": country}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.error("이름을 꼭 입력해줘!")
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 속마음 (심리 파악)
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

# 3. 테스트 (12문항 로직)
elif st.session_state.page == 'test':
    st.markdown("<h1>꿈 진단</h1>", unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">Q{st.session_state.step + 1} / {len(questions)}</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    q = questions[st.session_state.step]
    st.markdown(f"<h3>{q['q']}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    if col1.button("매우 그렇다"):
        st.session_state.scores[q['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    if col2.button("그렇지 않다"):
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4. 결과 (데이터 매칭)
elif st.session_state.page == 'result':
    st.markdown(f"<h1>{st.session_state.user_info['name']}의 리포트</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    best = max(st.session_state.scores, key=st.session_state.scores.get)
    if df is not None:
        m = df[df['대분류'] == best].iloc[0] if not df[df['대분류'] == best].empty else df.iloc[0]
        st.success(f"너와 잘 맞는 분야는 [{best}]야!")
        st.info(f"📍 추천 직무: {m['직무군']}")
        st.write(f"🚀 미래 유망 직업: {m['미래유망직업']}")
    
    if st.button("다시 하기"):
        st.session_state.page = 'intro'
        st.session_state.step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
