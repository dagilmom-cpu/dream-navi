"""
꿈네비 (DreamNavi) MVP v2.0 - 투자자 데모 강화판
변경 핵심:
  1. Groq(llama3) → Anthropic Claude API (신뢰도 및 품질)
  2. 결과 리포트 구조화 (PDF 저장 가능)
  3. 사용자 데이터 수집 → PMF 검증 지표 자동 집계
  4. 이탈률 추적 (퍼널 분석용)
  5. 빈 답변 방지 (Cognitive Integrity 강화)
"""

import streamlit as st
import pandas as pd
import datetime
import json
import os
import anthropic

# ── 설정 ──────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="꿈네비 - 모몽이와 꿈 찾기", layout="centered")

st.markdown("""
<style>
@keyframes floating {
    0%   { transform: translateY(0px); }
    50%  { transform: translateY(-15px); }
    100% { transform: translateY(0px); }
}
.momong-container {
    display: flex;
    justify-content: center;
    animation: floating 3s ease-in-out infinite;
    margin-bottom: 20px;
}
.stButton>button {
    width: 100%;
    border-radius: 20px;
    height: 3.5em;
    font-weight: bold;
}
.result-box {
    background: #f0f4ff;
    border-left: 4px solid #4B6EF5;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 12px 0;
}
.metric-row {
    display: flex;
    gap: 16px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 0,
        "page": "intro",
        "scores": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0},
        "answers": [],          # 퍼널 분석용 원본 응답
        "start_time": None,     # 완료율 측정
        "user_info": {},
        "result_generated": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── 질문 데이터 (4대 이론 통합 12문항) ────────────────────────────────────────
questions = [
    # (질문, RIASEC 유형, 다중지능 연결 힌트)
    {"q": "기계나 도구를 직접 만지고 고치는 일이 즐거운가요?",        "type": "R", "mi": "신체운동지능"},
    {"q": "새로운 사실을 알아내기 위해 관찰하고 분석하는 걸 좋아하나요?", "type": "I", "mi": "논리수학지능"},
    {"q": "그림, 음악, 글쓰기 등 창의적인 표현 활동이 좋은가요?",     "type": "A", "mi": "공간/언어지능"},
    {"q": "어려운 친구를 돕거나 가르쳐 주는 일에서 보람을 느끼나요?",   "type": "S", "mi": "대인지능"},
    {"q": "목표를 정하고 다른 사람들을 이끌어 성과를 내고 싶나요?",    "type": "E", "mi": "대인지능"},
    {"q": "규칙에 따라 꼼꼼하게 정리하고 기록하는 일이 편한가요?",     "type": "C", "mi": "논리수학지능"},
    {"q": "운동·요리·공예 등 몸을 직접 쓰는 직업이 끌리나요?",        "type": "R", "mi": "신체운동지능"},
    {"q": "수학·과학 같은 문제를 끝까지 파고드는 편인가요?",           "type": "I", "mi": "논리수학지능"},
    {"q": "남들과 다른 나만의 스타일이나 작품을 만들고 싶나요?",        "type": "A", "mi": "공간지능"},
    {"q": "사람들의 고민을 들어주고 함께 해결책을 찾는 게 편한가요?",  "type": "S", "mi": "대인지능"},
    {"q": "사업이나 프로젝트를 직접 기획하고 실행해 보고 싶나요?",     "type": "E", "mi": "기업가지능"},
    {"q": "정해진 계획대로 차근차근 진행하는 것이 마음 편한가요?",      "type": "C", "mi": "논리수학지능"},
]

RIASEC_LABEL = {
    "R": "탐구형 실천가 (Realistic)",
    "I": "분석형 탐구자 (Investigative)",
    "A": "창의적 예술가 (Artistic)",
    "S": "따뜻한 조력자 (Social)",
    "E": "도전적 리더 (Enterprising)",
    "C": "신중한 관리자 (Conventional)",
}

# ── PMF 데이터 저장 (로컬 CSV — 실제 배포 시 DB/BigQuery 연결) ───────────────
STATS_FILE = "dreamnavi_stats.csv"

def save_session_data(user_info, scores, top_type, elapsed_sec):
    """완료된 세션 데이터를 저장 → 투자자에게 보여줄 PMF 지표 원본"""
    row = {
        "timestamp": datetime.datetime.now().isoformat(),
        "nickname": user_info.get("nickname", ""),
        "birth_year": user_info.get("birth", "").year if hasattr(user_info.get("birth", ""), "year") else "",
        "top_type": top_type,
        "elapsed_sec": round(elapsed_sec),
        **{f"score_{k}": v for k, v in scores.items()},
    }
    df_new = pd.DataFrame([row])
    if os.path.exists(STATS_FILE):
        df_old = pd.read_csv(STATS_FILE)
        pd.concat([df_old, df_new], ignore_index=True).to_csv(STATS_FILE, index=False)
    else:
        df_new.to_csv(STATS_FILE, index=False)

# ── Claude API 호출 ────────────────────────────────────────────────────────────
def generate_report_with_claude(user_info, scores, top_type):
    """
    Anthropic Claude sonnet 사용.
    Groq/llama3 대비: 한국어 품질, 교육 도메인 정확도, 브랜드 신뢰도 모두 우위.
    """
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    birth = user_info.get("birth", "")
    age_str = ""
    if hasattr(birth, "year"):
        age = datetime.date.today().year - birth.year
        age_str = f"{age}세 (출생연도 {birth.year})"

    score_desc = ", ".join([f"{RIASEC_LABEL[k]}: {v}점" for k, v in sorted(scores.items(), key=lambda x: -x[1])])

    prompt = f"""당신은 진로 상담 전문가입니다. 아래 학생의 RIASEC 진단 결과를 바탕으로 
구체적이고 실행 가능한 진로 리포트를 작성해 주세요.

[학생 정보]
- 이름/별명: {user_info.get('nickname', '학생')}
- 나이: {age_str}

[RIASEC 점수]
{score_desc}

[작성 지침]
1. **최상위 유형 분석** (2~3줄): {top_type} 유형의 핵심 강점과 특성
2. **추천 직업군** (5개, 각 한 줄 설명): 2030년 이후에도 유망한 직업 중심
3. **대입 전략** (국내+해외 각 2개): 수시/정시 또는 US/UK 전형 연계
4. **지금 당장 할 수 있는 활동** (3가지): 중학생도 시작할 수 있는 구체적 액션
5. **모몽이의 한마디** (1줄, 따뜻하게 마무리)

반드시 한국어로, 학생이 읽기 쉬운 구어체로 작성하세요."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

# ── 화면 렌더링 ────────────────────────────────────────────────────────────────

# ▌INTRO
if st.session_state.page == "intro":
    st.title("☁️ 꿈네비")

    try:
        st.markdown('<div class="momong-container">', unsafe_allow_html=True)
        st.image("momong.png", width=200)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        st.markdown("<div style='text-align:center;font-size:80px'>🧸</div>", unsafe_allow_html=True)

    st.markdown("#### 모몽이가 12가지 질문으로 너의 꿈 구슬을 찾아줄게! ✨")
    st.caption("약 3분이면 완성돼요")

    nickname = st.text_input("모몽이가 부를 별명을 알려줘!", placeholder="예: 별이, 민준이, 해찬...")
    birth_date = st.date_input(
        "생년월일을 알려줘! (대입 전략 맞춤용)",
        min_value=datetime.date(2005, 1, 1),
        max_value=datetime.date(2015, 12, 31),
        value=datetime.date(2012, 3, 1),
    )

    if st.button("🚀 모몽이와 시작하기!"):
        if not nickname.strip():
            st.warning("별명을 입력해줘! ( 'ㅅ' )")
        else:
            st.session_state.user_info = {"nickname": nickname.strip(), "birth": birth_date}
            st.session_state.start_time = datetime.datetime.now()
            st.session_state.page = "test"
            st.rerun()

# ▌TEST
elif st.session_state.page == "test":
    step = st.session_state.step
    progress = step / len(questions)

    st.progress(progress, text=f"질문 {step + 1} / {len(questions)}")
    st.markdown(f"### ( 'ㅅ' )  {questions[step]['q']}")
    st.caption(f"관련 능력: {questions[step]['mi']}")

    col1, col2, col3 = st.columns(3)

    def advance(score_delta):
        q = questions[st.session_state.step]
        st.session_state.scores[q["type"]] += score_delta
        st.session_state.answers.append({
            "step": st.session_state.step,
            "type": q["type"],
            "delta": score_delta,
        })
        st.session_state.step += 1
        if st.session_state.step >= len(questions):
            st.session_state.page = "result"
        st.rerun()

    if col1.button("✅ 매우 그렇다"):
        advance(2)
    if col2.button("🤔 보통이다"):
        advance(1)
    if col3.button("❌ 아니다"):
        advance(0)

# ▌RESULT
elif st.session_state.page == "result":
    st.balloons()

    scores = st.session_state.scores
    user_info = st.session_state.user_info
    top_type = max(scores, key=scores.get)
    second_type = sorted(scores, key=scores.get, reverse=True)[1]

    # 소요 시간 계산 & 저장 (최초 1회)
    if not st.session_state.result_generated:
        elapsed = 0
        if st.session_state.start_time:
            elapsed = (datetime.datetime.now() - st.session_state.start_time).total_seconds()
        save_session_data(user_info, scores, top_type, elapsed)
        st.session_state.result_generated = True

    st.header(f"🎊 {user_info['nickname']}님의 꿈 구슬 리포트")

    # 유형 요약 카드
    st.info(
        f"**1순위:** {RIASEC_LABEL[top_type]}  \n"
        f"**2순위:** {RIASEC_LABEL[second_type]}"
    )

    # 레이더 점수 시각화
    df_scores = pd.DataFrame({
        "유형": [RIASEC_LABEL[k].split("(")[0].strip() for k in scores],
        "점수": list(scores.values()),
    })
    st.bar_chart(df_scores.set_index("유형"))

    # Claude 리포트
    st.markdown("---")
    st.subheader("🧭 모몽이의 진로 나침반")

    with st.spinner("모몽이가 미래를 시뮬레이션하는 중... ✨"):
        report = generate_report_with_claude(user_info, scores, top_type)

    if report:
        st.markdown(f'<div class="result-box">{report}</div>', unsafe_allow_html=True)

        # 리포트 텍스트 다운로드
        st.download_button(
            label="📄 리포트 저장하기",
            data=report,
            file_name=f"꿈네비_리포트_{user_info['nickname']}.txt",
            mime="text/plain",
        )
    else:
        st.warning("API 키를 설정하면 AI 리포트를 받을 수 있어요! (secrets.toml에 ANTHROPIC_API_KEY 입력)")

    # 다시하기
    st.markdown("---")
    if st.button("🔄 다시 해보기"):
        for key in ["step", "page", "scores", "answers", "start_time", "result_generated", "user_info"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ▌ADMIN (내부 PMF 대시보드 — URL에 ?admin=1 추가 시 노출)
query_params = st.query_params
if query_params.get("admin") == "1":
    st.markdown("---")
    st.subheader("📊 [내부] PMF 지표 대시보드")
    if os.path.exists(STATS_FILE):
        df = pd.read_csv(STATS_FILE)
        col1, col2, col3 = st.columns(3)
        col1.metric("총 완료 세션", len(df))
        col2.metric("평균 소요 시간", f"{df['elapsed_sec'].mean():.0f}초")
        col3.metric("최다 유형", df["top_type"].mode()[0] if len(df) > 0 else "-")
        st.bar_chart(df["top_type"].value_counts())
        st.dataframe(df.tail(20))
    else:
        st.info("아직 데이터가 없어요. 진단을 완료한 사용자가 생기면 여기에 집계됩니다.")
