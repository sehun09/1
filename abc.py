import streamlit as st
from openai import OpenAI

# 1. Streamlit Secrets에서 OpenAI API Key 가져오기
# Streamlit Cloud 배포 시 Advanced Settings -> Secrets 메뉴에 값을 입력해야 합니다.
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("⚠️ Streamlit Secrets에서 'OPENAI_API_KEY'를 설정해주세요.")
    st.stop()

# 2. OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# 3. 웹 페이지 UI 레이아웃 설정
st.set_page_config(page_title="AI 칭찬 생성기", page_icon="🎉", layout="centered")

st.title("🎉 나만을 위한 AI 칭찬 생성기")
st.write("칭찬받고 싶은 대상과 상황을 입력하시면, AI가 당신에게 딱 맞는 따뜻하고 멋진 칭찬을 선물합니다!")

# 4. 사용자 입력 폼 구성
with st.form("praise_form"):
    name = st.text_input("👤 칭찬받을 사람의 이름 또는 별명", placeholder="예: 길동, 나 자신")
    
    situation = st.text_area(
        "💡 어떤 상황에 대해 칭찬받고 싶나요?", 
        placeholder="예: 오늘 아침 일찍 일어나서 운동을 다녀왔어.\n예: 이번 프로젝트 발표를 무사히 마쳤어."
    )
    
    tone = st.selectbox(
        "🎭 칭찬의 분위기를 선택하세요",
        ["감동적이고 진지하게", "유쾌하고 열정적으로", "둥기둥기 다정하게", "성공한 CEO처럼 당차게"]
    )
    
    submit_button = st.form_submit_button("✨ 칭찬 생성하기")

# 5. 생성 버튼 클릭 시 로직 실행
if submit_button:
    if not name or not situation:
        st.warning("⚠️ 이름과 상황을 모두 입력해주세요!")
    else:
        with st.spinner("🤖 AI가 열심히 칭찬 문구를 작성하고 있습니다..."):
            try:
                # 프롬프트 구성
                system_prompt = f"당신은 상대방의 마음에 깊은 위로와 자신감을 주는 '칭찬 전문가'입니다. 사용자가 입력한 상황에 맞춰 {tone} 어조로 맞춤형 칭찬을 작성해주세요."
                user_content = f"이름: {name}\n상황: {situation}\n\n위 내용을 바탕으로 진정성 있고 감동적인 칭찬 메시지를 작성해줘."
                
                # OpenAI API 호출 (gpt-5.4-nano 모델 적용)
                response = client.chat.completions.create(
                    model="gpt-5.4-nano",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.7
                )
                
                # 결과 출력
                praise_result = response.choices[0].message.content
                st.success("🎈 맞춤 칭찬이 도착했습니다!")
                st.info(praise_result)
                
            except Exception as e:
                st.error(f"❌ 오류가 발생했습니다: {e}")
