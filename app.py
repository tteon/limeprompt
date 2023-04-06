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
	st.markdown(body = img_to_html(img_path='img/기업어때_Icon500x500_favicon_2.png' , width= 100, height = 100), unsafe_allow_html=True)
with col2:
	st.markdown(f"<h1 style='font-size:20px margin-top:30px'>안녕하세요. 투자대가와 분석할 기업을 선택해주세요.</h1>", unsafe_allow_html=True)

# investors 
investors = {
    'warrenbuffett': {
        'pros': "Buffett's value investing strategy has a long history of success, and he is widely regarded as one of the most successful investors of all time. His focus on high-quality companies with strong competitive advantages and management teams has resulted in significant long-term gains for his investment firm, Berkshire Hathaway.",
        'cons': "Buffett's approach can be difficult to replicate for individual investors, as it requires a deep understanding of a company's fundamentals and competitive landscape. Additionally, Buffett's approach is often criticized for being too focused on established, large-cap companies, which can limit potential returns."
    },
    'peterlynch': {
        'pros': "Lynch's 'buy what you know' approach is appealing for individual investors, as it emphasizes investing in companies that you are familiar with and understand. His focus on companies with strong fundamentals and growth potential has also proven successful in many cases.",
        'cons': "Lynch's approach can be risky for individual investors who do not have a deep understanding of a company's underlying business. Additionally, Lynch's focus on growth stocks can lead to volatility and potentially significant losses in market downturns."
    },
    'benjamingraham': {
        'pros': "Graham's value investing approach is widely regarded as a sound strategy for long-term investors. His emphasis on fundamental analysis and metrics such as price-to-earnings ratio and price-to-book ratio can help identify undervalued stocks.",
        'cons': "Graham's approach can be time-consuming and requires a significant amount of research and analysis. Additionally, his focus on buying stocks at a discount to their intrinsic value can limit potential returns in a rapidly growing market."
    },
    'raydalio': {
        'pros': "Dalio's 'all-weather' portfolio strategy is appealing for investors who are looking to minimize risk and volatility. His focus on diversification across different asset classes and geographies can help reduce risk in a portfolio.",
        'cons': "Dalio's approach can be difficult to implement for individual investors, as it requires access to a wide range of investment options and a significant amount of capital. Additionally, his focus on macroeconomic trends can lead to missed opportunities in individual stocks or sectors."
    },
    'georgesoros': {
        'pros': "Soros's focus on macroeconomic trends and his ability to make large, successful bets on currency markets has resulted in significant gains for his investment firm, Soros Fund Management.",
        'cons': "Soros's approach can be risky for individual investors, as it requires a significant amount of expertise in currency markets and a willingness to take large risks. Additionally, his focus on market reflexivity can lead to a self-fulfilling prophecy, as market participants may adjust their beliefs and actions based on Soros's actions."
    },
    'johnpaulson': {
        'pros': "Paulson's focus on identifying macroeconomic trends and making bets on specific sectors or assets has resulted in significant gains in the past, such as his successful bet against the subprime mortgage market in 2007.",
        'cons': "Paulson's approach can be risky for individual investors, as it requires a significant amount of expertise in macroeconomic trends and sector-specific knowledge. Additionally, his approach can be subject to significant market volatility, as evidenced by his recent losses in the gold market."
    }
}

# user input##################################################################################

advisor = st.selectbox(
    '투자대가를 선택해주세요.',
    (investors.keys()),
    label_visibility='visible')
if advisor:
    st.markdown(f"<p style='color: #6482FF; font-size: 10px'>{advisor}을 고르셨군요! {advisor}의 특징을 확인해보세요.</p>", unsafe_allow_html=True)

with st.expander('투자대가의 조언'):

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
                waitparagraph.text_area(label = f"그거 알고 계신가요?", placeholder= f"레포팅을 이용해서 투자일지를 적을 수 있는 공간이 있는데요." , height=col2height)

                # accounting information ##########
                accountingitem = 'income_statement'
                accountinginfo = loadcompanyinformation(company=companylongname,item=accountingitem)
                
                # prompt scenario #################
                message = defaultdict()
                message['system'] = f'you are the {advisor} advisor for help investment people who didnt know well the accounting information. so you should help him by {advisor} manner and view.'
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
                    report = paragraph_preprocessing(response['choices'][0]['message']['content'])
                    st.text_area(label = f'{advisor} 의 레포팅입니다', value = report, height=col2height)

    st.download_button(label='Download file', data=report, file_name=f'{advisor} with {companylongname}.txt', mime='text/plain')
except AttributeError:
    st.caption(f'⚠️ 티커가 입력되어있지 않아요. 티커 입력 후 Enter 를 눌러주세요.')
    pass
