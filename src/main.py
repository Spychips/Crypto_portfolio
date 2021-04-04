# ############################################################ #
# CONSTRUCTION DU FICHIER EXCEL DE SUIVI DU PORTEFEUILLE CRYPTO
# avec mise en forme du fichier Excel et calculs d'agrégats
# ############################################################ #

import pandas as pd
from src.util import *
import requests
import pandas as pd
from openpyxl import load_workbook
from datetime import date
import numpy as np

date_jour = date.today().strftime('%Y%m%d')

# ########################################################################### #
# ########################################################################### #
#  IMPORT DU TEMPLATE (fichier Excel de reporting mis en forme mais sans les données)
# ########################################################################### #
# ########################################################################### #

print('\n==========================================')
print('\n')
print('IMPORT DU TEMPLATE')
print('\n')
print('==========================================\n')

book = load_workbook(os.path.join(path_to_data,filename_template_excel))

# ########################################################################### #
# ########################################################################### #
#  CREATION DU REPORTING DU JOUR MIS EN FORME
# ########################################################################### #
# ########################################################################### #

print('\n==========================================')
print('CREATION DU REPORTING DU JOUR MIS EN FORME')
print('==========================================\n')

writer = pd.ExcelWriter(os.path.join(path_to_data,'Suivi_portefeuille_{}.xlsx'.format(date_jour)),engine='openpyxl',datetime_format='DD/MM/YYYY')
writer.book = book

# #Rename onglet "Statistiques_YYYYMMDD" :
# sheet = book['Statistiques_YYYYMMDD']
# sheet.title = 'Statistiques_{}'.format(date_jour)

#Création du fichier Excel (reprenant donc les onglets du template pour avoir la mise en forme)
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

# ########################################################################### #
# Onglet sur le cours actuel des cryptos ("Cours_Cryptos")
# ########################################################################### #

sheet = book[sheetname_cours_cryptos]

# --------------------------------------------------------------------------- #
# Récupération par API des prix actuels du marché (sur l'API Binance)
# --------------------------------------------------------------------------- #

json_response = requests.get('https://api.binance.com/api/v3/ticker/24hr').json()
json_response = [{k : v for k, v in i.items() if k in ['symbol','lastPrice','priceChangePercent']} for i in json_response]

df_binance_cryptos = pd.DataFrame(json_response).rename(columns={'symbol':'Pair','priceChangePercent':'PriceChange24hr','lastPrice':'CurrentPrice'})
df_binance_cryptos[['PriceChange24hr','CurrentPrice']] = df_binance_cryptos[['PriceChange24hr','CurrentPrice']].astype(float)

df_binance_cryptos['Coin'], df_binance_cryptos['Transaction_coin'] = zip(*df_binance_cryptos.Pair.apply(extract_transaction_coin))

# --------------------------------------------------------------------------- #
# Ajout dans l'onglet
# --------------------------------------------------------------------------- #

df_binance_cryptos.to_excel(writer,sheetname_cours_cryptos,startcol=0,startrow=1,index=False,header=False)

# ########################################################################### #
# Onglet sur l'historique des dépôts sur Binance
# ########################################################################### #

# --------------------------------------------------------------------------- #
# Mise en forme Mise en forme de l'historique brut (xls from Binance)
# --------------------------------------------------------------------------- #

df_deposits = pd.read_excel(path_to_deposits_binance,usecols=['Date(UTC)','Amount']).rename(columns={'Date(UTC)':'Date','Amount':'EUR_amount'})
df_deposits['USDT_amount'] = float(requests.get('https://api.binance.com/api/v3/ticker/price?symbol=EURUSDT').json()['price'])*df_deposits['EUR_amount']

# --------------------------------------------------------------------------- #
# Enregistrement dans l'onglet
# --------------------------------------------------------------------------- #

df_deposits.to_excel(writer,sheetname_deposits_euros,startcol=0,startrow=1,index=False,header=False)

# ########################################################################### #
# Onglet sur l'historique des transactions sur Binance
# ########################################################################### #

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

# --------------------------------------------------------------------------- #
# Enregistrement dans l'onglet
# --------------------------------------------------------------------------- #

df.to_excel(writer,sheetname_historique_transactions,startcol=0,startrow=1,index=False,header=False)

# ########################################################################### #
# Enregistrement du fichier Excel
# ########################################################################### #

if __name__ == '__main__':
    writer.save()