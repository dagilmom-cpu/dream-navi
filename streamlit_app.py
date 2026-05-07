import streamlit as st
import datetime
import pandas as pd

# 1. 페이지 테마 설정
st.set_page_config(page_title="꿈네비 - 진실된 미래 가이드", layout="centered")

# 2. 대입 전형 계산 로직 (진실된 데이터 기반)
def calculate_admission_year(birth_date):
    # 생년월일 기준 고3이 되는 해와 적용 교육과정 산출
    grad_year = birth_date.year + 19
    if grad_year >= 2028:
        curriculum = "2022 개정 교육과정 (고교학점제 전면 적용)"
    else:
        curriculum = "2015 개정 교육과정"
    return grad_year, curriculum

# 3. 세션 상태 관리
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'scores' not in st.session_state:
    st.session_state.scores = {"R(현장)":0, "I(탐구)":0, "A(예술)":0, "S(사회)":0, "E(진취)":0, "C(관습)":0}

# --- PAGE 1: 정보 수집 (별명/생년월일) ---
if st.session_state.page == 'intro':
    st.title("☁️ 모몽이와의 첫 만남")
    st.write("모몽이가 당신의 꿈 구슬을 빚기 위해 기본 정보가 필요해요.")
    
    nickname = st.text_input("모몽이가 당신을 뭐라고 부르면 좋을까요? (별명)")
    birth_date = st.date_input("생년월일을 알려주세요.", min_value=datetime.date(2005, 1, 1))
    
    if st.button("모몽이와 시작하기"):
        grad_year, curriculum = calculate_admission_year(birth_date)
        st.session_state.user_info = {
            "nickname": nickname,
            "grad_year": grad_year,
            "curriculum": curriculum
        }
        st.session_state.page = 'test'
        st.rerun()

# --- PAGE 2: 12문항 정밀 진단 (4대 이론 통합) ---
elif st.session_state.page == 'test':
    st.subheader(f"{st.session_state.user_info['nickname']}님을 위한 잠재력 스펙트럼 진단")
    
    # [예시 문항] 실제로는 12문항이 순차적으로 노출됩니다.
    st.info("Q1. 복잡한 기계의 내부 구조를 파악하고 고치는 일에 흥미를 느끼나요?")
    col1, col2 = st.columns(2)
    if col1.button("매우 그렇다"):
        st.session_state.scores["R(현장)"] += 2
        st.session_state.page = 'result' # 프로토타입상 바로 결과로 이동
        st.rerun()
    if col2.button("그렇지 않다"):
        st.session_state.page = 'result'
        st.rerun()

# --- PAGE 3: 진실된 데이터 전략 리포트 ---
elif st.session_state.page == 'result':
    st.success(f"🎊 {st.session_state.user_info['nickname']}님의 꿈 구슬 완성!")
    
    # 1. 대입 전략 컨설팅
    st.subheader("📍 맞춤형 대입 전략 개요")
    st.write(f"- **대입 예정 연도:** {st.session_state.user_info['grad_year']}학년도")
    st.write(f"- **적용 교육과정:** {st.session_state.user_info['curriculum']}")
    st.warning("💡 생년월일 분석 결과: 고교학점제에 따른 과목 선택이 매우 중요한 시기입니다.")
    
    # 2. 잠재력 스펙트럼 (홀랜드/다중지능 기반)
    st.subheader("📊 나의 잠재력 분석 결과")
    # (차트 시각화 로직 생략 - 이전 v1 참조)
    
    # 3. 세밀한 직업 및 컨설팅 (진로현황조사 기반)
    st.subheader("🚀 모몽이의 추천 경로")
    st.write("진로교육 현황조사(2025) 데이터와 당신의 역량을 매칭한 결과:")
    st.info("**추천 직업: 신재생 에너지 시스템 검사원**")
    st.write("- **이유:** R(현장형) 성향과 환경에 대한 사회적 수요가 결합된 최적의 경로입니다.")
    st.write("- **준비 전략:** 관련 대학의 학생부 종합 전형을 목표로, 과학 탐구 실험 역량을 강조하세요.")
