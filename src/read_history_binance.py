# ################################## #
# GESTION FICHIER HISTORIQUE BINANCE
# ################################## #

import pandas as pd
import os
import re

def extract_transaction_coin(value):
    transaction_coin = ['EUR', 'USD', 'USDT', 'BTC', 'ETH']
    for item in transaction_coin:
        pattern = item+'$'
        coin = re.sub(r'{}'.format(pattern),"",value)
        if value != coin: break
    return coin, item

path_to_file = r'C:\Users\ALEXIS\Downloads'
filename = "Exporter l'historique des ordres récents.xls"
#filename = 'history_binance.xlsx'

df = pd.read_excel(os.path.join(path_to_file,filename))\
        .rename(columns={'Date(UTC)':'Date','Order Amount':'Nb_tokens', 'AvgTrading Price':'Price_coin',\
                         'Total':'Total_price'})
df.drop(['Order Price','status'],axis=1,inplace=True)
df = df[df['Date'].notnull()]

df['Date'] = pd.to_datetime(df['Date'],format='%Y-%m-%d %H:%M:%S')
df['Coin'], df['Transaction_coin'] = zip(*df.Pair.apply(extract_transaction_coin))

df.sort_values(['Date','Coin']).reset_index(drop=True)


