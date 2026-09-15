import streamlit as st
import requests
from datetime import date, timedelta

# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="보라고등학교 급식",
    page_icon="🍚",
    layout="centered"
)

# 경기도교육청 / 보라고등학교
ATPT_OFCDC_SC_CODE = "J10"
SD_SCHUL_CODE = "7530882"

# NEIS API 키
# Streamlit Cloud → Settings → Secrets에 입력
try:
    NEIS_API_KEY = st.secrets["NEIS_API_KEY"]
except Exception:
    st.error("NEIS_API_KEY가 설정되어 있지 않습니다.")
    st.info(
        "Streamlit Cloud의 Settings → Secrets에서 "
        "NEIS_API_KEY를 추가해주세요."
    )
    st.stop()

API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


# ==========================================
# 급식 데이터 가져오기
# ==========================================

def get_meal(target_date):
    """특정 날짜의 급식 정보를 NEIS에서 가져옴"""

    date_string = target_date.strftime("%Y%m%d")

    params = {
        "KEY": NEIS_API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_YMD": date_string
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        # 정상적인 급식 데이터
        if "mealServiceDietInfo" in data:

            rows = data["mealServiceDietInfo"][1]["row"]

            return rows

        # NEIS에서 결과가 없는 경우
        if "RESULT" in data:

            code = data["RESULT"].get("CODE", "")
            message = data["RESULT"].get("MESSAGE", "")

            if code == "INFO-200":
                return []

            return None

        return []

    except requests.exceptions.RequestException:
        return None

    except Exception:
        return None


# ==========================================
# 메뉴에서 알레르기 번호 제거
# ==========================================

ALLERGY_INFO = {
    "1": "난류",
    "2": "우유",
    "3": "메밀",
    "4": "땅콩",
    "5": "대두",
    "6": "밀",
    "7": "고등어",
    "8": "게",
    "9": "새우",
    "10": "돼지고기",
    "11": "복숭아",
    "12": "토마토",
    "13": "아황산류",
    "14": "호두",
    "15": "닭고기",
    "16": "쇠고기",
    "17": "오징어",
    "18": "조개류",
    "19": "잣"
}


def format_menu(menu):
    """
    메뉴 문자열을 보기 좋게 변환
    예:
    김치찌개(5.6) → 김치찌개
    """

    items = menu.split("<br/>")

    result = []

    for item in items:
        item = item.strip()

        if not item:
            continue

        # 알레르기 번호 추출
        allergy_numbers = []

        import re

        matches = re.findall(
            r"\(([\d.]+)\)",
            item
        )

        for match in matches:
            for number in match.split("."):
                if number in ALLERGY_INFO:
                    allergy_numbers.append(number)

        # 메뉴명에서 알레르기 번호 제거
        item = re.sub(
            r"\([\d.]+\)",
            "",
            item
        )

        item = item.strip()

        result.append(
            (item, allergy_numbers)
        )

    return result


# ==========================================
# 제목
# ==========================================

st.title("🍚 보라고등학교 급식 메뉴")
st.caption("NEIS 교육정보 개방포털 API를 이용한 급식 정보")

st.divider()


# ==========================================
# 날짜 선택
# ==========================================

today = date.today()

selected_date = st.date_input(
    "📅 급식 날짜를 선택하세요",
    value=today
)

st.write("")


# ==========================================
# 급식 조회
# ==========================================

if st.button(
    "🍽️ 급식 조회",
    use_container_width=True
):

    with st.spinner("급식 정보를 불러오는 중..."):

        meals = get_meal(selected_date)

    if meals is None:

        st.error(
            "급식 정보를 불러오지 못했습니다.\n\n"
            "잠시 후 다시 시도해주세요."
        )

    elif len(meals) == 0:

        st.info(
            f"📅 {selected_date.strftime('%Y년 %m월 %d일')}에는 "
            "등록된 급식 정보가 없습니다."
        )

    else:

        st.success(
            f"📅 {selected_date.strftime('%Y년 %m월 %d일')} 급식"
        )

        for meal in meals:

            meal_name = meal.get(
                "MMEAL_SC_NM",
                "급식"
            )

            menu = meal.get(
                "DDISH_NM",
                ""
            )

            calories = meal.get(
                "CAL_INFO",
                "-"
            )

            nutrients = meal.get(
                "NTR_INFO",
                "-"
            )

            origin = meal.get(
                "ORPLC_INFO",
                "-"
            )

            st.subheader(
                f"🍽️ {meal_name}"
            )

            menu_items = format_menu(menu)

            for item, allergy_numbers in menu_items:

                if allergy_numbers:

                    allergy_text = ", ".join(
                        ALLERGY_INFO[number]
                        for number in allergy_numbers
                    )

                    st.markdown(
                        f"### 🍴 {item}"
                    )

                    st.caption(
                        f"⚠️ 알레르기: {allergy_text}"
                    )

                else:

                    st.markdown(
                        f"### 🍴 {item}"
                    )

            st.divider()

            # 칼로리
            if calories and calories != "-":
                st.write(
                    f"🔥 **칼로리:** {calories}"
                )

            # 영양정보
            if nutrients and nutrients != "-":

                with st.expander("🥗 영양정보 보기"):
                    st.write(nutrients)

            # 원산지
            if origin and origin != "-":

                with st.expander("🌾 원산지 정보 보기"):
                    st.write(origin)


# ==========================================
# 오늘 / 내일 바로가기
# ==========================================

st.divider()

st.subheader("📌 빠른 조회")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "오늘 급식",
        use_container_width=True
    ):

        meals = get_meal(today)

        if meals:

            for meal in meals:

                st.write(
                    f"### 🍽️ {meal.get('MMEAL_SC_NM', '급식')}"
                )

                for item, allergies in format_menu(
                    meal.get("DDISH_NM", "")
                ):

                    st.write(f"• {item}")

                    if allergies:

                        allergy_text = ", ".join(
                            ALLERGY_INFO[a]
                            for a in allergies
                        )

                        st.caption(
                            f"⚠️ 알레르기: {allergy_text}"
                        )

        else:

            st.info("오늘 등록된 급식 정보가 없습니다.")


with col2:

    tomorrow = today + timedelta(days=1)

    if st.button(
        "내일 급식",
        use_container_width=True
    ):

        meals = get_meal(tomorrow)

        if meals:

            for meal in meals:

                st.write(
                    f"### 🍽️ {meal.get('MMEAL_SC_NM', '급식')}"
                )

                for item, allergies in format_menu(
                    meal.get("DDISH_NM", "")
                ):

                    st.write(f"• {item}")

                    if allergies:

                        allergy_text = ", ".join(
                            ALLERGY_INFO[a]
                            for a in allergies
                        )

                        st.caption(
                            f"⚠️ 알레르기: {allergy_text}"
                        )

        else:

            st.info("내일 등록된 급식 정보가 없습니다.")


# ==========================================
# 출처
# ==========================================

st.divider()

st.caption(
    "📌 급식 정보 출처: 나이스 교육정보 개방 포털(NEIS)"
)
