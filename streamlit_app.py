import streamlit as st
import pandas as pd
import base64
import os
import plotly.graph_objects as go

# --- [1] UI/UX & 디자인 완벽 고정 (중앙 정렬 및 헤더 제거) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    html, body, [class*="css"] { 
        font-family: 'Pretendard', sans-serif; 
        color: #1e293b; 
        text-align: center !important; 
    }
    
    .stApp { 
        background-color: #ffffff; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
    }

    /* 상단 화이트 바 및 불필요 요소 완전 제거 */
    header, [data-testid="stHeader"] { visibility: hidden; height: 0px !important; display: none !important; }
    #MainMenu, footer, .stDeployButton { visibility: hidden; display:none; }

    /* 모몽이 둥실둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 40px auto 20px auto;
    }
    
    /* 메인 카드 디자인 (중앙 집중형) */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; max-width: 500px; margin: 0 auto;
        text-align: center;
    }
    
    /* 텍스트 및 라벨 크기 밸런스 */
    h1 { font-size: 28px !important; font-weight: 700 !important; margin-bottom: 25px !important; }
    label { font-size: 16px !important; font-weight: 600 !important; color: #475569 !important; text-align: left !important; display: block !important; margin-bottom: 8px !important; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 4em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; 
        box-shadow: 0 4px 15px rgba(181,255,252,0.3); margin-top: 15px;
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 사운드 및 엑셀 데이터 로드 엔진 ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            audio_html = f"""
                <audio id="audio-tag" autoplay="true" {loop} style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>document.getElementById("audio-tag").play();</script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

@st.cache_data
def load_excel_db():
    # 어머님이 보여주신 엑셀 파일명으로 고정
    file_path = "DreamNavi_Job_DB_v2_20240509.xlsx"
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return None

df = load_excel_db()

# --- [3] 세션 상태 초기화 (모든 로직 복구) ---
for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0, "AI":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

# 전략적 12문항 (4대 엔진 기반)
questions = [
    {"q": "기계의 원리를 파악하고 직접 고쳐보는 과정이 즐거운가요?", "type": "R"},
    {"q": "데이터 속에서 논리적인 패턴을 찾아내는 일이 흥미로운가요?", "type": "I"},
    {"q": "새로운 디지털 도구나 AI를 남들보다 먼저 탐구하고 사용해보나요?", "type": "AI"},
    {"q": "친구들의 의견을 조율하고 이끄는 리더 역할을 할 때 보람을 느끼나요?", "type": "S"},
    {"q": "글이나 그림으로 내 생각을 창의적으로 표현하는 것이 좋은가요?", "type": "A"},
    {"q": "정해진 규칙에 따라 꼼꼼하게 업무를 처리하는 환경이 편안한가요?", "type": "C"},
    {"q": "미래 기술 변화가 우리 삶에 줄 영향에 대해 고민해 본 적 있나요?", "type": "AI"},
    {"q": "낯선 환경에서도 빠르게 적응하고 문제를 해결할 수 있나요?", "type": "Game"},
    {"q": "어려운 상황에서 데이터와 직관을 이용해 결정을 내리는 편인가요?", "type": "Game"},
    {"q": "사람들을 돕고 가르치는 활동에서 큰 에너지를 얻나요?", "type": "S"},
    {"q": "하나의 목표를 위해 끈기 있게 파고들어 성과를 내는 편인가요?", "type": "I"},
    {"q": "새로운 프로젝트를 기획하고 널리 알리는 일이 설레나요?", "type": "E"}
]

# --- [4] 화면 단계별 구현 ---

# 1. 인트로 (정보 수집)
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

# 2. 심리 파악 (엄마의 공감)
elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}의 마음 읽기")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민은 뭐야?")
    
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'engine_desc'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. 4대 엔진 설명
elif st.session_state.page == 'engine_desc':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.title("🧪 4가지 진단 구슬")
    st.write("홀랜드(흥미), 재능, 행동, AI 역량을 통해 네 미래 지도를 그릴 거야.")
    if st.button("테스트 시작!"):
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 4. 테스트 진행
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    curr_q = questions[st.session_state.step]
    st.markdown(f"### Q{st.session_state.step + 1}. {curr_q['q']}")
    
    cols = st.columns(2)
    if cols[0].button("매우 그렇다"):
        play_sound("kkyu.mp3")
        st.session_state.scores[curr_q['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    if cols[1].button("아니다"):
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 5. 결과 리포트 (엑셀 데이터 기반)
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 꿈 지도")
    
    # 유형 분석 및 엑셀 데이터 매칭
    best_type = max(st.session_state.scores, key=st.session_state.scores.get)
    
    if df is not None:
        # 어머님이 주신 엑셀 컬럼명(유형)과 best_type 매칭 (예시 로직)
        matched_job = df[df['유형'] == best_type].iloc[0] if not df[df['유형'] == best_type].empty else df.iloc[0]
        
        st.subheader(f"추천 직업: {matched_job['직업명']}")
        st.write(f"🎓 추천 학과: {matched_job['학과']}")
        st.info(f"💡 모몽이의 한마디: {matched_job['모몽이의 한마디']}")
        st.error(f"⚠️ 성장 가이드: {matched_job['성장 가이드']}")
    
    # 오각형 그래프 추가
    categories = list(st.session_state.scores.keys())
    values = list(st.session_state.scores.values())
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#14b8a6'))
    st.plotly_chart(fig)
    
    if st.button("다시 처음으로"):
        st.session_state.page = 'intro'
        st.session_state.step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
