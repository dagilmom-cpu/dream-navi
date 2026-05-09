import streamlit as st
import pandas as pd
import datetime
import base64
import os
from groq import Groq

# --- 1. 초기 설정 및 CSS (시안 디자인 구현) ---
st.set_page_config(page_title="꿈네비", layout="centered")

# 배경 수채화 효과, 폰트, 모몽이 둥실 애니메이션 CSS
st.markdown("""
    <style>
    /* 전체 배경 수채화 번짐 효과 */
    .stApp {
        background: white;
        background-image: radial-gradient(#FFDEE9 1px, transparent 1px), radial-gradient(#B5FFFC 1px, transparent 1px);
        background-size: 50px 50px;
        background-position: 0 0, 25px 25px;
        opacity: 0.8;
    }
    
    /* 둥글둥글 귀여운 한글 폰트 적용 (폰트 파일이 있다면 서빙 필요, 여기선 기본 둥근폰트 예시) */
    html, body, [class*="css"]  { font-family: 'NanumGothic', sans-serif; color: #444; }
    
    /* 둥실둥실 움직이는 모몽이 컨테이너 */
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    .momong-container {
        display: flex; justify-content: center;
        animation: floating 3s ease-in-out infinite;
        margin-top: 30px; margin-bottom: 20px;
    }
    
    /* 입력창 및 버튼 디자인 개조 (둥글게, 파스텔 톤) */
    .stTextInput>div>div>input, .stDateInput>div>div>input { border-radius: 20px; border: 1px solid #ddd; padding: 10px 20px; }
    .stButton>button {
        background-color: #B5FFFC; color: #444;
        border-radius: 25px; border: none;
        padding: 15px 30px; font-weight: bold; width: 100%; height: 3.5em;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;
    }
    .stButton>button:hover { background-color: #FFDEE9; transform: translateY(-3px); }
    
    /* 하얀색 상단 바(Header) 숨기기 */
    header { visibility: hidden; }
    
    /* 오디오 숨기기 */
    .stAudio { display: none; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사운드 재생 함수 (효과음 & 배경음 통합) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                loop = "loop" if is_bgm else ""
                # 브라우저 정책 준수: autoplay=True로 설정하되, 첫 클릭 후 재생
                md = f'<audio autoplay="true" {loop}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
        except Exception as e:
            pass # 소리 재생 실패 시 조용히 넘어감

# --- 3. 세션 상태 관리 ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'scores' not in st.session_state:
    st.session_state.scores = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0}

# --- 4. 질문지 데이터 (4차 산업혁명 융합 직업 기반) ---
questions = [
    # 시안 2페이지의 '데이터 분석', 'UI/UX 디자인' 등을 질문으로 구현
    {"q": "( 'ㅅ' ) : 방대한 데이터 속에서 숨겨진 패턴을 찾아내는 일이 흥미롭나요? (데이터 과학자)", "type": "I"},
    {"q": "( 'ㅅ' ) : 사람들이 사용하기 편하고 아름다운 디지털 화면을 디자인하고 싶나요? (UI/UX 디자이너)", "type": "A"},
    {"q": "( 'ㅅ' ) : 움직이는 기계나 로봇을 직접 조립하고 프로그래밍하는 과정이 즐거운가요? (엔지니어)", "type": "R"},
    {"q": "( 'ㅅ' ) : 새로운 디지털 콘텐츠(유튜브, 웹툰 등)를 기획하고 널리 알리고 싶나요? (콘텐츠 기획자)", "type": "E"},
    # (총 12문항까지 이전 코드와 동일하게 확장)
]

# --- 5. 화면 구현 로직 ---

# [PAGE 1: 인트로 - 시안 1페이지 구현]
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-container">', unsafe_allow_html=True)
    # 짤뚱한 모몽이 이미지 (momong.png 확인 필요)
    if os.path.exists("momong.png"):
        st.image("momong.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>모몽이와 첫 만남</h2>", unsafe_allow_html=True)
    
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    grade = st.text_input("몇 학년인지 알려줘!")
    
    # 사운드 활성화 버튼 (시안 1페이지의 시작 버튼)
    # 이 버튼을 클릭해야 사운드가 출력되기 시작합니다.
    if st.button("🎵 모몽이와 꿈찾기 시작!"):
        if name and grade:
            # 클릭 데이터를 기반으로 사운드 출력
            play_sound("bgm.mp4", is_bgm=True)
            
            st.session_state.user_info = {"name": name, "grade": grade}
            st.session_state.page = 'test'
            st.rerun()
        else:
            st.error("이름과 학년을 입력해줘! ( 'ㅅ' )")

# [PAGE 2: 테스트 - 시안 2페이지 구현]
elif st.session_state.page == 'test':
    # 수채화풍 프로그레스 바
    progress = st.session_state.step / len(questions)
    st.markdown(f'<div style="width:100%; background:#f0f2f6; border-radius:10px; height:10px; margin-bottom:20px;"><div style="width:{progress*100}%; background:#FFDEE9; height:10px; border-radius:10px;"></div></div>', unsafe_allow_html=True)
    
    curr_q = questions[st.session_state.step]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # 질문 화면에도 작은 모몽이가 함께 둥실
        st.markdown('<div class="momong-container" style="animation: floating 2s ease-in-out infinite;">', unsafe_allow_html=True)
        if os.path.exists("momong.png"):
            st.image("momong.png", width=100)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {curr_q['q']}")
        
        # 시안처럼 4점 척도 버튼 배치 (예/아니오만 예시 구현)
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("매우 그렇다"):
            play_sound("kkyu.mp3") # 클릭 효과음
            st.session_state.scores[curr_q['type']] += 2
            st.session_state.step += 1
            if st.session_state.step >= len(questions): st.session_state.page = 'result'
            st.rerun()
        if col_btn2.button("그렇지 않다"):
            play_sound("kkyu.mp3") # 클릭 효과음
            st.session_state.step += 1
            if st.session_state.step >= len(questions): st.session_state.page = 'result'
            st.rerun()

# [PAGE 3: 결과 - 시안 3페이지 구현]
elif st.session_state.page == 'result':
    play_sound("twinkle.mp3") # 성공 효과음
    st.balloons()
    st.header(f"🎊 {st.session_state.user_info['name']}님의 꿈 구슬 리포트")
    
    # 시안 3페이지의 오각형 그래프, 꿈 지도 로직 등 (이전 코드와 동일하게 구현)
    st.markdown("### 모몽이가 보여주는 너의 꿈 지도")
    # (결과 분석 및 AI 컨설팅 로직 생략)
