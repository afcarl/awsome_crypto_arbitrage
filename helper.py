from collections import namedtuple
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import os
from torch.autograd import Variable
ExganceInfo = namedtuple("ExganceInfo", ["market", "volume"])
CombinationInfo = namedtuple("CombinationInfo", ["market_1", "market_2", "mean", "std"])
OpenTradePrice = namedtuple("OpenTradePrice", ["open_price", "open_asset"])

def repackage_hidden(h):
    """Wraps hidden states in new Variables, to detach them from their history."""
    if type(h) == Variable:
        return Variable(h.data)
    else:
        return tuple(repackage_hidden(v) for v in h)


def fetch_data_by_exchange(fswym, tsym, exchange, time_to, time_frame="hour"):
    """
    Get hourly data from cryptocompare
    :param fswym: From Symbol
    :param tsym: To Symbols
    :param exchange: Name of exchange
    :return:
    """
    url = "https://min-api.cryptocompare.com/data/histo{}?fsym={}&tsym={}&limit=2000&e={}&toTs={}".\
        format(time_frame, fswym, tsym, exchange, time_to)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())
    next_time_to = dic["TimeFrom"] - 1
    date = np.array([datetime.utcfromtimestamp(int(info["time"])).strftime('%Y-%m-%d %H:%M:%S') for info in dic["Data"]])
    data = pd.DataFrame.from_dict(dic["Data"])
    data.index = pd.to_datetime(date)

    return data.astype(np.float32), next_time_to

def fetch_data_daily_by_exchange(fsym, tsym, exchange):
    """
    Get daily data from cryptocompare
    :param fswym: From Symbol
    :param tsym: To Symbols
    :param exchange: Name of exchange
    """
    url = "https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&allData=1&e={}".format(fsym, tsym,
                                                                                                   exchange)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())
    date = np.array([datetime.fromtimestamp(int(info["time"])).strftime('%Y-%m-%d') for info in dic["Data"]])
    data = pd.DataFrame.from_dict(dic["Data"])
    data.index = pd.to_datetime(date)

    return data.astype(np.float32)


def ensure_dir(file_path):
    '''
    Used to ensure the creation of a directory when needed
    :param file_path: path to the file that we want to create
    '''
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return file_path