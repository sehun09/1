
import streamlit as st
import calendar
import sqlite3
from datetime import date, datetime

st.set_page_config(
    page_title="보라고등학교 캘린더",
    page_icon="📅",
    layout="wide"
)

# -------------------------
# 데이터베이스
# -------------------------
conn = sqlite3.connect("calendar.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_date TEXT,
    title TEXT,
    memo TEXT,
    done INTEGER DEFAULT 0
)
""")
conn.commit()

# -------------------------
# 학교 학사일정
# -------------------------
events = {
    "2026-03-18": [("학부모 총회", "행사")],
    "2026-03-24": [("전국연합학력평가", "시험")],
    "2026-04-23": [("1차 지필평가", "시험")],
    "2026-04-24": [("1차 지필평가", "시험")],
    "2026-04-27": [("1차 지필평가", "시험")],
    "2026-04-28": [("1차 지필평가", "시험")],
    "2026-05-04": [("재량휴업일", "휴일")],
    "2026-05-05": [("어린이날", "휴일")],
    "2026-05-07": [("전국연합학력평가", "시험")],
    "2026-05-08": [("창의적 체험활동", "행사")],
    "2026-05-22": [("체육한마당", "행사")],
    "2026-06-03": [("지방선거일", "휴일")],
    "2026-06-04": [("모의평가", "시험")],
    "2026-06-24": [("2차 지필평가", "시험")],
    "2026-06-25": [("2차 지필평가", "시험")],
    "2026-06-26": [("2차 지필평가", "시험")],
    "2026-06-29": [("2차 지필평가", "시험")],
    "2026-06-30": [("2차 지필평가", "시험")],
    "2026-07-20": [("여름방학식", "행사")],
    "2026-08-13": [("개학", "행사")],
    "2026-09-02": [("모의평가", "시험")],
    "2026-09-23": [("재량휴업일", "휴일")],
    "2026-09-24": [("추석 연휴", "휴일")],
    "2026-09-25": [("추석 연휴", "휴일")],
    "2026-10-09": [("한글날", "휴일")],
    "2026-10-12": [("1차 지필평가", "시험")],
    "2026-10-13": [("1차 지필평가", "시험")],
    "2026-10-14": [("1차 지필평가", "시험")],
    "2026-10-15": [("1차 지필평가", "시험")],
    "2026-10-20": [("전국연합학력평가", "시험")],
    "2026-11-19": [("수능·재량휴업일", "휴일")],
    "2026-12-09": [("2차 지필평가", "시험")],
    "2026-12-10": [("2차 지필평가", "시험")],
    "2026-12-11": [("2차 지필평가", "시험")],
    "2026-12-14": [("2차 지필평가", "시험")],
    "2026-12-15": [("2차 지필평가", "시험")],
    "2026-12-23": [("동아리 발표회", "행사")],
    "2026-12-24": [("동아리 발표회", "행사")],
    "2027-01-05": [("종업식·졸업식", "행사")]
}

COLORS = {
    "시험": ("#FDE2E2", "#A51C1C"),
    "행사": ("#DCEBFF", "#174EA6"),
    "휴일": ("#FFF0CC", "#875900"),
    "할 일": ("#DDF4E3", "#176B35")
}

# -------------------------
# 디자인
# -------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
}
.main-title {
    background: linear-gradient(110deg,#173B70,#3478C8);
    color: white;
    padding: 25px;
    border-radius: 15px;
}
.main-title h1 {color:white;}
.calendar-day {
    border: 1px solid #dddddd;
    border-radius: 8px;
    padding: 5px;
    min-height: 100px;
}
.event {
    padding: 4px;
    margin-top: 4px;
    border-radius: 5px;
    font-size: 11px;
    overflow-wrap: anywhere;
}
@media (max-width: 700px) {
    .block-container {padding: 1rem 0.5rem;}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title">
<h1>📅 보라고등학교 캘린더</h1>
<p>학교 일정과 나의 할 일을 한곳에서 관리하세요.</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# 월 이동
# -------------------------
if "year" not in st.session_state:
    st.session_state.year = 2026
    st.session_state.month = 3

a, b, c = st.columns([1, 3, 1])

with a:
    if st.button("◀ 이전 달", use_container_width=True):
        st.session_state.month -= 1
        if st.session_state.month == 0:
            st.session_state.month = 12
            st.session_state.year -= 1
        st.rerun()

with b:
    st.markdown(
        f"<h2 style='text-align:center'>"
        f"{st.session_state.year}년 {st.session_state.month}월</h2>",
        unsafe_allow_html=True
    )

with c:
    if st.button("다음 달 ▶", use_container_width=True):
        st.session_state.month += 1
        if st.session_state.month == 13:
            st.session_state.month = 1
            st.session_state.year += 1
        st.rerun()

# -------------------------
# 범례
# -------------------------
legend = st.columns(4)

for col, category in zip(
    legend, ["시험", "행사", "휴일", "할 일"]
):
    bg, fg = COLORS[category]
    with col:
        st.markdown(
            f"<div style='background:{bg};color:{fg};"
            f"padding:8px;border-radius:8px;text-align:center'>"
            f"<b>{category}</b></div>",
            unsafe_allow_html=True
        )

st.write("")

# -------------------------
# 달력
# -------------------------
year = st.session_state.year
month = st.session_state.month

weeks = calendar.Calendar(
    firstweekday=6
).monthdatescalendar(year, month)

header = st.columns(7)

for col, day_name in zip(
    header, ["일", "월", "화", "수", "목", "금", "토"]
):
    with col:
        st.markdown(
            f"<div style='text-align:center;font-weight:bold'>"
            f"{day_name}</div>",
            unsafe_allow_html=True
        )

for week in weeks:
    cols = st.columns(7, gap="small")

    for i, day in enumerate(week):
        with cols[i]:

            if day.month != month:
                st.write("")
                continue

            day_key = day.isoformat()

            st.markdown(
                f"**{day.day}일**",
                unsafe_allow_html=True
            )

            # 학교 일정
            for title, category in events.get(day_key, []):
                bg, fg = COLORS.get(category, ("#eee", "#333"))

                st.markdown(
                    f"<div class='event' "
                    f"style='background:{bg};color:{fg}'>"
                    f"{title}</div>",
                    unsafe_allow_html=True
                )

            # 개인 할 일
            cur.execute(
                "SELECT title, done FROM todos WHERE task_date=?",
                (day_key,)
            )

            for title, done in cur.fetchall():
                mark = "✓" if done else "□"
                bg, fg = COLORS["할 일"]

                st.markdown(
                    f"<div class='event' "
                    f"style='background:{bg};color:{fg}'>"
                    f"{mark} {title}</div>",
                    unsafe_allow_html=True
                )

# -------------------------
# 할 일 추가
# -------------------------
st.divider()
st.header("📝 나의 할 일 관리")

with st.form("add_task", clear_on_submit=True):
    task_date = st.date_input("날짜", value=date.today())
    task_title = st.text_input(
        "할 일",
        placeholder="예: 영어 수행평가 준비"
    )
    memo = st.text_input("메모 (선택)")
    submitted = st.form_submit_button("할 일 추가")

    if submitted:
        if task_title.strip():
            cur.execute(
                "INSERT INTO todos(task_date,title,memo) VALUES(?,?,?)",
                (task_date.isoformat(), task_title.strip(), memo.strip())
            )
            conn.commit()
            st.success("할 일이 추가되었습니다.")
            st.rerun()
        else:
            st.warning("할 일을 입력해 주세요.")

# -------------------------
# 할 일 목록 / 완료 / 삭제
# -------------------------
st.subheader("등록한 할 일")

cur.execute(
    "SELECT id,task_date,title,memo,done FROM todos ORDER BY task_date"
)
tasks = cur.fetchall()

if not tasks:
    st.info("아직 등록한 할 일이 없습니다.")

for task_id, task_date, title, memo, done in tasks:
    with st.container(border=True):
        left, middle, right = st.columns([1, 5, 1])

        with left:
            checked = st.checkbox(
                "완료",
                value=bool(done),
                key=f"done_{task_id}"
            )

        if checked != bool(done):
            cur.execute(
                "UPDATE todos SET done=? WHERE id=?",
                (int(checked), task_id)
            )
            conn.commit()
            st.rerun()

        with middle:
            st.write(
                f"~~{title}~~" if done else f"**{title}**"
            )
            st.caption(task_date)
            if memo:
                st.caption(memo)

        with right:
            if st.button("삭제", key=f"del_{task_id}"):
                cur.execute(
                    "DELETE FROM todos WHERE id=?",
                    (task_id,)
                )
                conn.commit()
                st.rerun()

st.caption(
    "※ 학교 일정은 제공된 학사운영 계획 사진을 바탕으로 입력했습니다. "
    "개인 할 일은 SQLite에 저장됩니다. Streamlit Cloud에서는 "
    "로컬 파일이 재배포·재시작 후 유지된다고 보장할 수 없으므로 "
    "장기 보존에는 외부 데이터베이스 연결을 권장합니다."
)
