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

def paragraph_preprocessing(paragraph):
    # Remove any line breaks and extra white space
    paragraph = re.sub(r'\s+', ' ', paragraph)

    # Remove any empty strings
    paragraph = list(filter(None, paragraph.split(' ')))

    # Join the paragraph back into a string
    paragraph = ' '.join(paragraph)
    return paragraph


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
        'pros': "버핏의 가치 투자 전략은 오랜 성공의 역사를 가지고 있으며, 그는 역사상 가장 성공적인 투자자 중 한 명으로 널리 여겨집니다. 강력한 경쟁 우위와 경영진을 보유한 고품질 기업에 집중한 그의 투자 회사인 Berkshire Hathaway는 상당한 장기적 이익을 얻었습니다.",
        'cons': "Buffet의 접근 방식은 기업의 기본 원리와 경쟁 환경에 대한 깊은 이해가 필요하기 때문에 개인 투자자들에게 복제하기 어려울 수 있습니다. 게다가, 버핏의 접근 방식은 종종 기존의 대형 회사에 너무 집중하여 잠재적인 수익을 제한할 수 있다는 비판을 받습니다."
    },
    'peterlynch': {
        'pros': "Lynch의 '당신이 아는 것을 사세요' 접근법은 당신이 친숙하고 이해하는 회사에 투자하는 것을 강조하기 때문에 개인 투자자들에게 매력적입니다. 강력한 기반과 성장 잠재력을 가진 기업에 집중한 그의 노력은 많은 경우에도 성공적인 것으로 입증되었습니다.",
        'cons': "Lynch의 접근 방식은 회사의 기본 비즈니스에 대한 깊은 이해가 없는 개인 투자자들에게 위험할 수 있습니다. 또한, 성장주에 대한 린치의 집중은 변동성과 잠재적으로 시장 침체에서 상당한 손실을 초래할 수 있습니다."
    },
    'benjamingraham': {
        'pros': "그레이엄의 가치 투자 접근법은 장기 투자자들을 위한 건전한 전략으로 널리 간주됩니다. 그가 주가수익률, 주가수익률 등 근본적인 분석과 지표를 강조하는 것은 저평가된 종목을 파악하는 데 도움이 될 수 있습니다.",
        'cons': "그레이엄의 접근 방식은 시간이 많이 걸릴 수 있으며 상당한 양의 연구와 분석이 필요합니다. 게다가, 그가 본질적인 가치를 할인하여 주식을 사는 것에 집중하는 것은 빠르게 성장하는 시장에서 잠재적인 수익을 제한할 수 있습니다."
    },
    'raydalio': {
        'pros': "Dalio의 '전천후' 포트폴리오 전략은 위험과 변동성을 최소화하려는 투자자들에게 매력적입니다. 다양한 자산 클래스와 지역에 걸친 다양화에 중점을 둔 그의 노력은 포트폴리오의 리스크를 줄이는 데 도움이 될 수 있습니다.",
        'cons': "Dalio의 접근 방식은 광범위한 투자 옵션과 상당한 자본을 필요로 하기 때문에 개인 투자자들에게 구현하기 어려울 수 있습니다. 또한 거시 경제 동향에 대한 그의 집중은 개별 주식이나 부문에서 기회를 놓치는 결과를 초래할 수 있습니다."
    },
    'georgesoros': {
        'pros': "소로스는 금융계에서 폭넓은 인맥을 보유하고 있어 귀중한 정보와 통찰력에 접근할 수 있습니다. 마지막으로, 소로스는 사회적으로 책임 있는 투자자들에게 어필할 수 있는 자선 사업과 사회적 행동주의로도 유명합니다.",
        'cons': "소로스는 시장을 조작하고 그의 재산을 정치에 영향을 미치기 위해 사용한 혐의를 받고 있는 논란이 많은 인물입니다. 소로스 펀드 운용사는 민간투자회사로 보유주식이나 투자전략을 외부에 공개하지 않아 일부 투자자들의 고민거리가 될 수 있습니다."
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

with st.expander('투자자 소개'):

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
