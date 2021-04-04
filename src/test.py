# ############################################################ #
# CONSTRUCTION DU FICHIER EXCEL DE SUIVI DU PORTEFEUILLE CRYPTO
# avec mise en forme du fichier Excel et calculs d'agrégats
# ############################################################ #

import pandas as pd
from src.util import os, path_to_data, filename_history_binance_post_treatments, rolling_calculation

df = pd.read_excel(os.path.join(path_to_data, filename_history_binance_post_treatments))

# ################### #
# Focus sur les achats
# ################### #

df_buy = df[df.Type=='BUY'].sort_values(['Coin','Date']).reset_index(drop=True)

#Calcul du prix moyen d'achat
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='USD_total_price')
_, df_buy = rolling_calculation(df_Init=df_buy, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_buy['AvgPrice_Buy'] = df_buy['USD_total_price_roll_sum']/df_buy['Nb_tokens_roll_sum']
df_buy.drop(['USD_total_price_roll_sum','Nb_tokens_roll_sum'],axis=1,inplace=True) #suppression des champs intermédiaires

# ################### #
# Focus sur les ventes
# ################### #

df_sell = df[df.Type=='BUY'].sort_values(['Coin','Date']).reset_index(drop=True)

#Calcul du prix moyen de vente
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='USD_total_price')
_, df_sell = rolling_calculation(df_Init=df_sell, index_str='Date', var_group_str='Coin', agg_str='sum', rolling_delta_str='360d', var_str='Nb_tokens')
df_sell['AvgPrice_Sell'] = df_sell['USD_total_price_roll_sum']/df_sell['Nb_tokens_roll_sum']
df_sell.drop(['USD_total_price_roll_sum','Nb_tokens_roll_sum'],axis=1,inplace=True) #suppression des champs intermédiaires

# Calcul de la rentabilité

"""
- Le calcul doit se faire à chaque observation avec SELL 
- Ajouter ligne SELL quand échange COIN contre ETH ou BTC
"""
