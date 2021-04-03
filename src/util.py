import re
import os

# Fonction pour split COIN et Transaction coin (Ex : ETHUSDT -> ETH et USDT)
def extract_transaction_coin(value):
    transaction_coin = ['EUR', 'USD', 'USDT', 'BTC', 'ETH', 'BNB', 'USDC']
    for item in transaction_coin:
        pattern = item+'$'
        coin = re.sub(r'{}'.format(pattern),"",value)
        if value != coin: break
        else: coin, item = None, None
    return coin, item

path_to_project = r'C:\Users\ALEXIS\PycharmProjects\Crypto_portfolio'
path_to_data = os.path.join(path_to_project,'data')

#Pour l'historique de trading Binance
binance_filename = "Exporter l'historique des ordres récents.xls"
path_to_historical_binance = os.path.join(r'C:\Users\ALEXIS\Downloads',binance_filename)
filename_history_binance_post_treatments = 'history_binance_post_treatments.xlsx'

# Pour enregistrer les prix actuels (en USDT, ETH, BTC, EUR) de toutes les cryptos dispo sur Binance
filename_current_prices_all_binance_cryptos = "current_prices_binance_cryptos.xlsx"

#Pour l'historique de transferts d'€ sur Binance
binance_deposits = "Exporter l'historique des dépôts.xlsx"
path_to_deposits_binance = os.path.join(r'C:\Users\ALEXIS\Downloads',binance_deposits)
filename_deposits_binance_post_treatments = 'deposits_binance_post_treatments.xlsx'

# Pour les prix ETH, BTC
historical_prices_filename = 'historical_prices.txt'
path_to_historical_prices = os.path.join(path_to_data,historical_prices_filename)