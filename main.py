import requests
import datetime as dt
from dotenv import load_dotenv
import os


# variables
load_dotenv()
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALPHA_API_KEY = os.getenv("ALPHA_API_KEY")
ALPHA_ENDPOINT = "https://www.alphavantage.co/query"
ALPHA_PARAMETERS = {"function": "TIME_SERIES_DAILY", "symbol": STOCK, "apikey": ALPHA_API_KEY}
today = dt.date.today()
yesterday = today - dt.timedelta(days=1)
two_days_ago = today - dt.timedelta(days=2)
yesterday = str(yesterday)
two_days_ago = str(two_days_ago)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_PARAMETERS = {"q": COMPANY_NAME, "apiKey": NEWS_API_KEY, "pageSize": 3}
BOT_CHAT_ID = os.getenv("BOT_CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_ENDPOINT = "https://api.telegram.org/bot"

# main
response_alfa = requests.get(url=ALPHA_ENDPOINT, params=ALPHA_PARAMETERS)
response_alfa.raise_for_status()
print(response_alfa.status_code)
alpha_data = response_alfa.json()
new_closing_price = alpha_data["Time Series (Daily)"][yesterday]["4. close"]
old_closing_price = alpha_data["Time Series (Daily)"][two_days_ago]["4. close"]
new_closing_price = float(new_closing_price)
old_closing_price = float(old_closing_price)
five_up = 1.01 * old_closing_price
five_down = 0.99 * old_closing_price
# sending notification if value changes by 5%
if five_down >= new_closing_price or new_closing_price >= five_up:
    response_news = requests.get(url=NEWS_ENDPOINT, params=NEWS_PARAMETERS)
    response_news.raise_for_status()
    print(response_news.status_code)
    data = response_news.json()
    selected_articles = data["articles"]
    percentage = (new_closing_price - old_closing_price) * 100 / old_closing_price
    percentage = "{:.2f}".format(percentage)
    if new_closing_price > old_closing_price:
        emoji = "🔺"
    else:
        emoji = "🔻"
    bot_text = ""
    for article_number in range(3):
        headline = selected_articles[article_number]["title"]
        brief = selected_articles[article_number]["content"]
        url = selected_articles[article_number]["url"]
        date = selected_articles[article_number]["publishedAt"].split("T")[0]
        bot_message = f"{STOCK}: {emoji}{percentage}% \n Data: {date} \n Headline: {headline} \n Brief: {brief}\n read it: {url}\n\n"
        bot_text += bot_message
    api_txt_message = BOT_ENDPOINT + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + '&parse_mode=Markdown&text=' + bot_text
    response_telegram = requests.get(api_txt_message)
    response_telegram.raise_for_status()
    print(response_telegram.status_code)