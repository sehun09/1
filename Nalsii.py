import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="보라고등학교 날씨",
    page_icon="🌤️",
    layout="centered"
)

# 보라고등학교 NEIS 정보
ATPT_OFCDC_SC_CODE = "J10"
SD_SCHUL_CODE = "7530882"

# 보라고등학교 위치
# NEIS 학교정보에서 확인되는 위치를 사용하도록 구성
# 필요하면 아래 좌표만 수정하면 됨.
SCHOOL_LAT = 37.3
SCHOOL_LON = 127.0

KST = ZoneInfo("Asia/Seoul")


# =========================================================
# 페이지 스타일
# =========================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #666666;
        margin-bottom: 25px;
    }

    .weather-card {
        padding: 25px;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #eaf4ff,
            #ffffff
        );
        border: 1px solid #dcecff;
        text-align: center;
        margin-bottom: 20px;
    }

    .temperature {
        font-size: 58px;
        font-weight: 800;
        margin: 10px 0;
    }

    .weather-icon {
        font-size: 65px;
    }

    .info-card {
        padding: 18px;
        border-radius: 15px;
        background-color: #f8f9fa;
        border: 1px solid #eeeeee;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 날씨 코드 → 설명
# =========================================================

def weather_description(code):

    weather = {
        0: ("맑음", "☀️"),
        1: ("대체로 맑음", "🌤️"),
        2: ("부분적으로 흐림", "⛅"),
        3: ("흐림", "☁️"),

        45: ("안개", "🌫️"),
        48: ("서리 안개", "🌫️"),

        51: ("약한 이슬비", "🌦️"),
        53: ("이슬비", "🌦️"),
        55: ("강한 이슬비", "🌧️"),

        61: ("약한 비", "🌧️"),
        63: ("비", "🌧️"),
        65: ("강한 비", "🌧️"),

        71: ("약한 눈", "🌨️"),
        73: ("눈", "❄️"),
        75: ("강한 눈", "❄️"),

        80: ("약한 소나기", "🌦️"),
        81: ("소나기", "🌦️"),
        82: ("강한 소나기", "⛈️"),

        95: ("뇌우", "⛈️"),
        96: ("우박을 동반한 뇌우", "⛈️"),
        99: ("강한 뇌우", "⛈️")
    }

    return weather.get(
        code,
        ("날씨 정보 없음", "❓")
    )


# =========================================================
# 날씨 데이터
# =========================================================

@st.cache_data(ttl=600)
def get_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": SCHOOL_LAT,
        "longitude": SCHOOL_LON,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"
        ),

        "hourly": (
            "temperature_2m,"
            "precipitation_probability,"
            "precipitation,"
            "weather_code"
        ),

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),

        "timezone": "Asia/Seoul",

        "forecast_days": 7
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.RequestException as e:

        return None, f"날씨 API 연결 오류: {e}"

    except Exception as e:

        return None, f"데이터 처리 오류: {e}"


# =========================================================
# 현재 날씨
# =========================================================

data, error = get_weather()

if error:

    st.error(error)
    st.stop()


current = data["current"]

temperature = current["temperature_2m"]
humidity = current["relative_humidity_2m"]
feels_like = current["apparent_temperature"]
precipitation = current["precipitation"]
wind_speed = current["wind_speed_10m"]
weather_code = current["weather_code"]

weather_name, weather_icon = weather_description(
    weather_code
)


# =========================================================
# 제목
# =========================================================

st.markdown(
    '<div class="main-title">🌤️ 보라고등학교 날씨</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '보라고등학교 주변 날씨 정보'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 현재 시간
# =========================================================

now = datetime.now(KST)

st.caption(
    f"🕐 {now.strftime('%Y년 %m월 %d일 %H:%M')} 기준"
)


# =========================================================
# 현재 날씨 카드
# =========================================================

st.markdown(
    f"""
    <div class="weather-card">

        <div class="weather-icon">
            {weather_icon}
        </div>

        <div style="font-size:22px;">
            {weather_name}
        </div>

        <div class="temperature">
            {temperature:.1f}°C
        </div>

        <div>
            체감온도 {feels_like:.1f}°C
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 상세 정보
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"""
        <div class="info-card">
            💧 습도<br>
            <b>{humidity}%</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        f"""
        <div class="info-card">
            💨 풍속<br>
            <b>{wind_speed:.1f} km/h</b>
        </div>
        """,
        unsafe_allow_html=True
    )


col3, col4 = st.columns(2)

with col3:

    st.markdown(
        f"""
        <div class="info-card">
            🌧️ 현재 강수량<br>
            <b>{precipitation:.1f} mm</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:

    st.markdown(
        f"""
        <div class="info-card">
            🌡️ 체감온도<br>
            <b>{feels_like:.1f}°C</b>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 오늘 예보
# =========================================================

st.markdown("---")

st.subheader("📅 오늘의 날씨")

daily = data["daily"]

today_code = daily["weather_code"][0]
today_max = daily["temperature_2m_max"][0]
today_min = daily["temperature_2m_min"][0]
today_rain = daily["precipitation_probability_max"][0]
today_precip = daily["precipitation_sum"][0]

today_name, today_icon = weather_description(
    today_code
)

st.markdown(
    f"""
    ### {today_icon} {today_name}

    **최저 {today_min:.1f}°C**
    
    **최고 {today_max:.1f}°C**

    🌧️ 강수확률 **{today_rain}%**

    💧 예상 강수량 **{today_precip:.1f} mm**
    """
)


# =========================================================
# 7일 예보
# =========================================================

st.markdown("---")

st.subheader("📆 7일 예보")

dates = daily["time"]

for i in range(len(dates)):

    date_obj = datetime.strptime(
        dates[i],
        "%Y-%m-%d"
    ).date()

    code = daily["weather_code"][i]

    max_temp = daily["temperature_2m_max"][i]
    min_temp = daily["temperature_2m_min"][i]

    rain_probability = (
        daily["precipitation_probability_max"][i]
    )

    name, icon = weather_description(code)

    day_name = [
        "월",
        "화",
        "수",
        "목",
        "금",
        "토",
        "일"
    ][date_obj.weekday()]

    col1, col2, col3, col4 = st.columns(
        [1.1, 1, 1.5, 1.2]
    )

    with col1:
        st.write(
            f"**{date_obj.strftime('%m/%d')} ({day_name})**"
        )

    with col2:
        st.write(f"{icon} {name}")

    with col3:
        st.write(
            f"🌡️ {min_temp:.0f}° / {max_temp:.0f}°C"
        )

    with col4:
        st.write(
            f"🌧️ {rain_probability}%"
        )

    st.divider()


# =========================================================
# 학교 정보
# =========================================================

with st.expander("🏫 학교 정보"):

    st.write("학교명: 보라고등학교")
    st.write(f"교육청 코드: {ATPT_OFCDC_SC_CODE}")
    st.write(f"학교 코드: {SD_SCHUL_CODE}")


# =========================================================
# 안내
# =========================================================

st.caption(
    "※ 날씨 데이터는 기상청 기반 날씨 API를 통해 제공됩니다."
)
