
# -------------------------
# 달력 (가로 7칸 × 세로 4~5주)
# -------------------------
year = st.session_state.year
month = st.session_state.month

weeks = calendar.Calendar(
    firstweekday=6
).monthdatescalendar(year, month)

# 요일 표시
header = st.columns(7, gap="small")

for col, day_name in zip(
    header, ["일", "월", "화", "수", "목", "금", "토"]
):
    with col:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold;"
            f"padding:8px 0;'>{day_name}</div>",
            unsafe_allow_html=True
        )

# 날짜 칸
for week in weeks:
    cols = st.columns(7, gap="small")

    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.markdown(
                    "<div style='height:125px;'></div>",
                    unsafe_allow_html=True
                )
                continue

            day_key = day.isoformat()

            with st.container(border=True, height=145):
                st.markdown(
                    f"<div style='font-size:16px;font-weight:bold;'>"
                    f"{day.day}</div>",
                    unsafe_allow_html=True
                )

                # 학교 일정
                for title, category in events.get(day_key, []):
                    bg, fg = COLORS[category]
                    st.markdown(
                        f"<div style='background:{bg};color:{fg};"
                        f"border-radius:5px;padding:3px;"
                        f"margin:3px 0;font-size:11px;'>"
                        f"{title}</div>",
                        unsafe_allow_html=True
                    )

                # 개인 할 일
                cur.execute(
                    "SELECT title, done FROM todos WHERE task_date=?",
                    (day_key,)
                )

                for title, done in cur.fetchall():
                    bg, fg = COLORS["할 일"]
                    mark = "✓" if done else "□"

                    st.markdown(
                        f"<div style='background:{bg};color:{fg};"
                        f"border-radius:5px;padding:3px;"
                        f"margin:3px 0;font-size:11px;'>"
                        f"{mark} {title}</div>",
                        unsafe_allow_html=True
                    )
