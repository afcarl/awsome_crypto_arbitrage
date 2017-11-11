
import pandas as pd
import json
from bs4 import BeautifulSoup
import requests
from helper import ExganceInfo, fetch_data_daily_by_exchange, fetch_data_hour_by_exchange, ensure_dir
from os.path import join as path_join


grey = .6, .6, .6
TOP_N = 10
# define a pair
fsym = "ETH"
tsym = "USD"



url = "https://www.cryptocompare.com/api/data/coinsnapshot/?fsym=" + fsym + "&tsym=" + tsym
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
# get currency data
dic = json.loads(soup.prettify())
# print currency data
# print(json.dumps(dic, indent=4, sort_keys=True))
# extract excange info
market = [ExganceInfo(excange["MARKET"], round(float(excange['VOLUME24HOUR']),2)) for excange in dic["Data"]["Exchanges"]]
market = sorted(market, key=lambda d: -d.volume)
for excange_info in market:
    print("{}\t{}".format(excange_info.market, excange_info.volume))

# download daily OHLC price-series for ETH/USD for a given 'market'
# extract close-price (cp)
print("{}/{}".format(fsym, tsym))
good_market_name = []

data = pd.DataFrame()
for market in map(lambda m: m.market, market):
    print("{}".format(market), end="")
    df = fetch_data_hour_by_exchange(fsym, tsym, market)
    df = df[(df.index > "2017-06-01") & (df.index <= "2017-11-05")]
    if df.shape[0] != 0:
        df.name = market
        df.to_csv(ensure_dir(path_join("./data", "{}_hourly.csv".format(market))))
        data = pd.concat([data, df], axis=1, ignore_index=False)
        print("\tdownloaded")
        good_market_name.append(market)
        if len(good_market_name) == 10:
            break
    else:
        print("\tskipp")

print(good_market_name)
print(data.head(10))
print(data.tail(10))