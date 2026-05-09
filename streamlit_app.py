import streamlit as st
import pandas as pd
import datetime
import base64
import os

# --- 1. 프리미엄 UI/UX 설정 (디자인 & 정렬 고정) ---
st.set_page_config(page_title="꿈네비", layout="centered")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');
    
    /* 1. 전체 중앙 정렬 및 폰트 */
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

    /* 2. 상단 하얀 바 완전 제거 */
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none; }
    
    /* 3. 모몽이 중앙 배치 및 둥실 애니메이션 */
    @keyframes floating { 0% { transform: translateY(0px); } 50% { transform: translateY(-15px); } 100% { transform: translateY(0px); } }
    .momong-center { 
        display: flex; justify-content: center; 
        animation: floating 2.5s ease-in-out infinite; 
        margin: 50px auto 20px auto;
    }
    
    /* 4. 메인 카드 디자인 (폭 조절 및 중앙 배치) */
    .main-card { 
        background: rgba(255, 255, 255, 0.9); border-radius: 30px; 
        padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); 
        border: 1px solid #f1f5f9; width: 100%; max-width: 480px; margin: 0 auto;
    }
    
    /* 5. 텍스트 크기 조절 */
    h1 { font-size: 28px !important; font-weight: 700 !important; margin-bottom: 30px !important; }
    label { font-size: 16px !important; font-weight: 600 !important; color: #475569 !important; text-align: left !important; display: block !important; margin-bottom: 8px !important; }
    
    /* 6. 버튼 디자인 */
    .stButton>button { 
        width: 100%; border-radius: 50px; height: 3.8em; font-weight: bold; font-size: 17px;
        background: linear-gradient(135deg, #B5FFFC 0%, #dfffff 100%); 
        border: none; color: #334155; transition: 0.3s; 
        box-shadow: 0 4px 15px rgba(181,255,252,0.4); margin-top: 20px;
    }
    .stButton>button:hover { background: #FFDEE9; transform: scale(1.02); box-shadow: 0 6px 20px rgba(255,222,233,0.6); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사운드 재생 엔진 (중요: HTML + JS 방식) ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            loop = "loop" if is_bgm else ""
            # 브라우저 차단을 뚫기 위한 오디오 태그 생성
            audio_html = f"""
                <audio id="audio-player" autoplay="true" {loop} style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById("audio-player");
                    audio.play();
                </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

# --- 3. 화면 구현 (인트로 화면) ---
if 'page' not in st.session_state: st.session_state.page = 'intro'

if st.session_state.page == 'intro':
    # 모몽이 중앙 정렬
    st.markdown('<div class="momong-center">', unsafe_allow_html=True)
    if os.path.exists("momong.png"):
        st.image("momong.png", width=200)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<h1>모몽이와 첫 만남</h1>", unsafe_allow_html=True)
    
    # 메인 카드
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    name = st.text_input("안녕! 너의 이름은 뭐야?", placeholder="별명을 적어줘도 좋아!")
    region = st.selectbox("어디에 살고 있니?", ["수도권", "비수도권", "농어촌(읍/면 단위)", "해외"])
    abroad = st.radio("유학을 가보고 싶니?", ["국내 대학이 좋아", "고민 중이야", "응! 세계로 나가고 싶어"])

    if st.button("모몽이와 꿈찾기 시작! ✨"):
        if name:
            # 버튼 클릭 시점에 사운드 엔진 가동
            play_sound("bgm.mp4", is_bgm=True)
            st.session_state.user_info = {"name": name, "region": region, "abroad": abroad}
            st.session_state.page = 'mind_check'
            st.rerun()
        else:
            st.error("이름을 입력해줘! ( 'ㅅ' )")
    st.markdown('</div>', unsafe_allow_html=True)
