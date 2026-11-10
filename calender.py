import streamlit as st
import calendar
from datetime import date

st.set_page_config(
    page_title="보라고등학교 학사일정",
    page_icon="📅",
    layout="wide"
)

# -----------------------------
# 2026학년도 학사일정
# -----------------------------

events = {
    "2026-03-02": [("대체 휴일", "휴일")],
    "2026-03-18": [("학부모 총회", "행사")],
    "2026-03-24": [("전국연합학력평가", "시험")],

    "2026-04-07": [("전국연합학력평가", "시험")],
    "2026-04-23": [("1차 지필평가", "시험")],
    "2026-04-24": [("1차 지필평가", "시험")],
    "2026-04-27": [("1차 지필평가", "시험")],
    "2026-04-28": [("1차 지필평가", "시험")],

    "2026-05-04": [("재량휴업일", "휴일")],
    "2026-05-05": [("어린이날", "휴일")],
    "2026-05-07": [("전국연합학력평가", "시험")],
    "2026-05-08": [("창의적 체험활동", "행사")],
    "2026-05-22": [("체육한마당", "행사")],
    "2026-05-25": [("대체 휴일", "휴일")],

    "2026-06-03": [("지방선거", "휴일")],
    "2026-06-04": [("모의평가 및 전국연합", "시험")],
    "2026-06-24": [("2차 지필평가", "시험")],
    "2026-06-25": [("2차 지필평가", "시험")],
    "2026-06-26": [("2차 지필평가", "시험")],
    "2026-06-29": [("2차 지필평가", "시험")],
    "2026-06-30": [("2차 지필평가", "시험")],

    "2026-07-08": [("전국연합학력평가", "시험")],
    "2026-07-17": [("제헌절", "기념일")],
    "2026-07-20": [("여름방학식", "행사")],

    "2026-08-13": [("개학", "행사")],
    "2026-08-17": [("대체 휴일", "휴일")],

    "2026-09-02": [("모의평가 및 전국연합", "시험")],
    "2026-09-23": [("재량휴업일", "휴일")],
    "2026-09-24": [("추석 연휴", "휴일")],
    "2026-09-25": [("추석 연휴", "휴일")],

    "2026-10-05": [("대체 휴일", "휴일")],
    "2026-10-09": [("한글날", "휴일")],
    "2026-10-12": [("1차 지필평가", "시험")],
    "2026-10-13": [("1차 지필평가", "시험")],
    "2026-10-14": [("1차 지필평가", "시험")],
    "2026-10-15": [("1차 지필평가", "시험")],
    "2026-10-20": [("전국연합학력평가", "시험")],

    "2026-11-19": [("수능 및 재량휴업일", "휴일")],

    "2026-12-09": [("2차 지필평가", "시험")],
    "2026-12-10": [("2차 지필평가", "시험")],
    "2026-12-11": [("2차 지필평가", "시험")],
    "2026-12-14": [("2차 지필평가", "시험")],
    "2026-12-15": [("2차 지필평가", "시험")],
    "2026-12-23": [("동아리 발표회", "행사")],
    "2026-12-24": [("동아리 발표회", "행사")],
    "2026-12-25": [("성탄절", "휴일")],

    "2027-01-01": [("신정", "휴일")],
    "2027-01-05": [("종업식 및 졸업식", "행사")]
}

# -----------------------------
# 색상 설정
# -----------------------------

colors = {
    "시험": "#FFE3E3",
    "행사": "#DCEBFF",
    "휴일": "#FFF0CC",
    "기념일": "#EADFFF"
}

text_colors = {
    "시험": "#C0392B",
    "행사": "#2457A6",
    "휴일": "#986500",
    "기념일": "#7040A0"
}

# -----------------------------
# CSS
# -----------------------------

st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: 800;
    text-align: center;
}
.day-box {
    min-height: 95px;
    padding: 7px;
    border: 1px solid #dddddd;
    border-radius: 9px;
    margin-bottom: 5px;
}
.event {
    padding: 4px;
    border-radius: 5px;
    font-size: 11px;
    margin-top: 4px;
    word-break: keep-all;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 제목
# -----------------------------

st.markdown(
    '<div class="main-title">📅 보라고등학교 학사일정</div>',
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>"
    "2026학년도 학교 일정 안내"
    "</p>",
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# 월 설정
# -----------------------------

if "year" not in st.session_state:
    st.session_state.year = 2026

if "month" not in st.session_state:
    st.session_state.month = 3

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if st.button("◀ 이전 달"):
        if st.session_state.month == 1:
            st.session_state.month = 12
            st.session_state.year -= 1
        else:
            st.session_state.month -= 1
        st.rerun()

with col2:
    st.markdown(
        f"<h2 style='text-align:center;'>"
        f"{st.session_state.year}년 "
        f"{st.session_state.month}월"
        f"</h2>",
        unsafe_allow_html=True
    )

with col3:
    if st.button("다음 달 ▶"):
        if st.session_state.month == 12:
            st.session_state.month = 1
            st.session_state.year += 1
        else:
            st.session_state.month += 1
        st.rerun()

# -----------------------------
# 학기 이동
# -----------------------------

c1, c2 = st.columns(2)

with c1:
    if st.button("1학기"):
        st.session_state.year = 2026
        st.session_state.month = 3
        st.rerun()

with c2:
    if st.button("2학기"):
        st.session_state.year = 2026
        st.session_state.month = 8
        st.rerun()

st.divider()

# -----------------------------
# 일정 범례
# -----------------------------

st.markdown("### 일정 구분")

legend = st.columns(4)

for col, category in zip(
    legend,
    ["시험", "행사", "휴일", "기념일"]
):
    with col:
        st.markdown(
            f"<div style='background:{colors[category]};"
            f"color:{text_colors[category]};"
            f"text-align:center;padding:8px;border-radius:8px;'>"
            f"{category}</div>",
            unsafe_allow_html=True
        )

st.write("")

# -----------------------------
# 달력 출력
# -----------------------------

year = st.session_state.year
month = st.session_state.month

cal = calendar.Calendar(firstweekday=6)
weeks = cal.monthdatescalendar(year, month)

week_names = ["일", "월", "화", "수", "목", "금", "토"]

header = st.columns(7)

for col, name in zip(header, week_names):
    with col:
        st.markdown(
            f"<div style='text-align:center;font-weight:bold;'>"
            f"{name}</div>",
            unsafe_allow_html=True
        )

for week in weeks:

    cols = st.columns(7)

    for i, day in enumerate(week):

        with cols[i]:

            if day.month != month:
                st.write("")
                continue

            key = day.isoformat()
            day_events = events.get(key, [])

            html = f"""
            <div class="day-box">
                <b>{day.day}</b>
            """

            for title, category in day_events:

                html += f"""
                <div class="event"
                style="background:{colors[category]};
                color:{text_colors[category]};">
                {title}
                </div>
                """

            html += "</div>"

            st.markdown(html, unsafe_allow_html=True)

# -----------------------------
# 일정 목록
# -----------------------------

st.divider()
st.subheader("📋 이번 달 주요 일정")

month_events = []

for day_key, items in events.items():

    event_date = date.fromisoformat(day_key)

    if event_date.year == year and event_date.month == month:

        for title, category in items:
            month_events.append(
                (event_date, title, category)
            )

month_events.sort()

if month_events:

    for event_date, title, category in month_events:

        st.markdown(
            f"**{event_date.month}월 {event_date.day}일** "
            f"· {title} "
            f"({category})"
        )

else:
    st.info("이번 달에는 등록된 일정이 없습니다.")

st.divider()

st.caption(
    "자료 출처: 2026학년도 보라고등학교 학사운영 계획"
)
st.caption(
    "※ 실제 학사일정 변경 사항은 학교 공지를 확인하세요."
)
