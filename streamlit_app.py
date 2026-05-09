import streamlit as st
import pandas as pd
import datetime
import base64
import os
import plotly.graph_objects as go
from groq import Groq

# --- 1. 브랜드 가이드라인 적용 UI 설정 ---
st.set_page_config(page_title="꿈네비 | 프리미엄 진로 컨설팅", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; color: #1e293b; background-color: #f8fafc; }
    
    .momong-container { display: flex; justify-content: center; animation: floating 2.5s ease-in-out infinite; margin: 20px 0; }
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    
    .main-card {
        background: white; border-radius: 24px; padding: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04); border: 1px solid #e2e8f0; margin-bottom: 20px;
    }
    
    .engine-box {
        background-color: #f1f5f9; border-radius: 16px; padding: 20px; margin-bottom: 15px;
        border-left: 6px solid #14b8a6;
    }
    
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600;
        background-color: #ffffff; color: #0f172a; border: 1px solid #e2e8f0; transition: 0.2s;
    }
    .stButton>button:hover { background-color: #f1f5f9; border-color: #14b8a6; color: #14b8a6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 세션 상태 관리 ---
states = {'page': 'intro', 'step': 0, 'scores': {"Holland":0, "MI":0, "Game":0, "Future":0}, 'user_info': {}, 'mind_info': {}}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. 화면별 구현 로직 ---

# [PAGE 1: 온보딩]
if st.session_state.page == 'intro':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if os.path.exists("momong.png"):
        st.markdown('<div class="momong-container">', unsafe_allow_html=True)
        st.image("momong.png", width=180)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("꿈네비: 미래 항법 시스템")
    st.write("반가워요! 우리 아이의 잠재력을 데이터로 정밀 분석하여, 최적의 입시 및 진로 로드맵을 설계합니다.")
    
    name = st.text_input("아이의 성함 혹은 별명을 입력해 주세요.")
    birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1), format="YYYY/MM/DD")
    region = st.selectbox("거주 지역", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("글로벌 유학 희망 여부", ["국내 대학 집중", "국내/해외 병행", "해외 대학 전념"])

    if st.button("진단 시작하기"):
        if name:
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.warning("정확한 분석을 위해 성함을 입력해 주세요.")
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 파악]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"{st.session_state.user_info['name']}님, 본격적인 탐험 전에 마음을 읽어볼까요?")
    
    hobby = st.text_input("🌈 생각만 해도 기분이 좋아지는 취미나 활동이 있나요?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다! 하는 게 있다면요?")
    hard_thing = st.text_area("😟 요즘 나를 힘들게 하거나 고민인 점이 있다면 무엇인가요?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 4대 엔진 상세 설명]
elif st.session_state.page == 'engine_desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 모몽이의 4가지 진단 구슬")
    st.write("꿈네비는 4가지 과학적 엔진을 통해 당신만의 미래 지도를 그립니다.")
    
    st.markdown("""
    <div class="engine-box">
        <b>1. 흥미 구슬 (Holland & 다중지능)</b><br>
        네가 무엇을 좋아하고, 어떤 방면에서 가장 똑똑한지 분석해. 네가 가진 기질에 딱 맞는 직업 환경을 찾아줄게.
    </div>
    <div class="engine-box">
        <b>2. 행동 구슬 (게임화 역량 GBA)</b><br>
        단순한 질문이 아니야! 네가 위기 상황에서 어떤 선택을 하는지 행동 패턴을 추적해서 진짜 문제 해결력을 측정해.
    </div>
    <div class="engine-box">
        <b>3. 미래 구슬 (미래 리터러시)</b><br>
        2030년, AI와 함께 살아갈 세상에서 네가 얼마나 준비되었는지 확인해. 새로운 기술을 다루는 너의 능력을 체크할 거야.
    </div>
    <div class="engine-box">
        <b>4. 마음 구슬 (심리 회복 탄력성)</b><br>
        네가 얼마나 단단한 마음을 가졌는지, 힘들 때 어떻게 다시 일어설 수 있는지 분석해서 따뜻한 조언을 건넬 거야.
    </div>
    """, unsafe_allow_html=True)
    
    st.info("💡 12가지 정교한 문항이 준비되었습니다. 모든 준비가 끝났다면 아래 버튼을 눌러주세요.")
    if st.button("좋아, 테스트 시작하기! ✨"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 테스트 진행 및 결과 리포트는 이전 로직 고정]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("테스트 진행 중... (12문항 로직 적용 예정)")
    if st.button("결과 확인 (임시)"):
        st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
