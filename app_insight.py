from typing import Dict, Any
import streamlit as st
import time
import openai
import pandas as pd
import json

# from io import StringIO

openai.api_key = st.secrets["api_key_insight"]
st.set_page_config(layout="wide", page_title="Peoply insight AI", page_icon="🤖", initial_sidebar_state="auto")

# employee_name_list 셋팅값
employee_name_set = {
    '손흥민': 'TEST110',
    '이강인': 'TEST111',
    '김민재': 'TEST112',
    '황희찬': 'TEST113',
    '정우영': 'TEST114'
}
employee_name_list = list(employee_name_set.keys())

# Temperature 셋팅값
temperature_set = {
    '낮음': 0.00,
    '보통': 0.50,
    '높음': 1.00
}
temperature_list = list(temperature_set.keys())

# feedback 생성 수 셋팅값
numbs_set = {
    '1': 1,
    '2': 2,
    '3': 3
}
numbs_list = list(numbs_set.keys())

# insight 글자수  셋팅값
length_set = {
    '50': 50,
    '10': 10,
    '20': 20,
    '30': 30,
    '40': 40
}
length_list = list(length_set.keys())

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
    employee_id = None
    input_dataset = None
    tbl_validation = None
    temperature = None
    length = None
    model = None
    output = None
    numbs = None

    def set_result(self, input_name, employee_id, input_dataset, tbl_validation, input_temperature, input_length,
                   input_model, p_output, input_numbs):
        self.name = input_name
        self.employee_id = employee_id
        self.input_dataset = input_dataset
        self.tbl_validation = tbl_validation
        self.temperature = input_temperature
        self.length = input_length
        self.model = input_model
        self.output = p_output
        self.numbs = input_numbs


def add_set():
    input_dataset = json.load(st.session_state.input_dataset)
    input_employee_text = st.session_state.input_employee_text
    input_employee_id = employee_name_set[input_employee_text]
    input_temperature_text = st.session_state.input_temperature_text
    input_temperature = temperature_set[input_temperature_text]
    input_length_text = st.session_state.input_length_text
    input_length = length_set[input_length_text]
    input_model = st.session_state.input_model
    input_numbs_text = st.session_state.input_numbs_text
    input_numbs = numbs_set[input_numbs_text]

    def get_csv_tbl(dataset, user_id, employee_name):
        # json_data = pd.read_json(dataset)
        lst_user_id = []
        lst_year = []
        lst_competency = []
        lst_objective = []
        lst_overall = []
        for a in dataset[user_id]["data"]["evaluation"]["table"]["data"]:
            # print(a['year'], a['competency'], a['objective'],a['overall'])
            lst_user_id.append(user_id)
            lst_year.append(a['year'])
            lst_competency.append(a['competency'])
            lst_objective.append(a['objective'])
            lst_overall.append(a['overall'])

        data_set = {'직원 이름': lst_user_id, '년도': lst_year, '개인 역량 수준': lst_competency, '사업 성과 수준': lst_objective,
                    '종합평가 수준': lst_overall}

        table_output = pd.DataFrame(data_set)
        df = pd.DataFrame(data_set)

        eval_set = {
            "S": "기대 수준을 매우 초과",
            "A": "기대 수준을 초과",
            "B": "보통 수준",
            "C": "미달",
            "D": "매우 미달",
            "EX": "우수함",
            "NI": "개선이 필요함",
            "GD": "보통"
        }
        for key in list(eval_set.keys()):
            df.replace(key, eval_set[key], inplace=True)
        df.replace(user_id, employee_name, inplace=True)

        csv_output = df.to_csv()
        return csv_output, table_output

    # st.write(input_dataset)

    data_prompt, tbl_validation = get_csv_tbl(input_dataset, input_employee_id, input_employee_text)
    sys_prompt = f'({st.secrets.system_content_insight._01} + {input_employee_text} + {st.secrets.system_content_insight._02} + {input_employee_text} + {st.secrets.system_content_insight._03} + {input_length} + {st.secrets.system_content_insight._04}'
    usr_prompt = f'({data_prompt})'

    gpt_prompt = [{
        "role": "system",
        "content": sys_prompt
    }, {
        "role": "user",
        "content": usr_prompt
    }]

    with st.spinner("Waiting for Insight AI..."):
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

    content: list = []
    counter = 0
    while input_numbs > counter:
        content.append(gpt_response.choices[counter]['message']['content'])
        counter += 1
    # model = gpt_response.model
    outputs = content

    g = Gen_set()
    g.set_result(input_employee_text, input_employee_id, data_prompt, tbl_validation, input_temperature, input_length,
                 input_model, outputs, input_numbs)

    gen = st.session_state.gen
    gen.append(g)
    st.session_state.gen = gen


def draw_result(input_employee_text, input_employee_id, data_prompt, tbl_validation, input_temperature, input_length,
                input_model, outputs, input_numbs):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"이름 : **{input_employee_text}**")
        st.write('- 피드백 다양성 값 : ', input_temperature)
        st.write('- 글자수 제한 : ', input_length)
    with col2:
        st.markdown(f"직원 id : **{input_employee_id}**")
        st.write('- GPT 모델 : ', input_model)
        st.write('- Insight 생성 수 : ', input_numbs)
    if st.session_state.debug:
        st.write('---------------')
        st.write('- source table : ', tbl_validation)
        st.write('---------------')
        # st.write('- user prompt : ', data_prompt)
        # st.write('---------------')
    st.write('- Insight report : ')
    # st.write(p_output)
    for output in outputs:
        # output = f"*** {o} ***"
        # st.markdown(output)
        st.write(output)
        st.write('---------------')
    st.write('---------------')


# st.text("피평가자에 대한 MBO 내용을 입력하면, ChatGPT가 MBO 피드백을 생성합니다.")

# col1, col2 = st.columns(2)

with st.sidebar:
    with st.form(key="my_form"):
        st.success('아래 폼을 완성해서 Insight를 생성하세요.', icon="📝")
        uploaded_file = st.file_uploader("Choose a file", key='input_dataset')

        # employee_name_list
        st.selectbox(
            '직원이름을 선택하세요.',
            employee_name_list,
            index=0,
            key='input_employee_text'
        )

        # GPT model
        st.selectbox(
            "GPT 모델을 선택하세요.",
            model_list,
            disabled=True,
            index=1,
            key='input_model'
        )

        # Temperature
        st.select_slider(
            'insight 다양성을 선택하세요.',
            options=temperature_list,
            disabled=True,
            # index=0,
            key='input_temperature_text'
        )

        # length of result
        st.selectbox(
            "생성할 피드백 수를 선택 하세요.",
            numbs_list,
            disabled=True,
            index=0,
            key='input_numbs_text'
        )

        # length of result
        st.selectbox(
            '글자수를 제한해 주세요.',
            length_list,
            disabled=True,
            index=0,
            key='input_length_text'
        )

        checked = st.checkbox(
            'debug mode', key='debug'
        )

        st.form_submit_button("Generate", on_click=add_set)
        # st.form_submit_button("Generate", on_click=add_set(uploaded_dataset))

st.image(
    'https://raw.githubusercontent.com/overfitting-ai-community/ChatGPT_Gen_Comment/f6e0722f128f8bb5ee85f29dd52fcb8a6d8784eb/peoply.png',
    width=130)
st.info('**🤖 Insight AI가 생성하는 인사평가 분석을 아래에서 확인 할 수 있습니다.**')

# Result
if (len(st.session_state.gen) > 0):
    # for i in range(len(st.session_state.gen)):
    #     set = st.session_state.gen[i]
    #     draw_result(set.name, set.fact_gathering, set.grade, set.temperature, set.length, set.model, set.output, set.numbs)
    for idx, set in reversed(list(enumerate(st.session_state.gen))):
        draw_result(set.name, set.employee_id, set.input_dataset, set.tbl_validation, set.temperature, set.length,
                    set.model, set.output,
                    set.numbs)
