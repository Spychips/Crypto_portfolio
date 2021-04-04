# ################################## #
# RECUPERATION DES INFOS SUR LES CRYPTOS (celles dispo sur Binance)
# ################################## #

import requests
import pandas as pd
from src.util import extract_transaction_coin, path_to_data, filename_current_prices_all_binance_cryptos, export_file

json_response = requests.get('https://api.binance.com/api/v3/ticker/24hr').json()
json_response = [{k : v for k, v in i.items() if k in ['symbol','lastPrice','priceChangePercent']} for i in json_response]

df_binance_cryptos = pd.DataFrame(json_response).rename(columns={'symbol':'Pair','priceChangePercent':'PriceChange24hr','lastPrice':'CurrentPrice'})
df_binance_cryptos[['PriceChange24hr','CurrentPrice']] = df_binance_cryptos[['PriceChange24hr','CurrentPrice']].astype(float)

df_binance_cryptos['Coin'], df_binance_cryptos['Transaction_coin'] = zip(*df_binance_cryptos.Pair.apply(extract_transaction_coin))

# Export du fichier
export_file(df_binance_cryptos, path_to_data, filename_current_prices_all_binance_cryptos)
