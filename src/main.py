# ############################################################ #
# CONSTRUCTION DU FICHIER EXCEL DE SUIVI DU PORTEFEUILLE CRYPTO
# avec mise en forme du fichier Excel et calculs d'agrégats
# ############################################################ #

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
print('IMPORT DU TEMPLATE')
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

writer = pd.ExcelWriter(os.path.join(path_to_data,'Suivi_portefeuille_{}.xlsx'.format(date_jour)),engine='openpyxl')
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

OSTPair = 'OSTUSDT'
OSTCoin = 'OST'
OSTTransaction_coin = 'USDT'
OSTCurrentPrice = df_binance_cryptos.loc[df_binance_cryptos['Pair']=='OSTBTC','CurrentPrice'].values*df_binance_cryptos.loc[df_binance_cryptos['Pair']=='BTCUSDT','CurrentPrice'].values
OSTPriceChange = df_binance_cryptos.loc[df_binance_cryptos['Pair']=='OSTBTC','PriceChange24hr'].values*df_binance_cryptos.loc[df_binance_cryptos['Pair']=='BTCUSDT','PriceChange24hr'].values

ost_df = pd.DataFrame({'Pair':OSTPair,'Coin':OSTCoin,'Transaction_coin':OSTTransaction_coin,'CurrentPrice':OSTCurrentPrice,'PriceChange24hr':OSTPriceChange})
df_binance_cryptos = pd.concat([df_binance_cryptos,ost_df], axis=0).reset_index(drop=True)

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

# Lecture de la table contenant les prix historiques ETH et BTC
df_historical_prices = pd.read_csv(path_to_historical_prices,sep=';')
df_historical_prices['Date'] = pd.to_datetime(df_historical_prices['Date'],format='%Y-%m-%d %H:%M:%S')

# --------------------------------------------------------------------------- #
# Mise en forme de l'historique brut (xls from Binance)
# --------------------------------------------------------------------------- #

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

# Ajout manuel de l'achat d'ATOM


# Changement pour le PUNDIX
for i in ['Nb_tokens','Filled']:
    df.loc[df.Coin=='NPXS',i] = df[i]/1000
df.loc[df.Coin=='NPXS','Price_coin'] = df['Price_coin']*1000
df.loc[df.Coin=='NPXS','Coin'] = 'PUNDIX'
df.loc[df.Coin=='PUNDIX','Pair'] = df['Coin'] + df['Transaction_coin']

df['USD_price_per_coin'] = np.where(df.Transaction_coin.isin(['USDT','USD']), df.Price_coin, np.NaN)
df['Fake_transaction'] = False

#Ajout de "fake" transactions pour les transactions avec Transaction_coin <> USD, USDT
df_fake_transactions = df[df.Transaction_coin!='USDT'].copy()
df_fake_transactions['Date'] = df_fake_transactions['Date'] - pd.Timedelta(1,unit='s')
df_fake_transactions['Pair'] = df_fake_transactions['Transaction_coin']+'USDT'
df_fake_transactions['Coin'] = df_fake_transactions['Transaction_coin']
df_fake_transactions['Transaction_coin'] = 'USDT'
df_fake_transactions['Type'] = 'SELL'
df_fake_transactions['Fake_transaction'] = True
df_fake_transactions['Nb_tokens'], df_fake_transactions['Filled'] = df_fake_transactions['Total_price'], df_fake_transactions['Total_price']
df_fake_transactions['Price_coin'], df_fake_transactions['Total_price'] = np.NaN, np.NaN
del df_fake_transactions['USD_price_per_coin']
df_fake_transactions = pd.merge(df_fake_transactions,df_historical_prices.rename(columns={'Transaction_coin':'Coin','USD_price':'USD_price_per_coin'})
                            ,left_on=['Date','Coin'], right_on=['Date','Coin'],how='left')
df_fake_transactions['Total_price'] = df_fake_transactions['Nb_tokens']*df_fake_transactions['USD_price_per_coin']
df_fake_transactions['Price_coin'] = df_fake_transactions['USD_price_per_coin']


# Filtre sur les opérations effectuées hors USD et USDT
df_filtered = df[~df.Transaction_coin.isin(['USDT','USD'])]
df_filtered = pd.merge(df_filtered,df_historical_prices,on=['Date','Transaction_coin'],how='left')
df_filtered['USD_price_per_coin'] = df_filtered['USD_price']*df_filtered['Price_coin']
del df_filtered['USD_price']

# On réintègre les données dans le dataframe df
df = pd.concat([df[df.Transaction_coin.isin(['USDT','USD'])], df_filtered, df_fake_transactions]).sort_values(['Date','Coin']).reset_index(drop=True)
df['USD_total_price'] = df['Nb_tokens']*df['USD_price_per_coin']

# var_to_keep = ['Date','Coin','Type', 'Nb_tokens', 'USD_price_per_coin', 'USD_total_price']
# df = df[var_to_keep]
df.drop(['Total_price','Filled'],inplace=True, axis=1)
# df = df[~df.Coin.isin(['OST','ONT'])].sort_values(['Coin','Date']).reset_index(drop=True)
df = df.sort_values(['Coin','Date']).reset_index(drop=True)

# Calcul du nombre d'achats / ventes
df['temp'] = df.groupby(['Coin','Type']).cumcount()+1 #var temporaire
df['Nombre_achats'] = np.where(df.Type=='BUY', df['temp'], None)
df['Nombre_achats'] = df.groupby('Coin')['Nombre_achats'].fillna(method='ffill').fillna(0).astype(np.int16)
df['Nombre_ventes'] = np.where(df.Type=='SELL', df['temp'], None)
df['Nombre_ventes'] = df.groupby('Coin')['Nombre_ventes'].fillna(method='ffill').fillna(0).astype(np.int16)
del df['temp']

# On slipt en deux types de champs pour distinguer les ventes des achats
df['Quantite_achetee'] = np.where(df.Type=='BUY', df.Nb_tokens, np.NaN)
df['Quantite_vendue'] = np.where(df.Type=='SELL', df.Nb_tokens, np.NaN)
df['Prix_achat'] = np.where(df.Type=='BUY', df.USD_price_per_coin, np.NaN)
df['Prix_vente'] = np.where(df.Type=='SELL', df.USD_price_per_coin, np.NaN)
df['Montant_achat'] = np.where(df.Type=='BUY', df.USD_total_price, np.NaN)
df['Montant_vente'] = np.where(df.Type=='SELL', df.USD_total_price, np.NaN)

# # Suppression de champs
# df.drop(['Nb_tokens', 'USD_price_per_coin', 'USD_total_price', 'Type'], axis=1, inplace=True)

# Quantité achetée totale jusqu'à date
df['Quantite_achetee_totale'] = df.groupby('Coin').Quantite_achetee.cumsum()
df['Quantite_achetee_totale'] = df.groupby('Coin').Quantite_achetee_totale.fillna(method='ffill')

# Quantité vendue totale jusqu'à date
df['Quantite_vendue_totale'] = df.groupby('Coin').Quantite_vendue.cumsum()
df['Quantite_vendue_totale'] = df.groupby('Coin').Quantite_vendue_totale.fillna(method='ffill').fillna(0)

# Quantité possédée totale jusqu'à date
df['Quantite_possedee_totale'] = df['Quantite_achetee_totale'] - df['Quantite_vendue_totale']

# Quantité totale achetée (exprimée en $)
df['Montant_achat_total'] = df.groupby('Coin').Montant_achat.cumsum()
df['Montant_achat_total'] = df.groupby('Coin').Montant_achat_total.fillna(method='ffill').fillna(0)

# Quantité totale vendue (exprimée en $)
df['Montant_vente_total'] = df.groupby('Coin').Montant_vente.cumsum()
df['Montant_vente_total'] = df.groupby('Coin').Montant_vente_total.fillna(method='ffill').fillna(0)

# Prix moyens
df['Prix_moyen_achat'] = df['Montant_achat_total']/df['Quantite_achetee_totale']
df['Prix_moyen_vente'] = df['Montant_vente_total']/df['Quantite_vendue_totale']

# Calcul de la plus value réalisée en vendant
df['temp'] = ((df['Prix_vente'] - df['Prix_moyen_achat'])*df['Quantite_vendue'])
df['Plus_value_vente_en_$'] = df.groupby('Coin')['temp'].cumsum().fillna(method='ffill').fillna(0)
del df['temp']

# # Suppression de champs
# df.drop(['Quantite_achetee', 'Quantite_vendue', 'Prix_achat', 'Prix_vente', 'Montant_achat', 'Montant_vente'], axis=1, inplace=True)
# #

# --------------------------------------------------------------------------- #
# Enregistrement dans l'onglet
# --------------------------------------------------------------------------- #

details_cols = ['Date', 'Coin', 'Type', 'Pair', 'Transaction_coin']
details_achats_cols = ['Quantite_achetee', 'Prix_achat', 'Montant_achat']
details_ventes_cols = ['Quantite_vendue', 'Prix_vente', 'Montant_vente']
achats_agg_cols = ['Quantite_achetee_totale', 'Montant_achat_total', 'Prix_moyen_achat', 'Nombre_achats']
ventes_agg_cols = ['Quantite_vendue_totale', 'Montant_vente_total', 'Prix_moyen_vente', 'Nombre_ventes']
others_agg_cols = ['Quantite_possedee_totale', 'Plus_value_vente_en_$']

cols = details_cols + details_achats_cols + details_ventes_cols + achats_agg_cols + ventes_agg_cols + others_agg_cols
df = df[cols].sort_values(['Date','Coin'])

df.to_excel(writer,sheetname_historique_transactions,startcol=0,startrow=3,index=False,header=False)

# ########################################################################### #
# Onglet vision agrégée par crypto
# ########################################################################### #

var_to_keep = ['Coin', 'Quantite_possedee_totale', 'Plus_value_vente_en_$', 'Prix_moyen_achat', 'Prix_moyen_vente', 'Nombre_achats', 'Nombre_ventes']
df_agg = df[var_to_keep].groupby('Coin').tail(1)

#Ajout price actuel + évolution sur 24h
df_agg['temp'] = df_agg['Coin']+'USDT'
df_agg = pd.merge(df_agg, df_binance_cryptos[['Pair','PriceChange24hr','CurrentPrice']],left_on='temp', right_on='Pair')
df_agg.drop(['Pair','temp'],axis=1,inplace=True)

#Ajout des dates pour la première et dernière transaction
a = pd.DataFrame(df.groupby("Coin").Date.min()).rename(columns ={'Date':'Date_min'})
b = pd.DataFrame(df.groupby("Coin").Date.min()).rename(columns ={'Date':'Date_max'})
df_agg = df_agg.set_index('Coin')
df_agg = pd.concat([df_agg,a,b], axis = 1).reset_index().rename(columns ={'index':'Coin'})
del [a,b]

df_agg['Valeur_actuelle_qte_possedee'] = df_agg['Quantite_possedee_totale']*df_agg['CurrentPrice']
df_agg['Cout_qt_possedee'] = df_agg['Quantite_possedee_totale']*df_agg['Prix_moyen_achat']
df_agg['Variation_qt_possedee'] = df_agg['Valeur_actuelle_qte_possedee'] - df_agg['Cout_qt_possedee']
df_agg['Variation_qt_possedee_%'] = 100*(df_agg['Valeur_actuelle_qte_possedee'] - df_agg['Cout_qt_possedee'])/df_agg['Cout_qt_possedee']

var_to_keep = ['Coin', 'Variation_qt_possedee','Variation_qt_possedee_%', 'Plus_value_vente_en_$', 'CurrentPrice', 'PriceChange24hr',
               'Prix_moyen_achat', 'Prix_moyen_vente', 'Quantite_possedee_totale', 'Nombre_achats', 'Nombre_ventes','Date_min','Date_max']

#Suppression temporaire pour la crypto OST
#df_agg = df_agg[df_agg.Coin!='OST']

df_agg['temp'] = df_agg['Quantite_possedee_totale']*df_agg['CurrentPrice'] #Pour trier la table

df_agg.sort_values('temp',ascending=False)[var_to_keep].to_excel(writer,sheetname_report,startcol=0,startrow=1,index=False,header=False)


# ########################################################################### #
# Enregistrement du fichier Excel
# ########################################################################### #

if __name__ == '__main__':
    writer.save()