
import streamlit as st
import calendar
import json
import os
from datetime import date, datetime

st.set_page_config(
    page_title="보라고등학교 캘린더",
    page_icon="📅",
    layout="wide"
)

# -----------------------------
# 디자인
# -----------------------------
st.markdown("""
<style>
.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.title-box {
    background: linear-gradient(120deg,#173B70,#4386D6);
    color: white;
    padding: 22px;
    border-radius: 15px;
    margin-bottom: 15px;
}
.title-box h1 {
    color: white;
    margin: 0;
}
.day-box {
    border: 1px solid #dddddd;
    border-radius: 9px;
    padding: 5px;
    min-height: 110px;
}
.event-chip {
    padding: 4px;
    border-radius: 5px;
    margin-top: 4px;
    font-size: 11px;
    overflow-wrap: anywhere;
}
div[data-testid="stButton"] button {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-box">
<h1>📅 보라고등학교 캘린더</h1>
<p>학교 일정과 나의 할 일을 한눈에 관리하세요.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 일정 분류 색상
# -----------------------------
COLORS = {
    "시험": ("#FCE8E6", "#B3261E"),
    "학교행사": ("#E8F0FE", "#174EA6"),
    "휴일": ("#FDECC8", "#8A5300"),
    "기념일": ("#EDE7F6", "#6741A5"),
    "개인일정": ("#E6F4EA", "#137333")
}

# -----------------------------
# 학교 학사일정
# 기존에 확인한 학교 일정
# -----------------------------
DEFAULT_EVENTS = [
    ("2026-03-02", "대체공휴일", "휴일"),
    ("2026-03-18", "학부모 총회", "학교행사"),
    ("2026-03-24", "전국연합학력평가", "시험"),

    ("2026-04-07", "전국연합학력평가", "시험"),
    ("2026-04-23", "1차 지필평가", "시험"),
    ("2026-04-24", "1차 지필평가", "시험"),
    ("2026-04-27", "1차 지필평가", "시험"),
    ("2026-04-28", "1차 지필평가", "시험"),

    ("2026-05-04", "재량휴업일", "휴일"),
    ("2026-05-05", "어린이날", "휴일"),
    ("2026-05-07", "전국연합학력평가", "시험"),
    ("2026-05-08", "창의적 체험활동", "학교행사"),
    ("2026-05-22", "체육한마당", "학교행사"),
    ("2026-05-25", "대체공휴일", "휴일"),

    ("2026-06-03", "지방선거일", "휴일"),
    ("2026-06-04", "모의평가·전국연합학력평가", "시험"),
    ("2026-06-24", "2차 지필평가", "시험"),
    ("2026-06-25", "2차 지필평가", "시험"),
    ("2026-06-26", "2차 지필평가", "시험"),
    ("2026-06-29", "2차 지필평가", "시험"),
    ("2026-06-30", "2차 지필평가", "시험"),

    ("2026-07-08", "전국연합학력평가", "시험"),
    ("2026-07-17", "제헌절", "기념일"),
    ("2026-07-20", "여름방학식", "학교행사"),

    ("2026-08-13", "개학", "학교행사"),
    ("2026-08-17", "대체공휴일", "휴일"),

    ("2026-09-02", "모의평가·전국연합학력평가", "시험"),
    ("2026-09-23", "재량휴업일", "휴일"),
    ("2026-09-24", "추석 연휴", "휴일"),
    ("2026-09-25", "추석 연휴", "휴일"),

    ("2026-10-05", "대체공휴일", "휴일"),
    ("2026-10-09", "한글날", "휴일"),
    ("2026-10-12", "1차 지필평가", "시험"),
    ("2026-10-13", "1차 지필평가", "시험"),
    ("2026-10-14", "1차 지필평가", "시험"),
    ("2026-10-15", "1차 지필평가", "시험"),
    ("2026-10-20", "전국연합학력평가", "시험"),

    ("2026-11-19", "수능·재량휴업일", "휴일"),

    ("2026-12-09", "2차 지필평가", "시험"),
    ("2026-12-10", "2차 지필평가", "시험"),
    ("2026-12-11", "2차 지필평가", "시험"),
    ("2026-12-14", "2차 지필평가", "시험"),
    ("2026-12-15", "2차 지필평가", "시험"),
    ("2026-12-23", "동아리 발표회", "학교행사"),
    ("2026-12-24", "동아리 발표회", "학교행사"),
    ("2026-12-25", "성탄절", "휴일"),

    ("2027-01-01", "신정", "휴일"),
    ("2027-01-05", "종업식·졸업식", "학교행사"),
]

# -----------------------------
# 데이터 저장
# -----------------------------
DATA_FILE = "calendar_data.json"

if "events" not in st.session_state:
    st.session_state.events = [
        {
            "date": d,
            "title": t,
            "category": c,
            "custom": False
        }
        for d, t, c in DEFAULT_EVENTS
    ]

if "todos" not in st.session_state:
    st.session_state.todos = []

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if "events" not in st.session_state:
            st.session_state.events = saved.get("events", [])
        st.session_state.todos = saved.get("todos", [])
    except (OSError, json.JSONDecodeError):
        pass

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "events": st.session_state.events,
            "todos": st.session_state.todos
        }, f, ensure_ascii=False, indent=2)

# -----------------------------
# 날짜 및 월 이동
# -----------------------------
if "year" not in st.session_state:
    st.session_state.year = date.today().year

if "month" not in st.session_state:
    st.session_state.month = date.today().month

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today().isoformat()

def change_month(amount):
    new_month = st.session_state.month + amount
    new_year = st.session_state.year

    if new_month < 1:
        new_month = 12
        new_year -= 1
    elif new_month > 12:
        new_month = 1
        new_year += 1

    st.session_state.month = new_month
    st.session_state.year = new_year

# -----------------------------
# 월 이동 버튼
# -----------------------------
left, center, right = st.columns([1, 3, 1])

with left:
    if st.button("◀ 이전 달", use_container_width=True):
        change_month(-1)
        st.rerun()

with center:
    st.markdown(
        f"<h2 style='text-align:center'>"
        f"{st.session_state.year}년 {st.session_state.month}월"
        f"</h2>",
        unsafe_allow_html=True
    )

with right:
    if st.button("다음 달 ▶", use_container_width=True):
        change_month(1)
        st.rerun()

# -----------------------------
# 범례
# -----------------------------
legend = st.columns(5)

for col, category in zip(
    legend, COLORS.keys()
):
    bg, fg = COLORS[category]
    with col:
        st.markdown(
            f"<div style='background:{bg};color:{fg};"
            f"padding:7px;border-radius:7px;"
            f"text-align:center;font-size:12px'>"
            f"<b>{category}</b></div>",
            unsafe_allow_html=True
        )

st.write("")

# -----------------------------
# 달력 표시
# 가로 7칸, 세로 4~5주
# -----------------------------
year = st.session_state.year
month = st.session_state.month

weeks = calendar.Calendar(
    firstweekday=6
).monthdatescalendar(year, month)

weekdays = ["일", "월", "화", "수", "목", "금", "토"]

header = st.columns(7, gap="small")

for col, name in zip(header, weekdays):
    with col:
        st.markdown(
            f"<div style='text-align:center;font-weight:bold;"
            f"padding:8px'>{name}</div>",
            unsafe_allow_html=True
        )

for week_index, week in enumerate(weeks):
    cols = st.columns(7, gap="small")

    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.markdown(
                    "<div style='height:115px'></div>",
                    unsafe_allow_html=True
                )
                continue

            day_key = day.isoformat()

            day_events = [
                e for e in st.session_state.events
                if e["date"] == day_key
            ]

            selected = (
                day_key == st.session_state.selected_date
            )

            with st.container(border=True, height=145):
                if st.button(
                    f"{day.day}일" + (" ●" if selected else ""),
                    key=f"date_{day_key}",
                    use_container_width=True,
                    type="primary" if selected else "secondary"
                ):
                    st.session_state.selected_date = day_key
                    st.rerun()

                for event in day_events[:3]:
                    bg, fg = COLORS.get(
                        event["category"],
                        ("#eeeeee", "#333333")
                    )

                    title = event["title"]
                    if len(title) > 11:
                        title = title[:10] + "…"

                    st.markdown(
                        f"<div style='background:{bg};color:{fg};"
                        f"padding:4px;border-radius:5px;"
                        f"margin-top:3px;font-size:10px;"
                        f"overflow-wrap:anywhere'>"
                        f"{title}</div>",
                        unsafe_allow_html=True
                    )

                if len(day_events) > 3:
                    st.caption(f"+{len(day_events)-3}개 더")

# -----------------------------
# 선택한 날짜 일정
# -----------------------------
st.divider()

selected_date = st.session_state.selected_date
selected_obj = datetime.strptime(
    selected_date, "%Y-%m-%d"
).date()

st.subheader(
    f"🗓️ {selected_obj.year}년 "
    f"{selected_obj.month}월 {selected_obj.day}일"
)

selected_events = [
    e for e in st.session_state.events
    if e["date"] == selected_date
]

if selected_events:
    for index, event in enumerate(selected_events):
        bg, fg = COLORS.get(
            event["category"],
            ("#eeeeee", "#333333")
        )

        st.markdown(
            f"<div style='background:{bg};color:{fg};"
            f"padding:10px;border-radius:8px;margin:5px 0'>"
            f"<b>{event['category']} · {event['title']}</b>"
            f"</div>",
            unsafe_allow_html=True
        )

        if event.get("custom", False):
            if st.button(
                "삭제",
                key=f"delete_event_{index}"
            ):
                st.session_state.events.remove(event)
                save_data()
                st.rerun()
else:
    st.info("등록된 일정이 없습니다.")

# -----------------------------
# 일정 직접 추가
# -----------------------------
st.divider()
st.header("➕ 일정 직접 추가하기")

with st.form("event_form", clear_on_submit=True):
    event_date = st.date_input(
        "일정 날짜",
        value=selected_obj
    )

    event_title = st.text_input(
        "일정 이름",
        placeholder="예: 과학 수행평가 제출"
    )

    event_category = st.selectbox(
        "일정 종류",
        list(COLORS.keys())
    )

    event_note = st.text_input(
        "메모",
        placeholder="추가 설명 (선택)"
    )

    add_event = st.form_submit_button(
        "일정 등록",
        use_container_width=True
    )

    if add_event:
        if event_title.strip():
            st.session_state.events.append({
                "date": event_date.isoformat(),
                "title": event_title.strip(),
                "category": event_category,
                "note": event_note.strip(),
                "custom": True
            })

            save_data()
            st.session_state.selected_date = event_date.isoformat()
            st.session_state.year = event_date.year
            st.session_state.month = event_date.month

            st.success("일정이 등록되었습니다.")
            st.rerun()
        else:
            st.warning("일정 이름을 입력해 주세요.")

# -----------------------------
# 개인 할 일
# -----------------------------
st.divider()
st.header("📝 나의 할 일")

with st.form("todo_form", clear_on_submit=True):
    todo_date = st.date_input(
        "할 일 날짜",
        value=selected_obj,
        key="todo_date"
    )

    todo_title = st.text_input(
        "할 일 내용",
        placeholder="예: 영어 단어 외우기"
    )

    add_todo = st.form_submit_button(
        "할 일 추가",
        use_container_width=True
    )

    if add_todo:
        if todo_title.strip():
            st.session_state.todos.append({
                "date": todo_date.isoformat(),
                "title": todo_title.strip(),
                "done": False
            })
            save_data()
            st.success("할 일이 추가되었습니다.")
            st.rerun()
        else:
            st.warning("할 일을 입력해 주세요.")

# -----------------------------
# 할 일 목록
# -----------------------------
st.subheader("할 일 목록")

for index, todo in enumerate(st.session_state.todos):
    col1, col2, col3 = st.columns([1, 5, 1])

    with col1:
        checked = st.checkbox(
            "완료",
            value=todo["done"],
            key=f"todo_{index}"
        )

        if checked != todo["done"]:
            todo["done"] = checked
            save_data()
            st.rerun()

    with col2:
        title = todo["title"]
        if todo["done"]:
            st.markdown(f"~~{title}~~")
        else:
            st.write(f"**{title}**")

        st.caption(todo["date"])

    with col3:
        if st.button("삭제", key=f"remove_{index}"):
            st.session_state.todos.pop(index)
            save_data()
            st.rerun()

st.caption(
    "※ 학교 학사일정은 기존에 확인한 학사운영 계획을 바탕으로 입력했습니다. "
    "학교 공지와 최종 대조해 주세요. "
    "Streamlit Cloud의 로컬 파일은 재배포 후 보존이 보장되지 않습니다."
)
