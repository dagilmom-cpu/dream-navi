import streamlit as st
import pandas as pd
import datetime
import base64
import os

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="꿈네비 - 모몽이와 함께하는 미래 여정", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Nanum Gothic', sans-serif; }
    
    .main-card {
        background-color: #ffffff;
        border-radius: 30px;
        padding: 40px;
        box-shadow: 0 10px 50px rgba(0,0,0,0.05);
        border: 1px solid #f9f9f9;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        background-color: #FFDEE9;
        background-image: linear-gradient(0deg, #FFDEE9 0%, #B5FFFC 100%);
        border: none;
        color: #444;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    
    .desc-box {
        background-color: #f8f9fa;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 5px solid #B5FFFC;
    }
    .momong-img { display: flex; justify-content: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 세션 상태 관리 ---
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'user_info' not in st.session_state: st.session_state.user_info = {}
if 'mind_info' not in st.session_state: st.session_state.mind_info = {}

# --- 3. 화면 전환 로직 ---

# [PAGE 1: 환영 및 기본 정보]
if st.session_state.page == 'intro':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("☁️ 안녕! 나는 꿈 가이드 모몽이야")
    st.write("너의 소중한 꿈을 찾기 위해 몇 가지 정보가 필요해.")
    
    name = st.text_input("이름(혹은 별명)을 알려줘")
    col1, col2 = st.columns(2)
    with col1:
        birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1))
    with col2:
        region = st.selectbox("사는 지역", ["수도권", "비수도권", "농어촌(읍/면)", "해외"])
        
    abroad = st.radio("유학에 관심이 있니?", ["관심 없어", "고민 중이야", "꼭 가고 싶어"])
    country = st.text_input("가고 싶은 나라가 있다면 적어줘 (없으면 패스!)")

    if st.button("모몽이와 대화 시작하기"):
        if name:
            st.session_state.user_info = {
                "name": name, "birth": birth, "region": region, 
                "abroad": abroad, "country": country
            }
            st.session_state.page = 'mind_check'
            st.rerun()
        else:
            st.warning("이름을 입력해줘! ( 'ㅅ' )")
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 및 취향 딥다이브]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}, 너의 마음이 궁금해")
    st.write("진지한 테스트 전에, 네가 어떤 사람인지 모몽이에게 들려줄래?")
    
    hobby = st.text_input("🌈 생각만 해도 기분 좋아지는 취미가 뭐야?")
    good_at = st.text_input("💪 이건 내가 좀 잘한다! 하는 게 있을까?")
    dislike = st.text_input("😕 이런 건 정말 하기 싫어! 하는 건?")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하거나 고민인 게 있다면 적어줘. (비밀 보장!)")
    
    if st.button("내 마음 저장하고 다음으로"):
        st.session_state.mind_info = {
            "hobby": hobby, "good_at": good_at, 
            "dislike": dislike, "hard_thing": hard_thing
        }
        st.session_state.page = 'explanation'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 4대 진단 용어 설명]
elif st.session_state.page == 'explanation':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 모몽이의 4가지 분석 구슬")
    st.write("우리는 아래 4가지 과학적 방법으로 너의 미래를 그려볼 거야.")
    
    # 홀랜드 설명
    st.markdown("""<div class="desc-box">
        <b>1. 홀랜드 (흥미 구슬)</b><br>
        네 성격이 어떤 직업 환경과 잘 맞는지 알아보는 거야. (만들기, 탐구하기, 돕기 등)
    </div>""", unsafe_allow_html=True)
    
    # 다중지능 설명
    st.markdown("""<div class="desc-box">
        <b>2. 다중지능 (재능 구슬)</b><br>
        사람마다 잘하는 '똑똑함'의 종류가 달라. 네가 가진 가장 빛나는 재능을 찾아줄게.
    </div>""", unsafe_allow_html=True)
    
    # 게임화 역량 설명
    st.markdown("""<div class="desc-box">
        <b>3. 게임화 역량 (행동 구슬)</b><br>
        문제를 만났을 때 네가 어떻게 행동하는지 게임처럼 분석해. 너의 진짜 해결 능력을 알 수 있지!
    </div>""", unsafe_allow_html=True)
    
    # 미래 역량 설명
    st.markdown("""<div class="desc-box">
        <b>4. 미래 역량 (AI 구슬)</b><br>
        앞으로 올 AI 세상에서 네가 얼마나 준비되어 있는지, 어떤 새로운 힘이 필요한지 확인해.
    </div>""", unsafe_allow_html=True)

    if st.button("좋아, 이제 테스트 시작!"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 테스트 진행 (예시)]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.progress(20) # 진행률 표시
    st.subheader("Q1. 복잡한 기계나 로봇을 직접 조립하는 과정이 즐겁니?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정말 그래"): pass
        if st.button("조금 그래"): pass
    with col2:
        if st.button("별로 안 그래"): pass
        if st.button("전혀 안 그래"): pass
    
    st.write("\n\n")
    st.caption("지금은 로직 확인을 위한 예시 화면이야. 나중에 12문항이 여기 들어갈 거야!")
    if st.button("결과 페이지 미리보기"):
        st.session_state.page = 'result_preview'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 5: 결과 미리보기]
elif st.session_state.page == 'result_preview':
    st.balloons()
    st.title("📋 너를 위한 꿈 지도")
    st.markdown(f"**{st.session_state.user_info['name']}**님, 모몽이가 분석한 너의 모습이야.")
    
    st.info(f"💡 분석 근거: 네가 좋아하는 '{st.session_state.mind_info['hobby']}'와(과) 테스트에서 보여준 논리력을 합쳐보니, 너는 미래의 설계자 스타일이야!")
    
    st.success("📍 국내 추천: 강원 지역인재 전형을 활용한 IT 공학 계열")
    st.warning("🌍 글로벌 추천: 영국 임페리얼 칼리지 스타일의 심화 전공 코스")
    
    if st.button("처음으로 돌아가기"):
        st.session_state.page = 'intro'
        st.rerun()
