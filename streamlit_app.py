import streamlit as st
import pandas as pd
import datetime
import base64
import os
import plotly.graph_objects as go

# --- 1. UI/UX 설정 (엄마의 시선으로 고정) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; color: #1e293b; }
    
    /* 전체 배경 수채화 톤 */
    .stApp { 
        background-color: #ffffff; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
    }

    /* 모몽이 둥실둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-float { display: flex; justify-content: center; animation: floating 2.5s ease-in-out infinite; margin-bottom: 20px; }
    
    /* 상단 바 제거 및 카드 스타일 */
    header { visibility: hidden; }
    .main-card { background: rgba(255, 255, 255, 0.8); border-radius: 30px; padding: 35px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; }
    
    /* 버튼 스타일 (시안 반영) */
    .stButton>button { width: 100%; border-radius: 50px; height: 3.5em; font-weight: bold; background: #B5FFFC; border: none; color: #444; transition: 0.3s; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 안전한 사운드 재생 함수 ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            md = f'<audio autoplay="true" {loop}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)

# --- 3. 세션 상태 초기화 (에러 방지) ---
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"R":5, "I":5, "A":5, "S":5, "E":5, "C":5, "AI":5}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

# --- 4. 질문지 로직 ---
questions = [
    {"q": "로봇이나 복잡한 기계의 원리를 파악하고 고치는 게 즐겁니?", "type": "R"},
    {"q": "데이터 속에서 논리적인 규칙을 찾아내는 일이 흥미로워?", "type": "I"},
    {"q": "새로운 AI 도구를 남들보다 빠르게 써보는 걸 좋아해?", "type": "AI"},
    {"q": "친구들의 의견을 조율하고 이끄는 리더 역할이 편안해?", "type": "S"}
]

# --- 5. 화면 구현 ---

# [PAGE 1: 인트로]
if st.session_state.page == 'intro':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<div class="momong-float">', unsafe_allow_html=True)
    if os.path.exists("momong.png"):
        st.image("momong.png", width=180)
    else:
        st.write("🐹 (모몽이 이미지를 준비중이야!)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'>모몽이와 첫 만남</h2>", unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학을 가보고 싶니?", ["아직은 국내가 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])

    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
        else:
            st.warning("너의 이름을 알려줘! ( 'ㅅ' )")
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 파악]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"{st.session_state.user_info['name']}의 속마음이 궁금해")
    hobby = st.text_input("🌈 너를 웃게 만드는 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민이 있니?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 4대 엔진 설명]
elif st.session_state.page == 'engine_desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 모몽이의 4가지 진단 구슬")
    st.write("우리는 흥미, 재능, 행동, AI 역량을 통해 네 미래 지도를 그릴 거야.")
    st.info("💡 12가지 질문을 통해 네가 가진 빛나는 가능성을 찾아줄게!")
    if st.button("좋아, 테스트 시작!"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 테스트 진행]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    curr_q = questions[st.session_state.step]
    st.write(f"### Q{st.session_state.step + 1}. {curr_q['q']}")
    
    if st.button("매우 그렇다"):
        play_sound("kkyu.mp3")
        st.session_state.scores[curr_q['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    if st.button("그렇지 않다"):
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 5: 결과 리포트]
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 꿈 지도")
    
    # 그래프 시각화 (근거 제시)
    categories = list(st.session_state.scores.keys())
    values = list(st.session_state.scores.values())
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#14b8a6'))
    st.plotly_chart(fig)
    
    st.subheader("📍 엄마와 모몽이의 전략 조언")
    st.write(f"거주지 '{st.session_state.user_info['region']}'의 이점을 살린 전략을 짜줄게.")
    st.error(f"⚠️ {st.session_state.user_info['name']}야, {st.session_state.mind_info['hard_thing']} 때문에 힘들었지? 하지만 너에겐 엄청난 잠재력이 있어!")
    
    if st.button("다시 처음으로"):
        st.session_state.page = 'intro'
        st.session_state.step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
