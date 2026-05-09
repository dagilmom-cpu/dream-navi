import streamlit as st
import pandas as pd
import time

# --- 1. 초기 설정 및 CSS (이미지 9의 디자인을 최대한 반영) ---
st.set_page_config(page_title="꿈네비 - 모몽이와 꿈 찾기", layout="centered")

# 카카오톡/애플 느낌의 둥글둥글한 폰트와 파스텔톤 CSS
st.markdown("""
    <style>
    @font-face { font-family: 'NanumSquareRound'; src: url('https://hangeul.naver.com/font/nanum/NanumSquareRound/NanumSquareRoundR.ttf'); }
    html, body, [class*="css"]  { font-family: 'NanumSquareRound', sans-serif; color: #333; }
    
    .stApp { background-color: #ffffff; }
    
    # /* 메인 카드 디자인 */
    .main-card {
        background-color: #ffffff;
        border-radius: 30px;
        padding: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    # /* 질문 박스 스타일 */
    .question-box {
        background-color: #fcfcfc;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        border: 1px solid #eee;
    }
    
    # /* 파스텔 답변 버튼 스타일 */
    .stButton>button {
        border-radius: 20px;
        height: 3em;
        font-weight: bold;
        transition: all 0.2s;
        border: none;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    
    # /* 매우그렇다 (연그린) */
    div[data-testid="column"]:nth-of-type(1) .stButton>button { background-color: #e3f9e5; color: #2d6a31; }
    # /* 그렇다 (연하늘) */
    div[data-testid="column"]:nth-of-type(2) .stButton>button { background-color: #e0f2fe; color: #0369a1; }
    # /* 보통이다 (연노랑) */
    div[data-testid="column"]:nth-of-type(3) .stButton>button { background-color: #fef9c3; color: #a16207; }
    # /* 아니다 (연핑크) */
    div[data-testid="column"]:nth-of-type(4) .stButton>button { background-color: #ffe4e6; color: #9f1239; }
    
    </style>
    """, unsafe_allow_html=True)

# --- 2. 세션 상태 관리 (데이터 보관창고) ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'page' not in st.session_state: st.session_state.page = 'intro'
# 4대 이론 데이터를 담을 그릇
if 'scores' not in st.session_state:
    st.session_state.scores = {
        "Holland": {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0},
        "MI": {"논리":0, "언어":0, "공간":0, "인간":0}, # 다중지능 일부
        "Game": {"위험감수":0, "문제해결":0}, # 게임화 역량
        "Future": {"AI활용":0, "시스템사고":0} # 미래역량
    }

# --- 3. 4대 이론 통합 질문지 데이터 ---
questions = [
    # 홀랜드 진단 (R형)
    {"q": "모몽이가 준 고장 난 로봇을 직접 분해해서 고쳐보고 싶나요? 🔩", "type": "Holland", "key": "R"},
    # 다중지능 진단 (논리수학)
    {"q": "복잡한 미로 찾기나 수수께끼를 풀 때 시간 가는 줄 모르나요? 🧠", "type": "MI", "key": "논리"},
    # 미래역량 진단 (AI활용)
    {"q": "챗GPT 같은 AI 친구에게 궁금한 점을 물어보는 게 익숙한가요? 🤖", "type": "Future", "key": "AI활용"},
    # 게임화 역량 (위험감수)
    {"q": "(미니게임 상황) 점수를 잃을 수도 있지만, 대박 보상이 있는 보물상자를 열 건가요? 🎁", "type": "Game", "key": "위험감수"},
    # ... (지면상 4개만 구현, 실제로는 12개로 확장됩니다)
]

# --- 4. 화면 구현 (UX/UI 가이드 반영) ---

# [PAGE 1: 인트로 - 모몽이와 첫 만남]
if st.session_state.page == 'intro':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.image("momong.png", width=200) # 짤뚱한 모몽이 이미지
    st.title("안녕! 나는 꿈 가이드 '모몽이'야 ( 'ㅅ' )")
    st.subheader("네가 어떤 '꿈 구슬'을 가졌는지 함께 찾아볼까?")
    
    name = st.text_input("네 이름이 뭐야?", placeholder="별명도 좋아!")
    grade = st.selectbox("지금 몇 학년이야?", ["초등학교 4학년", "초등학교 5학년", "초등학교 6학년", "중학교 1학년"])
    
    if st.button("모몽이와 꿈 찾기 시작! ✨"):
        st.session_state.user_info = {"name": name, "grade": grade}
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 테스트 - 모몽이의 꿈 수집]
elif st.session_state.page == 'test':
    # 상단 진행바 및 모몽이
    progress = st.session_state.step / len(questions)
    st.progress(progress)
    st.markdown(f"<p style='text-align:center;'>지금까지 {st.session_state.step}개의 꿈 구슬 수집 완료! ( 'ㅅ' )</p>", unsafe_allow_html=True)

    # 질문 박스
    curr_q = questions[st.session_state.step]
    st.markdown(f'<div class="question-box"><h3>{curr_q["q"]}</h3></div>', unsafe_allow_html=True)
    
    # 파스텔 답변 버튼 (4단 구성)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("😄 매우 그렇다"):
            st.session_state.scores[curr_q['type']][curr_q['key']] += 2
            st.session_state.step += 1
            st.rerun()
    with col2:
        if st.button("🙂 그렇다"):
            st.session_state.scores[curr_q['type']][curr_q['key']] += 1
            st.session_state.step += 1
            st.rerun()
    # ... 보통이다, 아니다 버튼 구현 (생략, 위와 동일 로직)
    
    # 모든 질문 완료 시 결과 페이지로
    if st.session_state.step >= len(questions):
        st.session_state.page = 'result'
        st.rerun()

# [PAGE 3: 결과 - 모몽이가 보여주는 너의 꿈 지도]
elif st.session_state.page == 'result':
    st.balloons() # 축하 효과
    st.title(f"🎊 {st.session_state.user_info['name']}님의 잠재력 스펙트럼 리포트")
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    # 여기에 오각형 방사형 그래프(Radar Chart) 코드가 추가됩니다 (차후 구현)
    st.subheader("📊 모몽이가 분석한 너의 핵심 강점")
    
    # 4대 이론 점수를 바탕으로 하이라이트 출력
    scores = st.session_state.scores
    if scores['Future']['AI활용'] > 1:
        st.info("💡 너는 미래의 기술을 두려워하지 않고 활용하는 **'AI 리터러시'**가 탁월해!")
    if scores['Holland']['R'] > 1:
        st.success("🛠️ 손으로 무언가를 만들고 고치는 **'실재적 성향'**이 강하구나!")
        
    st.markdown("---")
    st.subheader("🛰️ 너에게 어울리는 미래 융합 직업")
    st.write("너의 강점들을 모아보니... 너는 **[스마트 시티 디지털 트윈 설계자]**가 딱이야!")
    st.markdown('</div>', unsafe_allow_html=True)
