# ################################## #
# CHARGEMENT COURS ACTUEL DES CRYPTOS
# ################################## #

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
#from openpyxl import load_workbook

coins, tokens, prices = [], [], []

for i in range(1,60):

    print('Working on page {}...'.format(i))
    url = 'https://www.coingecko.com/fr?page={}'.format(i)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    extract_coins = soup.findAll("a", class_="d-none d-lg-flex font-bold align-items-center justify-content-between")
    text_coin = [re.sub("\n", "", elem.text) for elem in extract_coins]
    coins.append(text_coin)

    extract_tokens = soup.findAll("span", class_="d-none d-lg-inline font-normal text-3xs ml-2")
    text_token = [re.sub("\n", "", elem.text) for elem in extract_tokens]
    tokens.append(text_token)

    extract_prices = soup.findAll("td", class_="td-price price text-right")
    text_prices = [float(re.sub("\n", "", elem.text).replace(" ", "").replace("$", "").replace(",", ".")) for elem in extract_prices]
    prices.append(text_prices)

df_crypto_cours = pd.DataFrame({'Coin':sum(coins,[]), 'Token':sum(tokens,[]), 'Price_US$':sum(prices,[])})

# book = load_workbook('Portfolio.xlsx')
# writer = pd.ExcelWriter('Portfolio.xlsx', engine='openpyxl')
# writer.book = book
#
# writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
#
# df_crypto_cours.to_excel(writer, "Cours")
#
# writer.save()