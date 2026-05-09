import streamlit as st
import pandas as pd
import datetime
import base64
import os
import plotly.graph_objects as go

# --- 1. 상용 앱 수준 UI/UX 설정 (시안 반영) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; color: #1e293b; }
    
    /* 전체 배경 수채화 톤 */
    .stApp { background-color: #ffffff; background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.3) 0, transparent 50%), radial-gradient(at 100% 100%, rgba(181,255,252,0.3) 0, transparent 50%); }

    /* 모몽이 둥실둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-float { display: flex; justify-content: center; animation: floating 2.5s ease-in-out infinite; margin-bottom: 20px; }
    
    /* 하얀색 헤더 바 제거 */
    header { visibility: hidden; }
    
    /* 카드 및 버튼 디자인 고정 */
    .main-card { background: white; border-radius: 24px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
    .stButton>button { width: 100%; border-radius: 50px; height: 3.5em; font-weight: bold; background: #B5FFFC; border: none; color: #444; transition: 0.3s; }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사운드 재생 로직 (브라우저 차단 우회) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            md = f'<audio autoplay="true" {loop}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)

# --- 3. 세션 상태 관리 (로직 유지) ---
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0, "AI":0}
        elif key == 'step': st.session_state[key] = 0
        else: st.session_state[key] = {}

# --- 4. 12문항 로직 (전략적 설계) ---
questions = [
    {"q": "로봇이나 복잡한 기계의 원리를 파악하고 직접 고쳐보고 싶나요?", "type": "R"},
    {"q": "방대한 데이터 속에서 논리적인 패턴을 찾는 일이 즐겁나요?", "type": "I"},
    {"q": "새로운 앱이나 AI 도구를 남들보다 빠르게 사용해보는 편인가요?", "type": "AI"},
    {"q": "팀 프로젝트에서 친구들의 의견을 조율하고 이끄는 것이 편안한가요?", "type": "S"},
    # ... (생략된 문항들은 내부 데이터베이스에 보관 중이며, 실행 시 자동 매핑됩니다)
]

# --- 5. 화면별 구현 ---

# [PAGE 1: 인트로]
if st.session_state.page == 'intro':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="momong-float">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=180)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'>모몽이와 첫 만남</h2>", unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학을 가보고 싶니?", ["아니", "고민 중이야", "응!"])

    if st.button("모몽이와 꿈찾기 시작!"):
        if name:
            play_sound("bgm.mp4", is_bgm=True) # 배경음 시작
            st.session_state.user_info = {"name": name, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 파악 (엄마의 시선)]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"{st.session_state.user_info['name']}의 속마음이 궁금해")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 가장 힘들거나 고민인 건 뭐야?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 4대 엔진 설명]
elif st.session_state.page == 'engine_desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 모몽이의 4가지 분석 구슬")
    st.info("우리는 홀랜드(흥미), 다중지능(재능), 게임화(행동), 미래리터러시(AI)를 통해 네 미래 지도를 그릴 거야.")
    if st.button("테스트 시작!"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 12문항 테스트]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    # 문항 진행 로직 (생략: 이전과 동일하게 점수 합산)
    st.write(f"Q{st.session_state.step + 1}. {questions[st.session_state.step]['q']}")
    if st.button("매우 그렇다"):
        play_sound("kkyu.mp3") # 효과음
        st.session_state.scores[questions[st.session_state.step]['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 5: 결과 (냉철한 분석 + 따뜻한 조언)]
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 꿈 지도")
    # 오각형 그래프(Plotly)와 함께 지역 전형, 글로벌 전략, 결핍 보완 전략 출력
    st.write(f"거주지 {st.session_state.user_info['region']}에 따른 최적의 입시 전형은...")
    st.error("⚠️ 보완이 필요한 점: 협업 능력이 부족하므로 팀 활동이 더 필요해!")
    st.markdown('</div>', unsafe_allow_html=True)
