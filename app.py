from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.agents import tool
from langchain.prompts import PromptTemplate
from langchain import OpenAI

import statistics
import os
import requests
from bs4 import BeautifulSoup

import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

import streamlit as st

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
url = st.text_input("Enter rightmove link", "")
url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E116&maxBedrooms=3&minBedrooms=3&maxPrice=325000&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords="


@tool
def get_median_price(url=url) -> str:
    """Gets the median house price from the supplied Rightmove URL"""

    # Get the page

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
    response = requests.get(url, headers=headers)

    # Scrape the content

    soup = BeautifulSoup(response.text, "html.parser")

    props = soup.find_all("div", class_="l-searchResult is-list")

    all_prices = []
    for i in range(len(props)):
        prop = props[i]
        price = (
            prop.find("div", class_="propertyCard-priceValue")
            .get_text()
            .replace(",", "")
            .strip("£")
            .strip()
        )
        all_prices.append(int(price))

    res = round(statistics.median(all_prices), 2)

    return str(res)


@tool
def get_mean_price(url=url) -> str:
    """Gets the mean house price from the supplied Rightmove URL"""

    # Get the page

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
    response = requests.get(url, headers=headers)

    # Scrape the content

    soup = BeautifulSoup(response.text, "html.parser")

    apartments = soup.find_all("div", class_="l-searchResult is-list")

    all_prices = []
    for i in range(len(apartments)):
        apartment_no = apartments[i]
        price = (
            apartment_no.find("div", class_="propertyCard-priceValue")
            .get_text()
            .replace(",", "")
            .strip("£")
            .strip()
        )
        all_prices.append(int(price))

    res = round(statistics.mean(all_prices), 2)

    return str(res)


# Create the agent to use the tool
tools = [get_median_price, get_mean_price]

agent = initialize_agent(
    tools, llm, agent="chat-zero-shot-react-description", verbose=True
)


prompt = PromptTemplate(
    input_variables=["calctype"],
    template="""
            You have been given access to search data from Rightmove. 
            Please calculate the {calctype} based on the response using the {calctype} tool.         
           """,
)

if st.button("Get Summary"):
    # run the agent
    result = agent.run(prompt.format_prompt(calctype="mean"))

    st.write(result)
