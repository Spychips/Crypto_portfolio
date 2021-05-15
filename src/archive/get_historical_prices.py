
from src.util import *
import pandas as pd
import numpy as np
import requests

df = pd.read_excel(path_to_historical_binance)\
        .rename(columns={'Date(UTC)':'Date','Order Amount':'Nb_tokens', 'AvgTrading Price':'Price_coin',\
                         'Total':'Total_price'})
df = df[df.status=="Filled"]
df.drop(['Order Price','status'],axis=1,inplace=True)
df = df[(df['Date'].notnull()) & (df['Filled']!=0)]
df[['Nb_tokens','Price_coin']] = df[['Nb_tokens','Price_coin']].astype(np.float64)

df['Date'] = pd.to_datetime(df['Date'],format='%Y-%m-%d %H:%M:%S')
df['Coin'], df['Transaction_coin'] = zip(*df.Pair.apply(extract_transaction_coin))

df = df[~df.Coin.isin(['EUR'])]

# Filtre sur les opérations effectuées hors USD et USDT
df_filtered = df.loc[~df.Transaction_coin.isin(['USDT','USD']),['Date','Transaction_coin']]
df_filtered['Date_timestamp'] = (df_filtered['Date'].values.astype(np.int64) / 10**9).astype(np.int64)


def get_historical_price(coin, date):
    json_response = requests.get("https://min-api.cryptocompare.com/data/pricehistorical?fsym=USD&tsyms={0}&ts={1}&api_key=aaf62a0d97e5eaecf9b891d0f4346ff11b24eaf795a4b5d3105df5dc0a8590a6%22".format(coin, date)).json()
    usd_price = json_response.get("USD").get(coin)**-1
    return usd_price

df_filtered['USD_price'] = df_filtered.apply(lambda x : get_historical_price(x.Transaction_coin,x.Date_timestamp),axis=1)

"""
Pas suffisamment précis...
"""