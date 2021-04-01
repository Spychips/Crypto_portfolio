# ################################## #
# GESTION FICHIER HISTORIQUE BINANCE
# ################################## #

from src.util import *
import pandas as pd
import requests
import numpy as np

df = pd.read_excel(path_to_historical_binance)\
        .rename(columns={'Date(UTC)':'Date','Order Amount':'Nb_tokens', 'AvgTrading Price':'Price_coin',\
                         'Total':'Total_price'})
df.drop(['Order Price','status'],axis=1,inplace=True)
df = df[df['Date'].notnull()]
df[['Nb_tokens','Price_coin']] = df[['Nb_tokens','Price_coin']].astype(float)

df['Date'] = pd.to_datetime(df['Date'],format='%Y-%m-%d %H:%M:%S')
df['Coin'], df['Transaction_coin'] = zip(*df.Pair.apply(extract_transaction_coin))
df = df[df.Coin!='EUR']

# Récupération des prix actuels du marché
dict_prices = {}
for elem in df.Pair.unique():
    print('Working on {}...'.format(elem))
    json_response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol={}'.format(elem)).json()
    dict_prices[json_response['symbol']] = float(json_response['price'])

df['USD_current_coin_price'] = df.Pair.map(dict_prices)
df['USD_price_per_coin'] = np.where(df.Transaction_coin.isin(['USDT','USD']), df.Price_coin, np.NaN)


# Lecture de la table contenant les prix historiques ETH et BTC
df_historical_prices = pd.read_csv(path_to_historical_prices,sep=';')
df_historical_prices['Date'] = pd.to_datetime(df_historical_prices['Date'],format='%Y-%m-%d %H:%M:%S')

# Filtre sur les opérations effectuées hors USD et USDT
df_filtered = df[~df.Transaction_coin.isin(['USDT','USD'])]
df_filtered = pd.merge(df_filtered,df_historical_prices,on=['Date','Transaction_coin'],how='left')
df_filtered['USD_price_per_coin'] = df_filtered['USD_price']*df_filtered['Price_coin']
del df_filtered['USD_price']

# On réintègre les données dans le dataframe df
df = pd.concat([df[df.Transaction_coin.isin(['USDT','USD'])], df_filtered]).sort_values(['Date','Coin']).reset_index(drop=True)
df['USD_total_price'] = df['Nb_tokens']*df['USD_price_per_coin']
df.drop(['Total_price','Filled'],inplace=True, axis=1)

# Enregistrement du fichier
filename = 'history_binance_post_treatments.xlsx'
df.to_excel(os.path.join(path_to_data,filename),index=False)