import os
import openai
from collections import defaultdict

import time
import pandas as pd
import yfinance as yf
from yahooquery import Ticker

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# for long name
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# img_to_bytes and img_to_html inspired from https://pmbaumgartner.github.io/streamlitopedia/sizing-and-images.html
import base64
from pathlib import Path
from PIL import Image

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

def img_to_html(img_path, width , height):
    img_html = f"<img src='data:image/png;base64,{img_to_bytes(img_path)}' width = {width} height = {height} class='img-fluid'>"
    return img_html

def loadcompanyinformation(company:str = 'NVDA', item:str = 'income_statement'):
    infodict = defaultdict()
    commpanyinfo = Ticker(company)
    if item == 'income_statement':
        for idx, info in enumerate(commpanyinfo.income_statement()[commpanyinfo.income_statement()['asOfDate'].dt.year > 2021].iterrows()):
            infodict[idx] = info
    accountinginfo = infodict.items()
    return accountinginfo


def getlongname(symbol):    
    # Define the URL for the stock's Yahoo Finance page
    url = f"https://finance.yahoo.com/quote/{symbol}"
    # Send a GET request to the URL and parse the HTML content using BeautifulSoup
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the HTML element that contains the long name of the stock
    long_name_element = soup.find("h1", attrs={"class": "D(ib) Fz(18px)"})
    # Extract the long name from the HTML element
    long_name = long_name_element.get_text()
    return long_name

def slow_function():
    for i in range(5):
        time.sleep(1)

# Enable wide mode
# pavicon
st.set_page_config(
    page_title="기업어때",
    page_icon= 'img/기업어때_Icon500x500_favicon_1.png',
    layout="wide",
)

# Get the values of the environment variables
# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = st.secrets["openai_api_key"]

# empty report
report = ' '

# web

# st.markdown(img_to_html(img_path='img/기업어때_Icon500x500_favicon_1.png', width= 100, height = 100), unsafe_allow_html=True)

col1, col2 = st.columns([1,15])
with col1:
	st.markdown(body = img_to_html(img_path='img/기업어때_Icon500x500_favicon_1.png' , width= 100, height = 100), unsafe_allow_html=True)
with col2:
	st.markdown(f"<h1 style='font-size:20px margin-top:30px'>안녕하세요. 투자대가와 분석할 기업을 선택해주세요.</h1>", unsafe_allow_html=True)

# investors 
investors = {
    'warrenbuffett': {
        'pros': "워런버핏은 역사상 가장 성공한 투자자로 유명하며, 그의 가치투자 전략은 장기간 높은 성과를 달성했습니다. 워런버핏이 CEO인 투자회사 버크셔해서웨이의 작년 2022년까지 59년 누적 수익률은 379만%로 S&P500 지수의 동기 누적 수익률 2.5만%를 월등히 뛰어넘었습니다. 2022년 현재 워런버핏의 주요 포트폴리오로는 뱅크오브아메리카, 코카콜라, 아메리칸익스프레스, 애플 등이 있습니다.",
        'cons': "워런버핏의 투자 전략은 기업에 대한 편더멘털과 경쟁 구도에 대한 깊은 이해가 필요하여, 개인 투자자들이 모방하기에 어려운 측면이 있습니다(개인적으로 모든 기관투자자들에게 해당하는 이야기여서 이 부분은 빼도 무방할 것으로 생각하나 판단에 맡기겠음). 또한, 이미 어느 정도 성숙기에 접어들어 잠재 수익이 높지 않을 것으로 예상되는 대형 우량 기업 위주로 포트폴리오를 운영한다는 점에 주의해야 합니다."
    },
    'peterlynch': {
        'pros': "피터린치는 13년간 매년 평균 30%에 가까운 수익률을 낸 후 46세의 젊은 나이에 가족과 함께 하기 위해 은퇴한 월스트리트의 기록적인 펀드매니저입니다. 그의 투자 철학은 '알짜 주식은 내 주변에 있다!'로 요약할 수 있습니다. 그의 대표적인 투자 기업에는 실제로 자주 이용하던 던킨도너츠, GAP 등이 있습니다. 이처럼 그는 내가 잘 아는 주식을 사고, 경쟁사 주식이 아닌 왜 이 기업의 주식을 사야하는지를 초등학생도 이해하기 쉽게 설명할 수 있어야 한다고 강조합니다. 때문에 상대적으로 개인 투자자들도 쉽게 접근할 수 있다는 점이 매력적입니다.",
        'cons': "피터린치의 투자 방식으로 소비재 혹은 개인이 접하기 쉬운 섹터로 포트폴리오가 치우칠 수 있습니다. 또한 발견한 종목의 제품이 일시적인 유행 끝에 대폭 하락할 수 있기에 균형잡힌 시각이 필요하다는 점을 유념해야 합니다."
    },
    'benjamingraham': {
        'pros': "워런 버핏의 스승으로 증권분석 및 가치투자 이론의 창시자로 불리는 인물입니다. 약 20년간 연 평균 20%대의 수익을 냈으며, 투자 전략은 低 부채비율&PBR, 高 ROA, 즉 재무구조가 안정적이고 저평가된 기업을 찾는 것으로 요약됩니다.",
        'cons': "벤자민 그레이엄이 활동했던 시절은 대공황 이후로 그 당시와 제도 및 환경이 많이 변화되었습니다. 또한 재무적 지식이 없는 일반 개인 투자자가 모방하기 쉽지 않을 수 있으며, 저평가 주식은 성장성이 낮을 가능성이 있다는 점 유의해야 합니다. "
    },
    'raydalio': {
        'pros': "200조원의 자산을 관리하는 브리지워터의 창립자입니다. 글로벌 시장의 다양한 인덱스를 지표를 분석하고 분산 투자를 시스템화한 투자 기법으로 유명합니다. 자식들을 위해 비가 오나 눈이 오나 자산 가치 변동을 방어할 수 있는 '올웨더(All Wheather) 전략'으로 큰 인기를 얻고 있습니다.",
        'cons': "상당한 자본이 필요하고 수 많은 변수를 고려해야 하기 때문에 초보 개인투자자들이 접근하기에는 어려운 측면이 있습니다. 또한, 거시 경제에 초점을 맞추고 있어 개별 주식의 성장세를 통한 차익 실현 기회를 간과할 수 있다는 점 유의해야 합니다."
    },
    'georgesoros': {
        'pros': "4,200%의 경이로운 수익률을 달성한 퀀텀펀드의 공동 창립자입니다. 시장의 불균형과 불완전성에서 발견되는 기회에 큰 레버리지를 일으켜 수익을 극대화시키는 전략을 구사합니다.",
        'cons': "소로스는 시장을 조작하고 그의 재산을 정치에 영향을 미치기 위해 사용한 혐의를 받고 있는 논란이 많은 인물입니다. 소로스 펀드 운용사는 민간투자회사로 보유주식이나 투자전략을 외부에 공개하지 않아 일부 투자자들의 고민거리가 될 수 있습니다. 그의 투자 전략은 단기적이며 리스크가 매우 크다는 점 유의해야 합니다."
    },
    'johnpaulson': {
        'pros': "폴슨이 거시경제 동향을 파악하고 특정 부문이나 자산에 베팅하는 데 초점을 맞춘 것은 2007년 서브프라임 모기지(비우량 주택담보대출) 시장에 대한 성공적인 베팅과 같은 과거에 상당한 이득을 가져온 결과입니다.",
        'cons': "폴슨의 접근 방식은 거시 경제 동향과 부문별 지식에 대한 상당한 전문 지식이 필요하기 때문에 개인 투자자에게 위험할 수 있습니다. 또한, 그의 접근 방식은 최근 금 시장에서 손실을 입은 것에서 입증된 것처럼 상당한 시장 변동성을 겪을 수 있습니다."
    }
}

# user input##################################################################################

advisor = st.selectbox(
    '투자대가를 선택해주세요.',
    (investors.keys()),
    label_visibility='visible')
if advisor:
    st.markdown(f"<p style='color: #6482FF; font-size: 10px'>{advisor}을 고르셨군요! {advisor}의 특징을 확인해보세요.</p>", unsafe_allow_html=True)

with st.expander('투자 소개'):

        col1, col2 = st.columns(2)
        with col1:
            st.header('Pros')
            st.text_area(label = 'Pros', value = investors[advisor]['pros'],label_visibility='collapsed')

        with col2:
            st.header('Cons')
            st.text_area(label = 'Cons', value = investors[advisor]['cons'],label_visibility='collapsed')

#############################################################################################

# button customized #########################################################################

m = st.markdown(
"""
<style>
div.stButton > button:first-child {
	background:linear-gradient(to right, #2522f0 5%, #a53091 100%);
	background-color:#2522f0;
	border-radius:28px;
	border:1px solid #000000;
	display:inline-block;
	cursor:pointer;
	color:#ffffff;
	font-family:Arial;
	font-size:22px;
	padding:16px 31px;
	text-decoration:none;
	text-shadow:0px 1px 0px #2f6627;
}
button:hover {
	background:linear-gradient(to right, #a53091 5%, #2522f0 100%);
	background-color:#a53091;
}
button:active {
	position:relative;
	top:1px;
}
""",unsafe_allow_html=True)


#############################################################################################



#############################################################################################
targetticker = st.text_input('분석할 기업의 티커를 입력해주세요.',placeholder='예시) NVDA')
st.markdown(f"<p style='color: #6482FF; font-size: 10px'>지금은 뉴욕증권거래소에 상장된 기업만 입력이 가능해요.</p>", unsafe_allow_html=True)
try:
    with st.form("result form"):
        companylongname = getlongname(symbol = targetticker.upper())

        # Every form must have a submit button.
        _, _, _, col4, _, _, _ = st.columns([1,1,1,1.5,1,1,1])

        # this will put a button in the middle column
        with col4:
            submitted = st.form_submit_button("분석시작", use_container_width=True)

        if submitted:
            with st.spinner("당신의 투자를 응원해요"):
                slow_function()
            st.success(body=f"기다려 주셔서 감사해요. {companylongname}에 대한 레포팅은 다음과 같아요.")

            # chart visaulization ######################################################################
            # Loading information for stock market

            col1, _, col2 = st.columns([5,0.5,9])
            with col1:
                st.write('지난 1년간 주식 가격과 레포트를 대조하며 판단해보아요!')
                company = yf.Ticker(f'{targetticker}')
                stock_data = company.history(interval='1d',period='1y')

                ## parameter ##
                parameter = defaultdict()
                parameter['fontsize'] = 8

                # Find the index of the maximum and minimum values of the 'Close' column
                max_index = stock_data['Close'].idxmax()
                min_index = stock_data['Close'].idxmin()

                # Find the date of the highest and lowest prices
                highest_date = stock_data.loc[stock_data['Close'].idxmax()].name.date().strftime('%Y%m%d')
                lowest_date = stock_data.loc[stock_data['Close'].idxmin()].name.date().strftime('%Y%m%d')

                # Set custom colors and styling for the plot
                plt.style.use('seaborn')
                colors = ['#9836e3', '#ff7f0e', '#2ca02c']
                plt.rcParams.update({
                    'axes.spines.right': False,
                    'axes.spines.top': False,
                    'axes.edgecolor': '#cfcfd1',
                    'axes.labelcolor': '#cfcfd1',
                    'xtick.color': '#cfcfd1',
                    'ytick.color': '#cfcfd1',
                    'axes.grid': False,
                    'grid.alpha': 1.0,
                    'axes.facecolor' : '#0f0f13',
                    'grid.color': '#0f0f13',
                    'figure.facecolor' : '#0f0f13',
                })


                # Plot the closing price of the stock over time
                fig, ax = plt.subplots()
                ax.plot(stock_data['Close'], color=colors[0], label='Closing Price')
                ax.scatter(max_index, stock_data['Close'].loc[max_index], color=colors[1], marker='o', s=50, label='Highest Price')
                ax.scatter(min_index, stock_data['Close'].loc[min_index], color=colors[2], marker='o', s=50, label='Lowest Price')
                ax.annotate(f"Max Price: {stock_data['Close'].loc[max_index]:.2f}\n date: {highest_date}", xy=(max_index, stock_data['Close'].loc[max_index]),
                            xytext=(20, -20), textcoords='offset points', ha='left', va='top', fontsize=parameter['fontsize'], color = '#cfcfd1',
                            arrowprops=dict(arrowstyle='->', color='#cfcfd1', lw=2))
                ax.annotate(f"Min Price: {stock_data['Close'].loc[min_index]:.2f}\n date; {lowest_date}", xy=(min_index, stock_data['Close'].loc[min_index]),
                            xytext=(-20, 20), textcoords='offset points', ha='right', va='bottom', fontsize=parameter['fontsize'], color = '#cfcfd1',
                            arrowprops=dict(arrowstyle='->', color='#cfcfd1', lw=2))

                ax.set(xlabel='Date', ylabel='Closing Price')
                # # Add a watermark to the plot
                # ax.text(0.5, 0.5, 'Watermark Text', alpha=0.2, color='white',
                #         fontsize=50, ha='center', va='center', transform=ax.transAxes)

                st.pyplot(fig)
            # prompt engineering #######################################################################

            with col2:
                # wait time
                col2height = 350
                waitparagraph = st.empty()
                waitparagraph.text_area(label = f"이런 기능도 있어요", placeholder= f"레포팅을 이용해서 투자일지를 적을 수 있는 공간이 있습니다. 레포팅 완성 후 하단의 다운로드 버튼을 클릭하신후에 블로그 글 작성시에 함께 활용해보세요 ! 레포트를 열심히 만들고 있어요 조금만 기다려 주세요." , height=col2height)

                # accounting information ##########
                accountingitem = 'income_statement'
                accountinginfo = loadcompanyinformation(company=companylongname,item=accountingitem)
                
                # prompt scenario #################
                message = defaultdict()
                message['system'] = f'you are the {advisor} advisor for help investment people who didnt know well the accounting information. so you should help him by {advisor} manner and view. and you have to divide the results of outcome by separator for intutive report. plus'
                message['user1'] = f"i'm now considering {companylongname} company is it reasonable to investment for now?"
                message['assistant1'] = f"of course. i will help your investment by {advisor} view about the {companylongname}"
                message['user2'] = f"i will give you the company accounting information the 'NVDA' accounting information is {accountinginfo}"
                message['assistant2'] = f"thanks. i will apply that accounting information and utilize them when i invest {companylongname}"
                message['user3'] = f"could you write a report for the {companylongname} company {advisor} style including pros and cons and refer that i gave you the accounting information? by korean"
                
                response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages = [
                                {"role" : "system", "content" : message['system']},
                                {"role" : "user", "content" : message['user1']},
                                {"role" : "assistant", "content" : message['assistant1']},
                                {"role" : "user", "content" : message['user2']},
                                {"role" : "assistant", "content" : message['assistant2']},
                                {"role" : "user", "content" : message['user3']},
                            ],
                            max_tokens=2048,
                            stream=False,
                        )
		
                # report shoot
                if response:
                    waitparagraph.empty()
                    report = response['choices'][0]['message']['content']
                    st.text_area(label = f'{advisor} 의 레포팅입니다', value = report, height=col2height)

    st.download_button(label='download reports', data=report, file_name=f'{advisor} with {companylongname}.txt', mime='text/plain')
except AttributeError:
    st.caption(f'⚠️ 티커가 입력되어있지 않아요. 티커 입력 후 Enter 를 눌러주세요.')
    pass
