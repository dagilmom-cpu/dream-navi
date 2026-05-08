import streamlit as st
import pandas as pd
import datetime
import base64
import os
from groq import Groq

# --- 1. 초기 설정 및 CSS (모몽이 둥실 모션 + UI 한글화) ---
st.set_page_config(page_title="꿈네비 - 모몽이와 꿈 찾기", layout="centered")

# CSS: 둥실둥실 애니메이션 및 한글 폰트 최적화
st.markdown("""
    <style>
    @keyframes floating {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    .momong-container {
        display: flex; justify-content: center;
        animation: floating 2.5s ease-in-out infinite;
        margin: 30px 0;
    }
    .stButton>button { width: 100%; border-radius: 25px; height: 3.5em; font-weight: bold; background-color: #f0f2f6; }
    .stAudio { display: none; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사운드 재생 함수 ---
def play_sound(file_path, is_bgm=False):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                loop = "loop" if is_bgm else ""
                md = f'<audio autoplay="true" {loop}><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
                st.markdown(md, unsafe_allow_html=True)
        except Exception:
            pass

# --- 3. 세션 상태 관리 ---
if 'step' not in st.session_state: st.session_state.step = 0
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'scores' not in st.session_state:
    st.session_state.scores = {"R":0, "I":0, "A":0, "S":0, "E":0, "C":0}

# --- 4. 질문지 데이터 (12문항) ---
questions = [
    {"q": "기계나 도구를 직접 만지고 고치는 일이 즐거운가요? (R)", "type": "R"},
    {"q": "새로운 사실을 알아내기 위해 관찰하고 분석하는 걸 좋아하나요? (I)", "type": "I"},
    {"q": "예술적인 활동이나 창의적인 아이디어 내는 걸 좋아하나요? (A)", "type": "A"},
    {"q": "어려운 친구를 돕거나 가르쳐주는 일에서 보람을 느끼나요? (S)", "type": "S"},
    {"q": "목표를 정하고 다른 사람들을 이끌어 성과를 내고 싶나요? (E)", "type": "E"},
    {"q": "규칙에 따라 꼼꼼하게 정리하고 기록하는 일이 편한가요? (C)", "type": "C"},
    {"q": "운동이나 야외 활동 등 몸을 움직이는 직업이 끌리나요? (R)", "type": "R"},
    {"q": "수학이나 과학 같은 과제 해결에 몰입하는 편인가요? (I)", "type": "I"},
    {"q": "남들과 다른 나만의 독특한 옷이나 소품을 선호하나요? (A)", "type": "A"},
    {"q": "사람들의 고민을 들어주고 상담해주는 게 편한가요? (S)", "type": "S"},
    {"q": "사업을 하거나 무언가를 팔아보고 싶다는 생각을 하나요? (E)", "type": "E"},
    {"q": "정해진 시간표대로 움직이는 것이 마음 편한가요? (C)", "type": "C"}
]

# --- 5. 화면 구현 로직 ---

# [PAGE 1: 정보수집 - 한글 날짜 버전]
if st.session_state.page == 'intro':
    play_sound("bgm.mp4", is_bgm=True)
    st.title("☁️ 꿈네비")
    
    if os.path.exists("momong.png"):
        st.markdown('<div class="momong-container">', unsafe_allow_html=True)
        st.image("momong.png", width=220)
        st.markdown('</div>', unsafe_allow_html=True)
    
    nickname = st.text_input("모몽이가 부를 별명을 알려줘!", placeholder="예: 미래의박사")
    
    # 날짜 한글화 및 범위 설정
    today = datetime.date.today()
    birth_date = st.date_input(
        "생년월일을 선택해줘! ( 'ㅅ' )",
        value=datetime.date(2010, 1, 1),
        min_value=datetime.date(1990, 1, 1),
        max_value=today,
        help="달력에서 연도와 월을 선택할 수 있어!"
    )
    
    if st.button("🎵 음악과 함께 시작하기!"):
        if nickname:
            st.session_state.user_info = {"nickname": nickname, "birth": birth_date}
            st.session_state.page = 'test'
            st.rerun()
        else:
            st.error("별명을 입력해줘야 모몽이가 출발할 수 있어! ( 'ㅅ' )")

# [PAGE 2: 12문항 테스트]
elif st.session_state.page == 'test':
    progress = st.session_state.step / len(questions)
    st.progress(progress)
    
    curr_q = questions[st.session_state.step]
    st.markdown(f"### ( 'ㅅ' ) : {curr_q['q']}")
    
    col1, col2 = st.columns(2)
    if col1.button("매우 그렇다"):
        play_sound("kkyu.mp3")
        st.session_state.scores[curr_q['type']] += 2
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()
    if col2.button("그렇지 않다"):
        play_sound("kkyu.mp3")
        st.session_state.step += 1
        if st.session_state.step >= len(questions): st.session_state.page = 'result'
        st.rerun()

# [PAGE 3: 결과 리포트]
elif st.session_state.page == 'result':
    play_sound("twinkle.mp3")
    st.balloons()
    st.header(f"🎊 {st.session_state.user_info['nickname']}님의 꿈 구슬 리포트")
    
    excel_file = "DreamNavi_Job_DB_v2_Ethical.xlsx"
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        top_type = max(st.session_state.scores, key=st.session_state.scores.get)
        st.success(f"모몽이 분석 결과: 당신은 **[{top_type}]** 유형의 강점이 뚜렷해!")
    
    if st.secrets.get("GROQ_API_KEY"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.spinner('모몽이가 미래를 시뮬레이션 중...'):
            try:
                # 생년월일을 바탕으로 나이 계산 등을 포함한 프롬프트
                prompt = f"{st.session_state.user_info['nickname']}({st.session_state.user_info['birth']}년생) 학생은 {st.session_state.scores} 역량을 가졌어. 진실된 데이터에 기반해 대입 전략과 직업 조언을 해줘."
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                )
                st.markdown(response.choices[0].message.content)
            except:
                st.write("모몽이가 생각에 잠겼어. 잠시 후 다시 확인해줘!")
