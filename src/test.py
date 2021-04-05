# ############################################################ #
# CONSTRUCTION DU FICHIER EXCEL DE SUIVI DU PORTEFEUILLE CRYPTO
# avec mise en forme du fichier Excel et calculs d'agrégats
# ############################################################ #

import pandas as pd
from src.util import os, path_to_historical_binance, extract_transaction_coin, rolling_calculation, path_to_historical_prices
import numpy as np

# --------------------------------------------------------------------------- #
# Mise en forme de l'historique brut (xls from Binance)
# --------------------------------------------------------------------------- #

df = pd.read_excel(path_to_historical_binance)\
        .rename(columns={'Date(UTC)':'Date','Order Amount':'Nb_tokens', 'AvgTrading Price':'Price_coin',\
                         'Total':'Total_price'})
df.drop(['Order Price','status'],axis=1,inplace=True)
df = df[df['Date'].notnull()]
df[['Nb_tokens','Price_coin']] = df[['Nb_tokens','Price_coin']].astype(float)

df['Date'] = pd.to_datetime(df['Date'],format='%Y-%m-%d %H:%M:%S')
df['Coin'], df['Transaction_coin'] = zip(*df.Pair.apply(extract_transaction_coin))
df = df[df.Coin!='EUR']

df['USD_price_per_coin'] = np.where(df.Transaction_coin.isin(['USDT','USD']), df.Price_coin, np.NaN)
df['Fake_transaction'] = False

#Ajout de "fake" transactions pour les transactions avec Transaction_coin <> USD, USDT
df_not_usd = df[df.Transaction_coin!='USDT'].copy()
df_not_usd['Date'] = df_not_usd['Date'] - pd.Timedelta(1,unit='s')
df_not_usd['Pair'] = df_not_usd['Transaction_coin']+'USDT'
df_not_usd['Coin'] = df_not_usd['Transaction_coin']
df_not_usd['Transaction_coin'] = 'USDT'
df_not_usd['Type'] = 'SELL'
df_not_usd['Fake_transaction'] = True
df_not_usd['Nb_tokens'], df_not_usd['Filled'] = df_not_usd['Total_price'], df_not_usd['Total_price']
df_not_usd['Price_coin'], df_not_usd['Total_price'] = np.NaN, np.NaN

df = pd.concat([df,df_not_usd],axis=0).sort_values(['Date','Coin']).reset_index(drop=True)

# Lecture de la table contenant les prix historiques ETH et BTC
df_historical_prices = pd.read_csv(path_to_historical_prices,sep=';')
df_historical_prices['Date'] = pd.to_datetime(df_historical_prices['Date'],format='%Y-%m-%d %H:%M:%S')

# Filtre sur les achats faits en BTC, ETH ou BNB
df_filtered = df[~df.Transaction_coin.isin(['USDT','USD'])]
df_filtered = pd.merge(df_filtered,df_historical_prices,on=['Date','Transaction_coin'],how='left')
df_filtered['USD_price_per_coin'] = df_filtered['USD_price']*df_filtered['Price_coin']
del df_filtered['USD_price']

# Travail sur les "fake" transactions (pour gérer les achats en ETH, BTC, BNB)
df_filtered_fake = df[df.Fake_transaction]
del df_filtered_fake['USD_price_per_coin']
df_filtered_fake = pd.merge(df_filtered_fake,df_historical_prices.rename(columns={'Transaction_coin':'Coin','USD_price':'USD_price_per_coin'})
                            ,left_on=['Date','Coin'], right_on=['Date','Coin'],how='left')
df_filtered_fake['Total_price'] = df['Nb_tokens']*df['USD_price_per_coin']
df_filtered_fake['Price_coin'] = df['USD_price_per_coin']

# On réintègre les données dans le dataframe df
df = pd.concat([df[df.Transaction_coin.isin(['USDT','USD'])], df_filtered]).sort_values(['Date','Coin']).reset_index(drop=True)
df['USD_total_price'] = df['Nb_tokens']*df['USD_price_per_coin']
df.drop(['Total_price','Filled'],inplace=True, axis=1)

# --------------------------------------------------------------------------- #
# Calcul
# --------------------------------------------------------------------------- #

# Focus sur les achats
# --------------------#

df_buy = df[df.Type=='BUY'].sort_values(['Coin','Date']).reset_index(drop=True)

#Calcul du prix moyen d'achat
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='USD_total_price')
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_buy['AvgPrice_Buy'] = df_buy['USD_total_price_roll_sum']/df_buy['Nb_tokens_roll_sum']
df_buy.drop(['USD_total_price_roll_sum','Nb_tokens_roll_sum'],axis=1,inplace=True) #suppression des champs intermédiaires

# Quantité achetée
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_buy.rename(columns={'Nb_tokens_roll_sum':'Nb_tokens_buy_tot'},inplace=True)

# Date min d'achat de la crypto
df_buy['Date_temp'] = df_buy.Date.values.astype(np.int64)
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='min', rolling_delta_str='360d', var_str='Date_temp')
df_buy['Date_min_buy'] = pd.to_datetime(df_buy['Date_temp_roll_min'])

# Date max d'achat de la crypto
df_buy['Date_temp'] = df_buy.Date.values.astype(np.int64)
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='max', rolling_delta_str='360d', var_str='Date_temp')
df_buy['Date_max_buy'] = pd.to_datetime(df_buy['Date_temp_roll_max'])

df_buy.drop(['Date_temp','Date_temp_roll_min','Date_temp_roll_max'],axis=1,inplace=True)

# Focus sur les achats
# --------------------#

df_sell = df[df.Type=='SELL'].sort_values(['Coin','Date']).reset_index(drop=True)

#Calcul du prix moyen de vente
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='USD_total_price')
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_sell['AvgPrice_sell'] = df_sell['USD_total_price_roll_sum']/df_sell['Nb_tokens_roll_sum']
df_sell.drop(['USD_total_price_roll_sum','Nb_tokens_roll_sum'],axis=1,inplace=True) #suppression des champs intermédiaires

# Quantité vendue
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_sell.rename(columns={'Nb_tokens_roll_sum':'Nb_tokens_sell_tot'},inplace=True)

# Date min d'achat de la crypto
df_sell['Date_temp'] = df_sell.Date.values.astype(np.int64)
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='min', rolling_delta_str='360d', var_str='Date_temp')
df_sell['Date_min_sell'] = pd.to_datetime(df_sell['Date_temp_roll_min'])

# Date max de vente de la crypto
df_sell['Date_temp'] = df_sell.Date.values.astype(np.int64)
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='max', rolling_delta_str='360d', var_str='Date_temp')
df_sell['Date_max_sell'] = pd.to_datetime(df_sell['Date_temp_roll_max'])

df_sell.drop(['Date_temp','Date_temp_roll_min','Date_temp_roll_max'],axis=1,inplace=True)

# Concaténation
# --------------------#

df_tot = pd.concat([df_buy,df_sell],axis=0).sort_values(by=['Date','Coin','Type']).reset_index(drop=True)
df_tot = df_tot.groupby('Coin').fillna(method='ffill')
df_tot['Current_price'] = '=RECHERCHEV(@F:F&"USDT";Cours_Cryptos!A:C;3;FAUX)'

# --------------------------------------------------------------------------- #
# Travail sur les observations avec transaction_coin <> USD, USDT
# --------------------------------------------------------------------------- #

df_not_usd = df_tot[df_tot.Transaction_coin!='USDT']
