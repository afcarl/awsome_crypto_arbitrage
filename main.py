from __future__ import absolute_import
from __future__ import print_function

import numpy as np
import pandas as pd
import argparse
from scipy import stats
from os.path import join as path_join
from helper import CombinationInfo
import itertools
from model import ManulaStrategy
from visdom import Visdom
from datetime import datetime

MARKETS = ['Bitfinex', 'Coinbase', 'Poloniex', 'Gemini', 'Kraken', 'BitTrex', 'HitBTC', 'Cexio', 'Quoine', 'Exmo']
BASE_DIR = "./data"
TIME_FRAME = "daily"
fsym = "ETH"
tsym = "USD"
EXP_NAME = "exp-{}".format(datetime.now())


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


def plot_timeseries(data, market_1, market_2, exp_name):
    viz.line(
        Y=np.concatenate((np.expand_dims(data[market_1].values, 1), np.expand_dims(data[market_2].values, 1)), axis=1),
        X=np.array([range(data[market_1].shape[0]), range(data[market_2].shape[0])]).T,
        opts=dict(legend=[market_1, market_2],
                  title="Correlation: {}-{}".format(market_1, market_2),
                  showlegend=True,
                  x_label=fsym,
                  y_label=tsym,
                  width=800,
                  height=400,
                  markers=True,
                  markersize=4),
        win="Correlation{}".format(exp_name))


if __name__ == '__main__':
    viz = Visdom()

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


    market_1 = "Exmo"
    market_2 = "Kraken"

    assert(data[market_1].shape[0] == data[market_2].shape[0])  # both sizes must be equal
    plot_timeseries(data, market_1, market_2, EXP_NAME)


    model = ManulaStrategy(10000, data, market_1, market_2)
    model.manual_strategy(0, viz, EXP_NAME)


