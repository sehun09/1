import streamlit as st
from openai import OpenAI

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="칭찬 생성기",
    page_icon="✨",
    layout="centered"
)

# -----------------------------
# OpenAI API 연결
# -----------------------------
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("OPENAI_API_KEY가 Streamlit Secrets에 설정되어 있지 않습니다.")
    st.stop()

# -----------------------------
# 제목
# -----------------------------
st.title("✨ AI 칭찬 생성기")
st.write("이름과 특징을 입력하면 AI가 자연스러운 칭찬을 만들어줍니다!")

st.divider()

# -----------------------------
# 입력
# -----------------------------
name = st.text_input(
    "👤 이름",
    placeholder="예: 민수"
)

character = st.text_area(
    "💬 특징이나 잘한 점",
    placeholder="예: 친구들을 잘 도와주고 발표를 열심히 했다."
)

# -----------------------------
# 칭찬 생성
# -----------------------------
if st.button("✨ 칭찬 만들어줘", use_container_width=True):

    if not name.strip():
        st.warning("이름을 입력해주세요.")
        st.stop()

    if not character.strip():
        st.warning("칭찬할 특징이나 잘한 점을 입력해주세요.")
        st.stop()

    prompt = f"""
너는 사람의 장점을 찾아 따뜻하고 자연스럽게 칭찬해주는 AI야.

이름: {name}
특징 또는 잘한 점: {character}

위 정보를 바탕으로 다음 조건을 만족하는 칭찬을 만들어줘.

1. 이름을 자연스럽게 포함할 것
2. 진심이 느껴지도록 작성할 것
3. 너무 과장된 표현은 사용하지 않을 것
4. 2~4문장 정도로 작성할 것
5. 학생이 들어도 자연스러운 표현을 사용할 것
6. 입력된 특징을 구체적으로 칭찬할 것
7. 칭찬 내용만 출력하고 설명은 하지 말 것
"""

    try:
        with st.spinner("칭찬을 만드는 중... ✨"):

            response = client.responses.create(
                model="gpt-5.4-nano",
                input=prompt
            )

            result = response.output_text

        st.success("칭찬 완성! 🎉")

        st.markdown(
            f"""
            ### 💖 {name}에게

            > {result}
            """
        )

    except Exception as e:
        st.error("칭찬을 생성하는 중 오류가 발생했습니다.")
        st.code(str(e))
