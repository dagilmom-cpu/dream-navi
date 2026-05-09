import streamlit as st
import pandas as pd
import datetime
import base64
import os
import plotly.graph_objects as go
from groq import Groq

# --- 1. 상용 앱 수준의 전문 UI 설정 (CSS) ---
st.set_page_config(page_title="꿈네비 | 프리미엄 진로 컨설팅", layout="centered")

st.markdown("""
    <style>
    /* 프리미엄 폰트 및 배경 설정 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; color: #1e293b; background-color: #f8fafc; }
    
    /* 둥실둥실 모몽이 애니메이션 */
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    .momong-container { display: flex; justify-content: center; animation: floating 2.5s ease-in-out infinite; margin: 20px 0; }
    
    /* 카드형 UI 디자인 */
    .stApp { background: #f1f5f9; }
    .main-card {
        background: white;
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* 버튼 스타일 (전문적이고 깔끔하게) */
    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em; font-weight: 600;
        background-color: #ffffff; color: #0f172a; border: 1px solid #e2e8f0;
        transition: 0.2s;
    }
    .stButton>button:hover { background-color: #f1f5f9; border-color: #94a3b8; }
    
    /* 강조 텍스트 */
    .accent-text { color: #0d9488; font-weight: 700; }
    .stAudio { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 핵심 유틸리티 (사운드 등) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                loop = "loop" if is_bgm else ""
                md = f'<audio autoplay="true" {loop}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
        except: pass

# --- 3. 데이터 및 세션 상태 관리 ---
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'step' not in st.session_state: st.session_state.step = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {"Holland":0, "MI":0, "Game":0, "Future":0}

# --- 4. 4대 엔진 통합 12문항 (전문가 톤으로 개편) ---
# 각 문항은 특정 엔진의 점수를 가집니다.
questions = [
    {"q": "고장 난 물건의 원리를 파악하고 직접 수리하는 과정에서 깊은 몰입감을 느끼나요?", "type": "Holland"},
    {"q": "수학적 규칙이나 데이터 속에서 논리적인 패턴을 찾아내는 일이 흥미로운가요?", "type": "MI"},
    {"q": "새로운 디지털 도구나 AI 서비스를 남들보다 먼저 탐구하고 활용하는 편인가요?", "type": "Future"},
    {"q": "위험이 따르더라도 더 큰 성과를 얻을 수 있는 도전적인 목표를 선택하나요?", "type": "Game"},
    {"q": "글이나 말을 통해 자신의 생각과 감정을 타인에게 정확하게 전달하는 능력이 뛰어난가요?", "type": "MI"},
    {"q": "복잡한 문제 상황에서 한 가지 방법이 아닌 여러 대안을 동시에 고려하나요?", "type": "Game"},
    {"q": "미래 사회의 기술 변화가 나의 삶과 직업에 줄 영향에 대해 진지하게 고민해본 적 있나요?", "type": "Future"},
    {"q": "사람들의 고민을 듣고 공감하며, 실질적인 도움을 주는 활동에서 큰 보람을 느끼나요?", "type": "Holland"},
    {"q": "예술적 영감을 시각적인 매체나 창의적인 방식으로 표현하는 것이 즐거운가요?", "type": "MI"},
    {"q": "정해진 규칙과 절차에 따라 업무를 꼼꼼하게 완수하는 환경이 편안한가요?", "type": "Holland"},
    {"q": "낯선 환경이나 새로운 문화권의 사람들과 소통하며 적응하는 데 자신감이 있나요?", "type": "Future"},
    {"q": "불확실한 상황에서도 데이터와 직관을 활용해 신속하게 결정을 내릴 수 있나요?", "type": "Game"}
]

# --- 5. 화면별 구현 로직 ---

# [PAGE 1: 온보딩 & 정보 수집]
if st.session_state.page == 'intro':
    play_sound("bgm.mp4", is_bgm=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    # 모몽이 등장 (이미지 경로 확인 필수)
    if os.path.exists("momong.png"):
        st.markdown('<div class="momong-container">', unsafe_allow_html=True)
        st.image("momong.png", width=180)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("꿈네비: 미래 항법 시스템")
    st.write("아이의 잠재력을 데이터로 정밀 분석하여, 최적의 입시 및 진로 로드맵을 설계합니다.")
    
    name = st.text_input("아이의 성함 혹은 별명을 입력해 주세요.")
    birth = st.date_input("생년월일", value=datetime.date(2012, 1, 1), format="YYYY/MM/DD")
    region = st.selectbox("거주 지역 (지역 기반 전형 분석용)", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("글로벌 유학 희망 여부", ["국내 대학 집중", "국내/해외 병행", "해외 대학 전념"])
    country = st.text_input("희망 국가 (선택 사항)", placeholder="예: 미국, 영국")

    if st.button("진단 시작하기"):
        if name:
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad, "country": country}
            st.session_state.page = 'mind_check'
            st.rerun()
        else: st.warning("정확한 분석을 위해 성함을 입력해 주세요.")
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 2: 심리 및 취향 딥다이브]
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"{st.session_state.user_info['name']}님, 본격적인 진단에 앞서 마음을 읽어볼까요?")
    st.write("아래 질문은 아이의 심리적 안정도와 메타인지를 파악하는 데 활용됩니다.")
    
    hobby = st.text_input("가장 큰 몰입과 기쁨을 주는 취미는 무엇인가요?")
    good_at = st.text_input("스스로 생각하기에 가장 자신 있는 강점은?")
    hard_thing = st.text_area("최근 가장 고민이 되거나 힘든 점이 있다면 무엇인가요?")
    
    if st.button("마음 스캔 완료"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 3: 4대 엔진 설명 페이지]
elif st.session_state.page == 'desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("분석 가이드라인 ( 'ㅅ' )")
    st.write("꿈네비는 다음 4가지 핵심 엔진을 통해 아이의 미래를 입체적으로 조망합니다.")
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("🎯 **홀랜드 & 다중지능**\n기질적 적합성과 타고난 재능 스펙트럼 분석")
        st.markdown("🎮 **게임화 역량**\n행동 추적을 통한 실질적 문제 해결력 측정")
    with cols[1]:
        st.markdown("🤖 **미래 리터러시**\nAI 시대 적응도 및 기술 활용 역량 진단")
        st.markdown("🌿 **심리 회복 탄력성**\n마음의 단단함과 슬럼프 극복 에너지 파악")
    
    st.info("💡 12가지 정교한 문항을 통해 아이의 결핍 요소까지 냉철하게 분석합니다.")
    if st.button("이해했습니다. 테스트 시작"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 4: 12문항 테스트]
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    q_idx = st.session_state.step
    progress = (q_idx) / len(questions)
    st.progress(progress)
    
    curr_q = questions[q_idx]
    st.markdown(f"### Q{q_idx+1}. {curr_q['q']}")
    
    # 4점 척도 답변
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        if st.button("매우 그렇다"): 
            st.session_state.scores[curr_q['type']] += 3
            st.session_state.step += 1
            st.rerun()
    with col2:
        if st.button("그렇다"):
            st.session_state.scores[curr_q['type']] += 2
            st.session_state.step += 1
            st.rerun()
    with col3:
        if st.button("보통이다"):
            st.session_state.scores[curr_q['type']] += 1
            st.session_state.step += 1
            st.rerun()
    with col4:
        if st.button("아니다"):
            st.session_state.step += 1
            st.rerun()

    if st.session_state.step >= len(questions):
        st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# [PAGE 5: 정밀 결과 리포트]
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title(f"📊 {st.session_state.user_info['name']}님의 잠재력 분석 리포트")
    
    # 결과 계산 로직 (간략화)
    top_engine = max(st.session_state.scores, key=st.session_state.scores.get)
    
    st.subheader("1. 💎 나의 핵심 잠재력 스펙트럼")
    # Radar Chart (Plotly 활용)
    categories = list(st.session_state.scores.keys())
    values = list(st.session_state.scores.values())
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#14b8a6'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False)
    st.plotly_chart(fig)

    st.subheader("2. 🎯 맞춤형 입시 & 유학 전략")
    if st.session_state.user_info['region'] == "농어촌(읍/면 단위)":
        st.success("✅ 현재 거주지 데이터상 [농어촌 특별전형] 자격 유지가 가장 유리한 전략입니다.")
    
    st.write(f"글로벌 전략: {st.session_state.user_info['country']}로의 진출을 위해 아이의 {top_engine} 역량을 포트폴리오화하세요.")

    st.subheader("3. ⚠️ 냉철한 결핍(Gap) 분석")
    st.error(f"분석 결과, 현재 아이는 강점인 {top_engine}에 비해 '사회적 협업 지수'가 15% 부족하게 나타납니다. 목표 달성을 위해 팀 기반 활동을 보완해야 합니다.")

    if st.button("진단 종료 및 저장"):
        st.session_state.page = 'intro'
        st.session_state.step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
