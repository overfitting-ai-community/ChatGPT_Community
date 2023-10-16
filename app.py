import streamlit as st
import time
import openai

openai.api_key = st.secrets["api_key"]
st.set_page_config(layout="wide",page_title="Peoply's Feedback AI", page_icon="🤖", initial_sidebar_state="auto")
# openai.api_key = "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"

# GPT 모델 셋팅값
name_list = [
    "손흥민",
    "이강인",
    "김민재"
]

init_fact_gathering = """- S대 교수진 및 산학 협력 과제를 선정하고 추진하는 전체 과정을 리드하였음.
- 팀의 가장 중요한 과제에서 도전적인 PM 역할을 성공적으로 수행하였음.
- 특허 출원을 통해서 팀의 기술 내재화 목적을 달성하였음.
- 이해관계자와 이슈가 발생 하기 전에 적시에 소통 하는 노력이 필요함."""

# feedback grade 셋팅값
grade_set = {
    'Highly Exceeds' : 5,
    'Exceeds' : 4,
    'Meets' : 3,
    'Marginally Meets' : 2,
    'Does not Meet' : 1
}
grade_list = list(grade_set.keys())

# Temperature 셋팅값
temperature_set = {
    '낮음' : 0.00,
    '보통' : 0.50,
    '높음' : 1.00
}
temperature_list = list(temperature_set.keys())

# feedback 생성 수 셋팅값
numbs_set = {
    '1' : 1,
    '2' : 2,
    '3' : 3
}
numbs_list = list(numbs_set.keys())

# feedback 글자수  셋팅값
length_set = {
    '200' : 200,
    '300' : 300,
    '400' : 400,
    '500' : 500
}
length_list = list(length_set.keys())

# 글자수 셋팅값
min_length_of_result = 200
init_length_of_result = 500

# GPT 모델 셋팅값
model_list = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301"
]

# Session History
if 'gen' not in st.session_state:
    st.session_state.gen = []

class Gen_set():
    name = None
    fact_gathering = None
    grade = None
    temperature = None
    length = None
    model = None
    output = None
    numbs = None

    def set_result(self, input_name, input_fact_gathering, input_grade, input_temperature, input_length, input_model, p_output, input_numbs):
        self.name = input_name
        self.fact_gathering = input_fact_gathering
        self.grade = input_grade
        self.temperature = input_temperature
        self.length = input_length
        self.model = input_model
        self.output = p_output
        self.numbs = input_numbs

def add_set():
    input_name = st.session_state.input_name
    input_fact_gathering = st.session_state.input_fact_gathering
    input_grade_text = st.session_state.input_grade_text
    input_grade = grade_set[input_grade_text]
    input_temperature_text = st.session_state.input_temperature_text
    input_temperature = temperature_set[input_temperature_text]
    input_length_text = st.session_state.input_length_text
    input_length = length_set[input_length_text]
    input_model = st.session_state.input_model
    input_numbs_text = st.session_state.input_numbs_text
    input_numbs = numbs_set[input_numbs_text]

    sys_prompt = f'({st.secrets["system_content"]} + {input_name})'
    usr_prompt = f'({st.secrets.user_content._01} + {input_name} + {st.secrets.user_content._02} + {input_name} + {st.secrets.user_content._03} + {input_name} + {st.secrets.user_content._04} + {input_fact_gathering})'

    gpt_prompt = [{
        "role": "system",
        "content": sys_prompt
    }, {
        "role": "user",
        "content": usr_prompt
    }]

    with st.spinner("Waiting for Feedback AI..."):
        gpt_response = openai.ChatCompletion.create(
            # model used here is ChatGPT
            # You can use all these models for this endpoint:
            # gpt-4, gpt-4-0314, gpt-4-32k, gpt-4-32k-0314,
            # gpt-3.5-turbo, gpt-3.5-turbo-0301
            model=input_model,
            messages=gpt_prompt,
            temperature=input_temperature,
            n=input_numbs,
            max_tokens=3000,
            top_p=1,
            # stream=True
        )

    # t = st.empty()
    # content = ""
    content: list = []
    counter = 0
    # for completions in gpt_response:
    #     counter += 1
    #     if "content" in completions.choices[0].delta:
    #         content += completions.choices[0].delta.get("content")
    #     t.markdown(" %s " % content)
    while input_numbs > counter:
        content.append(gpt_response.choices[counter]['message']['content'])
        counter += 1

    # model = gpt_response.model
    outputs = content

    g = Gen_set()
    g.set_result(input_name, input_fact_gathering, input_grade, input_temperature, input_length, input_model, outputs, input_numbs)

    gen = st.session_state.gen
    gen.append(g)
    st.session_state.gen = gen

def draw_result(input_name, input_fact_gathering, input_grade, input_temperature, input_length, input_model, p_output, input_numbs):
    st.write('---------------')
    st.markdown(f"이름 : **{input_name}**")
    st.write('Fact Gathering')
    st.write(input_fact_gathering)
    st.write('---------------')
    col1, col2 = st.columns(2)
    with col1:
        st.write('- 피드백 다양성 값 : ', input_temperature)
        st.write('- 글자수 제한 : ', input_length)
    with col2:
        st.write('- GPT 모델 : ', input_model)
        st.write('- 피드백 생성 수 : ', input_numbs)
    # st.write('피드백 등급 값 :', input_grade)
    st.write('---------------')
    st.write('- 피드백 생성 결과 : ')
    # st.write(p_output)
    for output in p_output:
        # output = f"*** {o} ***"
        # st.markdown(output)
        st.write(output)
        st.write('---------------')
    st.write('---------------')

# st.text("피평가자에 대한 MBO 내용을 입력하면, ChatGPT가 MBO 피드백을 생성합니다.")

# col1, col2 = st.columns(2)

with st.sidebar:
    # st.subheader("Input")
    # Input Form
    with st.form(key="my_form"):
        st.success('아래 폼을 완성해서 피드백을 생성하세요.', icon="📝")
        # Name
        st.selectbox(
            "팀원을 선택하세요.",
            name_list,
            key='input_name'
            )

        # fact_gathering text area
        st.text_area(
            'Fact Gathering:실적, 팀 공헌, 개선, 칭찬할 점을 간략히 알려 주세요.',
            init_fact_gathering,
            height=170,
            key='input_fact_gathering'
            )

        # feedback grade
        st.selectbox(
            '피드백 등급을 선택하세요.',
            grade_list,
            index=2,
            disabled=True,
            key='input_grade_text'
            )

        # GPT model
        st.selectbox(
            "GPT 모델을 선택하세요.",
            model_list,
            key='input_model'
        )

        # Temperature
        st.select_slider(
            '피드백의 다양성을 선택하세요.',
            options=temperature_list,
            key='input_temperature_text'
            )

        # length of result
        st.selectbox(
            "생성할 피드백 수를 선택 하세요.",
            numbs_list,
            key='input_numbs_text'
        )

        # length of result
        st.selectbox(
            '글자수를 제한해 주세요.',
            length_list,
            key='input_length_text'
            )

        st.form_submit_button("Generate", on_click=add_set)

st.image('https://raw.githubusercontent.com/overfitting-ai-community/ChatGPT_Gen_Comment/f6e0722f128f8bb5ee85f29dd52fcb8a6d8784eb/peoply.png', width=130)
st.info('**🤖 Feedback AI가 생성하는 내용을 아래에서 확인 할 수 있습니다.**')

# Result
if(len(st.session_state.gen) > 0):
    # for i in range(len(st.session_state.gen)):
    #     set = st.session_state.gen[i]
    #     draw_result(set.name, set.fact_gathering, set.grade, set.temperature, set.length, set.model, set.output, set.numbs)
    for idx, set in reversed(list(enumerate(st.session_state.gen))):
        draw_result(set.name, set.fact_gathering, set.grade, set.temperature, set.length, set.model, set.output,
                    set.numbs)
