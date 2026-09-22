import streamlit as st
import requests
from datetime import date

st.set_page_config(
    page_title="한국 날씨",
    page_icon="🌤️",
    layout="centered"
)

# ==========================================
# 한국 주요 지역 좌표
# ==========================================

LOCATIONS = {
    "서울": (37.5665, 126.9780),
    "인천": (37.4563, 126.7052),
    "수원": (37.2636, 127.0286),
    "대전": (36.3504, 127.3845),
    "대구": (35.8714, 128.6014),
    "부산": (35.1796, 129.0756),
    "광주": (35.1595, 126.8526),
    "울산": (35.5384, 129.3114),
    "세종": (36.4800, 127.2890),
    "제주": (33.4996, 126.5312),
    "강릉": (37.7519, 128.8761),
    "전주": (35.8242, 127.1480),
    "청주": (36.6424, 127.4890),
    "춘천": (37.8813, 127.7298)
}


# ==========================================
# 날씨 코드
# ==========================================

def get_weather_name(code):

    weather = {
        0: ("맑음", "☀️"),
        1: ("대체로 맑음", "🌤️"),
        2: ("부분적으로 흐림", "⛅"),
        3: ("흐림", "☁️"),

        45: ("안개", "🌫️"),
        48: ("안개", "🌫️"),

        51: ("약한 이슬비", "🌦️"),
        53: ("이슬비", "🌦️"),
        55: ("강한 이슬비", "🌧️"),

        61: ("약한 비", "🌧️"),
        63: ("비", "🌧️"),
        65: ("강한 비", "🌧️"),

        71: ("약한 눈", "🌨️"),
        73: ("눈", "❄️"),
        75: ("강한 눈", "❄️"),

        80: ("소나기", "🌦️"),
        81: ("소나기", "🌧️"),
        82: ("강한 소나기", "⛈️"),

        95: ("뇌우", "⛈️"),
        96: ("우박을 동반한 뇌우", "⛈️"),
        99: ("강한 뇌우", "⛈️")
    }

    return weather.get(
        code,
        ("날씨 정보 없음", "❓")
    )


# ==========================================
# 날씨 API
# ==========================================

@st.cache_data(ttl=600)
def get_weather(lat, lon, selected_date):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": lon,

        "start_date": selected_date,
        "end_date": selected_date,

        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),

        "timezone": "Asia/Seoul"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ==========================================
# 제목
# ==========================================

st.title("🇰🇷 한국 날씨")

st.caption(
    "원하는 지역과 날짜를 선택해서 날씨를 확인하세요."
)

st.divider()


# ==========================================
# 지역 선택
# ==========================================

st.subheader("📍 지역 선택")

location = st.selectbox(
    "지역",
    list(LOCATIONS.keys())
)

lat, lon = LOCATIONS[location]


# ==========================================
# 날짜 선택
# ==========================================

st.subheader("📅 날짜 선택")

selected_date = st.date_input(
    "날짜",
    value=date.today()
)

date_text = selected_date.strftime(
    "%Y년 %m월 %d일"
)

st.write(
    f"**{location} · {date_text}**"
)


# ==========================================
# 날씨 조회
# ==========================================

if st.button(
    "🔍 날씨 조회",
    use_container_width=True
):

    try:

        data = get_weather(
            lat,
            lon,
            selected_date.strftime("%Y-%m-%d")
        )

        daily = data["daily"]

        weather_code = daily["weather_code"][0]

        max_temp = daily["temperature_2m_max"][0]
        min_temp = daily["temperature_2m_min"][0]

        rain_probability = (
            daily["precipitation_probability_max"][0]
        )

        precipitation = daily["precipitation_sum"][0]

        weather_name, weather_icon = get_weather_name(
            weather_code
        )


        # ==================================
        # 결과 카드
        # ==================================

        st.divider()

        st.markdown(
            f"""
            <div style="
                padding:30px;
                border-radius:22px;
                background:linear-gradient(
                    135deg,
                    #eaf4ff,
                    #ffffff
                );
                border:1px solid #d8eaff;
                text-align:center;
            ">

                <div style="font-size:70px;">
                    {weather_icon}
                </div>

                <h2>
                    {location}
                </h2>

                <h3>
                    {date_text}
                </h3>

                <div style="
                    font-size:28px;
                    margin:20px;
                ">
                    {weather_name}
                </div>

                <div style="
                    font-size:22px;
                ">
                    최저
                    <b>{min_temp:.1f}°C</b>
                    &nbsp;&nbsp;&nbsp;
                    최고
                    <b>{max_temp:.1f}°C</b>
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ==================================
        # 상세 정보
        # ==================================

        st.subheader("🌡️ 상세 날씨")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "최저 기온",
                f"{min_temp:.1f}°C"
            )

        with col2:

            st.metric(
                "최고 기온",
                f"{max_temp:.1f}°C"
            )


        col3, col4 = st.columns(2)

        with col3:

            st.metric(
                "강수확률",
                f"{rain_probability}%"
            )

        with col4:

            st.metric(
                "예상 강수량",
                f"{precipitation:.1f} mm"
            )


    except Exception as e:

        st.error(
            "날씨 정보를 가져오는 중 오류가 발생했습니다."
        )

        st.caption(str(e))


# ==========================================
# 안내
# ==========================================

st.divider()

st.caption(
    "※ 날씨 정보는 Open-Meteo API를 통해 제공합니다."
)
