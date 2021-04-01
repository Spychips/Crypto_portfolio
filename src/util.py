import re
import os

# Fonction pour split COIN et Transaction coin (Ex : ETHUSDT -> ETH et USDT)
def extract_transaction_coin(value):
    transaction_coin = ['EUR', 'USD', 'USDT', 'BTC', 'ETH']
    for item in transaction_coin:
        pattern = item+'$'
        coin = re.sub(r'{}'.format(pattern),"",value)
        if value != coin: break
    return coin, item

path_to_project = r'C:\Users\ALEXIS\PycharmProjects\Crypto_portfolio'
path_to_data = os.path.join(path_to_project,'data')

#Pour l'historique Binance
binance_filename = "Exporter l'historique des ordres récents.xls"
path_to_historical_binance = os.path.join(r'C:\Users\ALEXIS\Downloads',binance_filename)

# Pour les prix ETH, BTC
historical_prices_filename = 'historical_prices.txt'
path_to_historical_prices = os.path.join(path_to_data,historical_prices_filename)