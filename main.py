import time
import requests
import google.generativeai as genai
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup
load_dotenv()


genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')

def get_isin(provided_stock_name):
        url = f'https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&query={provided_stock_name}&type=1&format=json&callback=suggest1'
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        response = requests.get(url)  # , headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract ISIN from the website's HTML structure
        isin_element = soup.find('span')  # Example structure, adjust as per actual website
        isin_element = str(isin_element)
        return (isin_element[6: isin_element.index(",")])

def give_analysis(provided_stock_name, today, one_year_ago):

    isin = get_isin(provided_stock_name)
    time.sleep(5)
    url = f'https://api.upstox.com/v2/historical-candle/NSE_EQ%7C{isin}/day/{today}/{one_year_ago}'
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    # Check the response status
    if response.status_code == 200:
        # Do something with the response data (e.g., print it)
        resp = response.json()
        print(resp)
        resp_transform = {
            "stock_name": provided_stock_name,
            "candles": resp["data"]["candles"]
        }

        pred = model.generate_content(f"Your are stock market expert. You will analyze the data given to you that is {resp_transform}."
                                      f" The data contains the name of the stock. The candle contains the list of data in order."
                                      f" The data in order is date-time, open price, highest price, lowest price, closing price, volume traded, open interest"
                                      f" Give me the detailed analysis of the data provided."
                                      f"Make the response in segments of 1.Overview of the stock. 2.Overall Trend 3.Key Support and Resistance Levels 4.Volatility 5.Volume 6.Based on the current data, we can cautiously observe 7. Disclaimer")
        print(pred.text.replace("**", ""))
    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code} - {response.text}")


isin_number = input("Please provide full name of the stock: ")
today = date.today()
one_year_ago = today - timedelta(days=365)
give_analysis(isin_number, today, one_year_ago)

# example ISIN = INE009A01021