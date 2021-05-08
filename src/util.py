import re
import os
import pickle
import pandas as pd

# Fonction pour split COIN et Transaction coin (Ex : ETHUSDT -> ETH et USDT)
def extract_transaction_coin(value):
    transaction_coin = ['EUR', 'USD', 'USDT', 'BTC', 'ETH', 'BNB', 'USDC']
    for item in transaction_coin:
        pattern = item+'$'
        coin = re.sub(r'{}'.format(pattern),"",value)
        if value != coin: break
        else: coin, item = None, None
    return coin, item


# Pour exporter le dataframe
def export_file(df, output_path, output_filename, output_extensions='NotDefined'):
    if len(output_filename.split('.'))==2:
        output_extensions = output_filename.split('.')[1]
        output_filename = output_filename.split('.')[0]
    if isinstance(output_extensions, str): output_extensions = [output_extensions]  # Pour éviter de déclarer une liste si on souhaite enregistrer le fichier qu'à un seul format
    output_extensions = [i.lower() for i in output_extensions]
    for ext in output_extensions:
        output_filename_ext = '{0}.{1}'.format(output_filename, ext)
        if ext.lower() not in ['csv', 'txt', 'xlsx', 'pkl', 'sav']: raise ValueError('Extension "{}" non reconnue.'.format(ext))
        if ext.lower() in ['csv', 'txt']:
            df.to_csv(os.path.join(output_path, output_filename_ext), index=False, sep=';')
        elif ext.lower() == 'xlsx':
            df.to_excel(os.path.join(output_path, output_filename_ext), index=False, engine='openpyxl')
        elif ext.lower() in ['pkl', 'sav']:
            pickle.dump({output_filename_ext: df},
                        open(os.path.join(output_path, output_filename_ext), 'wb'))
        print('Fichier "{}" généré.'.format(output_filename_ext))


def rolling_calculation(df_Init, index_str, var_group_str, agg_str, rolling_delta_str, var_str):
    rolling = df_Init.reset_index().set_index(index_str).groupby(var_group_str).rolling(rolling_delta_str).agg({var_str:agg_str}).reset_index()
    rolling = rolling[var_str].reset_index()
    rolling.rename(columns={var_str:var_str+"_roll_"+agg_str}, inplace=True)
    rolling.drop(columns=['index'], inplace = True)
    print(rolling.columns)
    df_result = pd.concat([df_Init, rolling], axis=1)
    return rolling, df_result

path_to_project = r'C:\Users\ALEXIS\PycharmProjects\Crypto_portfolio'
path_to_data = os.path.join(path_to_project,'data')

#Pour l'historique de trading Binance
binance_filename = "Exporter l'historique des ordres récents.xlsx"
path_to_historical_binance = os.path.join(r'C:\Users\ALEXIS\Downloads',binance_filename)
filename_history_binance_post_treatments = 'history_binance_post_treatments.xlsx'

# Pour enregistrer les prix actuels (en USDT, ETH, BTC, EUR) de toutes les cryptos dispo sur Binance
filename_current_prices_all_binance_cryptos = "current_prices_binance_cryptos.sav"

#Pour l'historique de transferts d'€ sur Binance
binance_deposits = "Exporter l'historique des dépôts.xlsx"
path_to_deposits_binance = os.path.join(r'C:\Users\ALEXIS\Downloads',binance_deposits)
filename_deposits_binance_post_treatments = 'deposits_binance_post_treatments.xlsx'

# Pour les prix ETH, BTC
historical_prices_filename = 'historical_prices.txt'
path_to_historical_prices = os.path.join(path_to_data,historical_prices_filename)

# Template Excel
filename_template_excel = 'template_portfolio_v6.xlsx'
sheetname_report = 'Historique par crypto'
sheetname_cours_cryptos = 'Cours_Cryptos'
sheetname_historique_transactions = 'Historique des transactions'
sheetname_deposits_euros = 'Historique_EUR'