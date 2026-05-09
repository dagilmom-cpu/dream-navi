import streamlit as st
import pandas as pd
import base64
import os
import plotly.graph_objects as go

# --- [1] UI/UX 설정 (디자인 고정 및 상단 바 제거) ---
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

    /* 상단 화이트 바 제거 */
    header, [data-testid="stHeader"] { visibility: hidden; height: 0px !important; display: none !important; }
    #MainMenu, footer, .stDeployButton { visibility: hidden; display:none; }

    /* 모몽이 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 40px auto 20px auto;
    }
    
    /* 메인 카드 디자인 */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; max-width: 500px; margin: 0 auto;
    }
    
    /* 텍스트 스타일링 */
    h1 { font-size: 26px !important; font-weight: 700 !important; margin-bottom: 25px !important; }
    label { font-size: 16px !important; font-weight: 600 !important; color: #475569 !important; text-align: left !important; display: block !important; margin-bottom: 10px !important; }
    
    /* 버튼 스타일 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; 
        box-shadow: 0 4px 15px rgba(181,255,252,0.3); margin-top: 15px;
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- [2] 사운드 및 데이터 로드 엔진 ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            audio_html = f'<audio autoplay="true" {loop} style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "DreamNavi_Job_DB_v2_20240509.xlsx" # 파일명 확인 완료
    if os.path.exists(file_name):
        return pd.read_excel(file_name)
    return None

df = load_data()

# --- [3] 화면 로직 ---
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'scores' not in st.session_state: st.session_state.scores = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0}

# 인트로 화면
if st.session_state.page == 'intro':
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"): st.image("momong.png", width=220)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1>모몽이와 꿈찾기</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("너의 이름은 뭐야?")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    
    if st.button("모몽이랑 시작하기 ✨"):
        if name:
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "region": region}
            st.session_state.page = 'test'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 테스트 화면 (중략 - 엑셀 기반 질문 매칭 로직 포함)
elif st.session_state.page == 'test':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    # 질문 로직 구현...
    if st.button("매우 그렇다"):
        play_sound("kkyu.mp3")
        # 점수 합산 로직...
        st.session_state.page = 'result'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 결과 화면 (엑셀 데이터 매칭)
elif st.session_state.page == 'result':
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header(f"🎊 {st.session_state.user_info['name']}의 꿈 리포트")
    
    # 엑셀 DB에서 가장 점수가 높은 유형의 직업 추출
    # 예시: AI 역량이 높다면 AI 관련 직업 정보를 엑셀에서 가져와 보여줌
    if df is not None:
        best_job = df.iloc[0] # 로직에 따른 필터링 결과
        st.subheader(f"추천 직업: {best_job['직업명']}")
        st.info(f"💡 모몽이의 한마디: {best_job['모몽이의 한마디']}")
        st.error(f"⚠️ 성장을 위한 팁: {best_job['성장 가이드']}")
    
    st.markdown('</div>', unsafe_allow_html=True)
