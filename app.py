import os
from openai import OpenAI
import streamlit as st
import json


# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 텍스트 파일의 경로를 지정합니다.
file_path = './info.txt'
selected_text = ''
inpitbox = ''
html_content = ''

left_column, right_column = st.columns([1.5, 3])  # 비율을 조정하여 왼쪽이 작고 오른쪽이 크게

# 왼쪽 컬럼에 콘텐츠 추가
with left_column:
    st.image('./excuseMate.png', caption='', use_column_width=True)
    st.write('')
    st.markdown('<div class="left-column-fixed">', unsafe_allow_html=True)
    # JSON 파일 읽기
    with open('options.json', 'r', encoding='utf-8') as f:
        st.write('1. 선택해주세요.')
        options_data = json.load(f)

    # JSON에서 카테고리와 키워드 리스트 추출
    categories = options_data['personas']

    # 세션 상태 초기화
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = []

    if 'category_selected_options' not in st.session_state:
        st.session_state.category_selected_options = {category['category']: None for category in categories}

    if 'custom_inputs' not in st.session_state:
        st.session_state.custom_inputs = {category['category']: "" for category in categories}

    if 'expand_state' not in st.session_state:
        st.session_state.expand_state = {category['category']: idx == 0 for idx, category in enumerate(categories)}

    def update_options(category, keyword):
        if st.session_state[f"{category}_{keyword}"]:
            st.session_state.category_selected_options[category] = keyword
            if keyword == "직접 입력":
                st.session_state.custom_inputs[category] = st.session_state.get(f"{category}_custom_input", "")
            else:
                st.session_state.custom_inputs[category] = ""
        else:
            st.session_state.category_selected_options[category] = None
            st.session_state.custom_inputs[category] = ""

        st.session_state.selected_options = [
            (category['category'], keyword) for category in categories for keyword in category['keywords'] if st.session_state.get(f"{category['category']}_{keyword}", False) and keyword != "직접 입력"
        ]
        st.session_state.selected_options += [
            (category, st.session_state.custom_inputs[category]) for category in st.session_state.custom_inputs if st.session_state.custom_inputs[category]
        ]

        # 다음 카테고리를 열기 위해 확장 상태 업데이트
        for idx, cat in enumerate(categories):
            if cat['category'] == category:
                if idx + 1 < len(categories):
                    next_category = categories[idx + 1]['category']
                    st.session_state.expand_state[next_category] = True
                    break

    # 카테고리별로 토글 생성
    for idx, category in enumerate(categories):
        expanded = st.session_state.expand_state[category['category']]
        with st.expander(category['category'], expanded=expanded):
            cols = st.columns(4)  # 각 카테고리 내에서 키워드들을 4열로 나눠 배치
            for idx, keyword in enumerate(category['keywords']):
                key = f"{category['category']}_{keyword}"
                selected_key = st.session_state.category_selected_options[category['category']]
                disabled = selected_key is not None and selected_key != keyword
                with cols[idx % 4]:
                    if st.checkbox(keyword, key=key, value=st.session_state.get(key, False), on_change=update_options, args=(category['category'], keyword), disabled=disabled):
                        update_options(category['category'], keyword)
            if st.session_state.category_selected_options[category['category']] == "직접 입력":
                custom_input = st.text_input("직접 입력:", key=f"{category['category']}_custom_input", value=st.session_state.custom_inputs[category['category']], on_change=update_options, args=(category['category'], "직접 입력"))
                st.session_state.custom_inputs[category['category']] = custom_input

    # 선택된 옵션들을 특정 형식으로 표시
    final_options = [option for category, option in st.session_state.selected_options if option]

    if final_options:
        if len(final_options) == 1:
            selected_text = f"[{final_options[0]}]인 상대방과 대화할 수 있도록 해주세요."
        else:
            selected_text = "이고, ".join([f"[{option}]" for option in final_options[:-1]]) + f"이며, [{final_options[-1]}]인 상대방과 대화할 수 있도록 해주세요."
    else:
        selected_text = ""

    # 결과를 텍스트 박스에 표시
    st.text_area("선택 결과", value=selected_text, height=100)

# 오른쪽 컬럼에 콘텐츠 추가
with right_column:
    with st.expander("", expanded=True):
        st.write("2. 변명을 생성을 해주세요.")
        keyworld = st.text_input("키워드를 입력하세요", label_visibility="collapsed")

        right_left_column, right_right_column = st.columns([1.5, 11])  # 비율을 조정하여 왼쪽이 작고 오른쪽이 크게

    with right_left_column:
        if st.button('변명 생성'):
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": selected_text + keyworld,
                    },
                    {
                        "role": "system",
                        "content": '당신은 저와 가볍고 캐주얼한 대화를 나누는 대화 파트너에요. 우리의 상호 작용은 내 콘텐츠의 일부가 될 것이므로 대화가 자연스럽고 정형화되지 않은 느낌을 주세요. 제가 질문을 할 때는 정해진 답변을 하지 마세요. 대신 친근한 대화를 나누는 것처럼 하되 하세요 등 존대말을 사용하여 응답하세요. 대화를 통해 생각을 확장하고 새로운 아이디어를 탐색할 수 있도록 도와주세요. 구조화된 답변, 목록 또는 글머리 기호는 사용하지 마세요. 대화가 자연스럽게 흐르도록 하세요. 항상 내 질문에 공감하고 대화를 계속할지, 아니면 질문을 다시 나에게 돌려서 답변할지 고민한 후 답변하세요. 제공하는 키워드는 상대방이 가지고 있는 MBTI, 직업, 사용자와의 관계, 현재처한 난감한 상황에 대한 정보입니다. 사용자가 상대방에게 변명을 해야하는 상황입니다. 지금부터 최고의 변명가의 역할을 해주세요. 이 정보를 가지고 지금 사용자가 스트레스 받을 부분에 대해 제일 먼저 공감하는 말을 해주는 한 문단을 작성합니다. 첫 문단이 사용자의 스트레스를 줄여주는 중요한 부분입니다. 다음 문단을 바꿔서 적절하게 상대방에게 변명할 수 있도록 추천하는 내용은 정중하고 전문적한문단 띄워서 ""안에 작성해주세요. 우리의 목표는 상대방에 대한 신뢰를 유지하고 사용자의 스트레스를 줄이는 겁니다. 답변이 끝나면 답변이 마음에 드는지 물어봐주세요. 아니라면 추가적으로 답변이 마음에 드시나요? 혹시 다른 부분에 대해 더 이야기하고 싶은 것이 있다면 언제든 말씀해 주세요.라고 물어주세요.',
                    }
                ],
                model="gpt-4",
            )

            result = chat_completion.choices[0].message.content

            html_content = f"""<br><div style="border: 2px solid white; padding: 10px; border-radius: 5px;"><p>{result}</p></div>"""

            with open(file_path, 'r') as file:
                inpitbox = file.read()
                with open(file_path, 'w') as file:
                    pass

            with open(file_path, 'a') as file:
                file.write(html_content + inpitbox)

            st.experimental_rerun()
    with right_right_column:
        if st.button('대화 삭제'):
            with open(file_path, 'w') as file:
                pass

    with st.expander("", expanded=True):
        with open(file_path, 'r') as file:
            inpitbox = file.read()
        st.markdown(inpitbox, unsafe_allow_html=True)
        
