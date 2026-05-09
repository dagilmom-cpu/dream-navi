import streamlit as st
import pandas as pd
import datetime
import base64
import os
import plotly.graph_objects as go

# --- 1. UI/UX 및 디자인 고정 (중앙 정렬 & 헤더 제거) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 전체 배경 및 폰트 */
    html, body, [class*="css"] { 
        font-family: 'Pretendard', sans-serif; 
        color: #1e293b; 
    }
    
    .stApp { 
        background-color: #ffffff; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
    }

    /* 상단 화이트 바(헤더) 및 메뉴 완전 제거 */
    header { visibility: hidden; height: 0px !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display:none; }

    /* 중앙 정렬 컨테이너 */
    .st-emotion-cache-16idsys, .st-emotion-cache-z5fcl4 {
        display: flex; justify-content: center;
    }
    
    /* 모몽이 둥실둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-float { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 40px auto;
    }
    
    /* 메인 카드 디자인 (중앙 집중형) */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; max-width: 550px; margin: 0 auto;
        text-align: center;
    }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 4em; font-weight: bold; 
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #444; transition: 0.3s; 
        box-shadow: 0 4px 15px rgba(181,255,252,0.3); 
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }

    /* 입력 폼 라벨 좌측 정렬 */
    .stMarkdown, .stTextInput label, .stSelectbox label, .stRadio label { text-align: left !important; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사운드 재생 엔진 (첫 클릭 시 강제 호출) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            md = f"""
                <audio id="audio-element" autoplay="true" {loop} style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById("audio-element");
                    audio.play().catch(function(error) {{ console.log("Audio play failed:", error); }});
                </script>
                """
            st.markdown(md, unsafe_allow_html=True)

# --- 3. 세션 상태 및 진단 질문 데이터 고정 ---
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0, "AI":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

questions = [
    {"q": "기계의 원리를 파악하고 직접 조립하거나 고치는 과정이 즐겁나요?", "type": "R"},
    {"q": "데이터 속에서 논리적인 패턴을 찾아내는 일이 흥미로운가요?", "type": "I"},
    {"q": "새로운 디지털 도구나 AI를 남들보다 먼저 탐구하고 사용해보나요?", "type": "AI"},
    {"q": "친구들의 의견을 조율하고 이끄는 리더 역할을 할 때 보람을 느끼나요?", "type": "S"},
    # (실제 서비스 시 12문항 전체가 이 패턴으로 동작합니다)
]

# --- 4. 화면 구현 (로직 체인) ---

# [PAGE 1: 인트로]
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-float">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=220)
    else: st.write("🐹 (모몽이 이미지를 준비 중이에요!)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align:center;'>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학을 가보고 싶니?", ["국내 대학이 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])

    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.error("이름을 입력해야 모몽이가 출발할 수 있어! ( 'ㅅ' )")
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 파악]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}의 마음을 들려줄래?")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하거나 고민인 건 뭐야?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 엔진 설명]
elif st.session_state.page == 'engine_desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 모몽이의 4가지 분석 구슬")
    st.write("우리는 홀랜드(흥미), 다중지능(재능), 게임화(행동), 미래역량(AI)을 통해 네 미래 지도를 그릴 거야.")
    st.info("💡 12가지 정교한 질문을 통해 네가 가진 빛나는 가능성을 찾아줄게!")
    if st.button("이해했어, 테스트 시작!"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 테스트 및 결과 리포트는 고정된 로직에 따라 점수 합산 및 출력]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    curr_q = questions[st.session_state.step]
    st.markdown(f"### Q{st.session_state.step + 1}. {curr_q['q']}")
    if st.button("매우 그렇다"):
        play_sound("kkyu.mp3")
        st.session_state.scores[curr_q['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    # (생략된 버튼 및 결과 로직은 이전 고정 로직 유지)
    st.markdown('</div>', unsafe_allow_html=True)
