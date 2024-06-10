# scrape news from https://it.cointelegraph.com/
# and send them via telegram
# check every minute and send via telegram if there is a new news
import time
import json
import asyncio
import telegram
import configparser
import requests
from bs4 import BeautifulSoup

# get the html content of the page
url = 'https://cointelegraph.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}
jsonNewsFile = 'en_cointelegraph.json'
 
# telegram token and chat id
# create a config.ini file with the following content
# [main]
# my_token = your_token (without quotes: 49358973534)
# my_chat_id = your_chat_id (without quotes: 548743)
# where your_token and your_chat_id are the token and chat id of your bot
config = configparser.ConfigParser()
config.read('config.ini')
my_token = config['main']['my_token']
my_chat_id = config['main']['my_chat_id']


def find_differences(list1, list2):
    #find the differences between two lists of news
    for i in range(min(len(list1), len(list2))):
        if list1[i]['title'] == list2[0]['title']:
            if i > 0:
                return list1[:i]
            else:
                return []

async def tg_send_async(news_list):
    for i in reversed(news_list): # send the news in reverse order, the last sended is the recent one
       await send(msg=(f'{i['title']} \n {i['link']}'), chat_id=my_chat_id, token=my_token)



async def send(msg, chat_id, token=my_token):
    """
    Send a message "msg" to a telegram user or group specified by "chat_id"
    msg         [str]: Text of the message to be sent. Max 4096 characters after entities parsing.
    chat_id [int/str]: Unique identifier for the target chat or username of the target channel (in the format @channelusername)
    token       [str]: Bot's unique authentication token.
    """
    bot = telegram.Bot(token=token)
    await bot.sendMessage(chat_id=chat_id, text=msg)
    print('Message Sent!')


while True: # search for news every 1 minute
    response = requests.get(url, headers=headers)
    page = response
    soup = BeautifulSoup(page.content, 'html.parser')
    news = soup.find_all('div', class_='post-card')
    news_list = []
    for n in news:
        title = n.find('span', class_='post-card__title').text
        date = n.find('time').text
        link = url + n.find('a')['href']
        news_list.append({'title': title, 'date':date, 'link':link})

    async def process_news ():
        try:
            with open(jsonNewsFile, 'r') as file:
                old_news = json.load(file)
            if news_list != old_news:
                differences = find_differences(news_list, old_news)
                with open(jsonNewsFile, 'w') as file:
                    json.dump(news_list, file)
                await tg_send_async(differences)
        except:
            with open(jsonNewsFile, 'w') as file:
                json.dump(news_list, file)
            await tg_send_async(news_list)
    asyncio.run(process_news())
    time.sleep(60)
