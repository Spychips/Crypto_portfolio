# ############################################################ #
# CONSTRUCTION DU FICHIER EXCEL DE SUIVI DU PORTEFEUILLE CRYPTO
# avec mise en forme du fichier Excel et calculs d'agrégats
# ############################################################ #

import pandas as pd
from src.util import os, path_to_data, filename_history_binance_post_treatments

df = pd.read_excel(os.path.join(path_to_data, filename_history_binance_post_treatments))
df.sort_values(by=['Coin','Date'],inplace=True)

# Calcul de la rentabilité

"""
Le calcul doit se faire à chaque observation avec SELL 
"""