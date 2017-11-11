from __future__ import absolute_import
from __future__ import print_function

import numpy as np
import pandas as pd
import argparse
from scipy import stats
from matplotlib import pyplot as plt
from os.path import join as path_join
from helper import CombinationInfo
import itertools

MARKETS = ['Bitfinex', 'Coinbase', 'Poloniex', 'Gemini', 'Kraken', 'BitTrex', 'HitBTC', 'Cexio', 'Quoine', 'Exmo']
BASE_DIR = "./data"
TIME_FRAME = "daily"

def load_data(dir, exchange):
    """
    load csv data
    :param dir: base directory
    :param exchange: file_name
    :return:
    """
    df = pd.read_csv(path_join(dir, "{}_{}.csv".format(exchange, TIME_FRAME)), index_col=0)["close"]
    df.name = exchange
    return df

def compute_stats(market_1, market_2):
    """
    Compute mean and std of 2 time-series
    :param market_1: name of market1
    :param market_2: name of market2
    :return:
    """
    market_data_1 = data[market_1]
    market_data_2 = data[market_2]
    diff = np.abs(market_data_1 - market_data_2)
    avg = np.mean(diff)
    std = np.std(diff, ddof=1)
    return CombinationInfo(market_1, market_2, avg, std)


if __name__ == '__main__':
    data = pd.DataFrame()
    for market in MARKETS:
        df = load_data(BASE_DIR, "{}".format(market))
        data = pd.concat([data, df], axis=1, ignore_index=False)

    combinations = []
    for market_1, market_2 in itertools.combinations(MARKETS, 2):
        combinations.append(compute_stats(market_1, market_2))

    combinations = sorted(combinations, key=lambda x: -x.mean)

    print("{: ^10s}{: ^10s}{: ^10s}{: ^10s}".format("Coin1", "Coin2", "Mean", "Std Dev"))
    for e in combinations:
        print("{: ^10s}{: ^10s}{: ^10.2f}{: ^10.2f}".format(e[0], e[1], e[2], e[3]))