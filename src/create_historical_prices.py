import pandas as pd
from src.util import export_file, path_to_historical_prices, path_to_data, historical_prices_filename

df = pd.read_csv(path_to_historical_prices,sep=';')

df_tot = pd.concat([df,df_not_usd[['Date','Coin']].rename(columns={'Coin':'Transaction_coin'})],axis=0)
export_file(df_tot, path_to_data, historical_prices_filename)


