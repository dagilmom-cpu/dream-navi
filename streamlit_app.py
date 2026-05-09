import streamlit as st
import pandas as pd
import base64
import os
import datetime
import plotly.graph_objects as go

# --- [1] UI/UX 극강 처방 (상단 바 박멸 및 여백 제거) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 상단 화이트 바 물리적 제거 (최종 레벨) */
    header, [data-testid="stHeader"] { 
        display: none !important; 
        height: 0 !important;
    }
    
    /* 화면 전체를 위로 강제 밀어올려 상단 바 공간 삭제 */
    .stApp { 
        margin-top: -100px !important; 
        background-image: radial-gradient(at 0% 0%, rgba(255,222,233,0.4) 0, transparent 50%), 
                          radial-gradient(at 100% 100%, rgba(181,255,252,0.4) 0, transparent 50%); 
        background-color: #ffffff;
    }

    .block-container {
        padding-top: 0rem !important;
        max-width: 500px !important;
    }

    /* 2. 모든 요소 강제 중앙 정렬 */
    div[data-testid="stVerticalBlock"] > div {
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
    }

    /* 3. 모몽이 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 0 auto 10px auto;
    }
    
    /* 4. 메인 카드 디자인 */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; text-align: center;
    }
    
    h1 { font-size: 26px !important; font-weight: 700 !important; margin-bottom: 20px !important; color: #1e293b; }
    label { font-size: 15px !important; font-weight: 600 !important; text-align: left !important; width: 100%; display: block !important; margin-top: 15px !important; color: #475569; }
    
    /* 5. 버튼 디자인 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; margin-top: 20px;
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    
    #MainMenu, footer, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 소리 재생 엔진 (브라우저 차단 뚫기용 JS 강제 실행) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "true" if is_bgm else "false"
            # 자바스크립트를 직접 주입하여 오디오 객체 생성 및 재생
            js_code = f"""
                <script>
                var audio = new Audio('data:audio/mp3;base64,{b64}');
                audio.loop = {loop};
                audio.play().catch(function(e) {{ console.log("Sound play blocked"); }});
                </script>
            """
            st.markdown(js_code, unsafe_allow_html=True)

# --- [3] 데이터 및 세션 관리 (무생략 전수 점검) ---
@st.cache_data
def load_db():
    f = "DreamNavi_Job_DB_v2_20240509.xlsx"
    return pd.read_excel(f) if os.path.exists(f) else None

df = load_db()

for key in ['page', 'step', 'scores', 'user_info', 'mind_info']:
    if key not in st.session_state:
        if key == 'scores': st.session_state[key] = {"정보통신":0, "문화/예술":0, "경영/회계":0, "보건/의료":0, "교육/법률":0}
        elif key == 'step': st.session_state[key] = 0
        elif key == 'page': st.session_state[key] = 'intro'
        else: st.session_state[key] = {}

questions = [
    {"q": "컴퓨터 프로그램이나 앱이 어떻게 만들어지는지 궁금하고 직접 만들고 싶니?", "type": "정보통신"},
    {"q": "그림을 그리거나 영상을 편집해서 나만의 작품을 만드는 게 즐겁니?", "type": "문화/예술"},
    {"q": "용돈을 계획적으로 관리하거나 물건을 사고파는 경제 활동에 관심이 있니?", "type": "경영/회계"},
    {"q": "아픈 사람이나 동물을 도와주고 치료하는 일에 보람을 느끼니?", "type": "보건/의료"},
    {"q": "친구들에게 새로운 지식을 알려주거나 법과 규칙을 지키는 게 중요하다고 생각하니?", "type": "교육/법률"},
    {"q": "새로운 스마트 기기가 나오면 먼저 써보고 원리를 파악하는 걸 좋아하니?", "type": "정보통신"},
    {"q": "무대에서 공연하거나 전시회에서 작품을 보여주는 상상을 자주 하니?", "type": "문화/예술"},
    {"q": "복잡한 문제를 효율적으로 해결하기 위해 계획을 세우는 걸 잘하니?", "type": "경영/회계"},
    {"q": "생명과학 실험이나 우리 몸의 구조를 탐구하는 수업이 재미있니?", "type": "보건/의료"},
    {"q": "어려운 처지에 놓인 사람들을 위해 목소리를 내고 돕고 싶니?", "type": "교육/법률"},
    {"q": "방대한 데이터를 분석해서 미래를 예측하는 일이 멋져 보이니?", "type": "정보통신"},
    {"q": "팀 프로젝트를 할 때 창의적인 아이디어를 내서 분위기를 이끄니?", "type": "문화/예술"}
]

# --- [4] 화면 구현 (전수 복구) ---
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<h1>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?")
    birth = st.date_input("생년월일은 언제니?", value=datetime.date(2012, 1, 1))
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학에 관심이 있니?", ["아직은 국내가 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])
    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "birth": birth, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'mind_check':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader(f"✨ {st.session_state.user_info['name']}의 속마음")
    hobby = st.text_input("🌈 생각만 해도 즐거운 취미는 뭐야?")
    good_at = st.text_input("💪 이건 내가 진짜 자신 있다!")
    hard_thing = st.text_area("😟 요즘 너를 힘들게 하는 고민은 뭐야?")
    if st.button("내 마음 전달하기"):
        st.session_state.mind_info = {"hobby": hobby, "good_at": good_at, "hard_thing": hard_thing}
        st.session_state.page = 'test'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    q = questions[st.session_state.step]
    st.markdown(f"### Q{st.session_state.step + 1}. {q['q']}")
    if st.button("매우 그렇다"):
        play_sound("kkyu.mp3")
        st.session_state.scores[q['type']] += 3
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    if st.button("아니다"):
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 결과")
    best = max(st.session_state.scores, key=st.session_state.scores.get)
    if df is not None:
        m = df[df['대분류'] == best].iloc[0] if not df[df['대분류'] == best].empty else df.iloc[0]
        st.success(f"너와 잘 맞는 분야는 [{best}]야!")
        st.info(f"📍 추천 직무: {m['직무군']}")
        st.write(f"🚀 미래 유망 직업: {m['미래유망직업']}")
    if st.button("다시 하기"):
        st.session_state.page = 'intro'
        st.session_state.step = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
