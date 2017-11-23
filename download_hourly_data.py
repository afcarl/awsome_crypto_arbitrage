
import pandas as pd
import json
import requests
from helper import ExganceInfo, fetch_data_daily_by_exchange, fetch_data_by_exchange, ensure_dir
from os.path import join as path_join


grey = .6, .6, .6
TOP_N = 10
# define a pair
FSYM = "ETH"
TSYM = "USD"
MARKETS = ['Bitfinex', 'Coinbase', 'Poloniex', 'Gemini', 'Kraken', 'BitTrex', 'HitBTC', 'Cexio', 'Quoine', 'Exmo']
DATE_START = 1511337600
DATE_END = 1510732800
LIMIT = 2000

def get_data(container, time):
    df, time_to = fetch_data_by_exchange(FSYM, TSYM, market, time, time_frame="minute")
    container.append(df)
    return df.shape[0], time_to

for market in MARKETS:
    print("{}".format(market), end="")
    dfs = []

    num_row, time = get_data(dfs, DATE_START)
    while num_row > LIMIT:
        num_row, time = get_data(dfs, time)

    data = pd.concat(dfs).sort_index().drop_duplicates("time")
    data.to_csv(ensure_dir(path_join("./data", "{}_minute.csv".format(market))))
    print("\tdownloaded")
