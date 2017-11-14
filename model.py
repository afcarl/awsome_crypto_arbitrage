from helper import OpenTradePrice
import numpy as np

class ManulaStrategy(object):
    def __init__(self, initial_investment, data, market_1, market_2):
        self.initial_investment = initial_investment
        self.ts_1, self.ts_2 = data[market_1], data[market_2]
        self.market_1, self.market_2 = market_1, market_2
        self.account_1, self.account_2 = initial_investment/ 2, initial_investment/ 2  # USD
        self.position = 0.5 * (initial_investment/ 2)  # USD

        self.roi = []
        self.ac_1_history = [self.account_1]
        self.ac_2_history = [self.account_2]
        self.money = [self.account_1 + self.account_2]

        # trading_price
        self.open_1 = OpenTradePrice(0., "")
        self.open_2 = OpenTradePrice(0., "")
        self.trade_number = 0
        #signals
        self.trade = False
        self.new_trade = False

    def __open_new_position__(self, p1, p2, asset1, asset2):
        """
        Open new trading position
        :param p1: price ts1
        :param p2: price ts2
        :param asset1: LONG/SHORT on ts1
        :param asset2: LONG/SHORT on ts2
        :return:
        """
        assert (asset1 != asset2)
        assert (asset1 in ["LONG", "SHORT"])
        assert (asset2 in ["LONG", "SHORT"])

        self.open_1 = OpenTradePrice(p1, asset1)
        self.open_2 = OpenTradePrice(p2, asset2)
        self.trade = True
        self.new_trade = False
        self.trade_number += 1
        print("{: ^10.2f}{: ^10.2f}{: ^10s}{: ^10s}{: ^10d}".format(p1, p2, asset1, asset2, self.trade), end="")

    def __print_trading_summary__(self):
        """
        Print the summary of the current trade
        :return:
        """
        # return on investment (ROI)
        total = self.account_1 + self.account_2
        self.roi.append(total / self.initial_investment - 1)
        self.ac_1_history.append(self.account_1)
        self.ac_2_history.append(self.account_2)
        self.money.append(total)
        print("ROI = ", self.roi[-1])
        print("trade closed\n")

    def __plot_trading_summary__(self, update, viz, exp_name):
        viz.line(
            Y=np.array([[self.account_1, self.account_2]]),
            X=np.array([[self.trade_number, self.trade_number]]),
            opts=dict(legend=[self.market_1, self.market_2],
                      title="Accounts cash level",
                      showlegend=True,
                      x_label="Trade No.",
                      y_label="USD",
                      width=400,
                      height=400,
                      markers=True,
                      markersize=2),
            win="Account_Cash_level{}".format(exp_name),
            update=update
        )

        viz.line(
            Y=np.array([self.money[-1]]),
            X=np.array([self.trade_number]),
            opts=dict(legend=["Total cash"],
                      title="Total cash obtained",
                      showlegend=True,
                      x_label="Trade No.",
                      y_label="USD",
                      width=400,
                      height=400,
                      markers=True,
                      markersize=2),
            win="Total_Cash_level{}".format(exp_name),
            update=update
        )
        return "append"


    def manual_strategy(self, transaction_cost, viz, exp_name):
        """
        Backtesting Stat Arb trading strategy for ETH/USD at Exmo and Kraken cryptocurrency exchanges
        :param initial_investment: initial amount of money in USD
        :return:
        """
        self.__plot_trading_summary__(None, viz, exp_name)
        # running the backtest
        for i, (p1, p2) in enumerate(zip(self.ts_1, self.ts_2)):
            if p1 > p2:
                asset1 = "SHORT"
                asset2 = "LONG"
                if not self.trade:
                    self.__open_new_position__(p1, p2, asset1, asset2)
                    print("----first trade info")
                    continue
                elif asset1 == self.open_1.open_asset:
                    self.new_trade = False  # flag
                elif asset1 == self.open_2.open_asset:
                    self.new_trade = True  # flag

            elif p2 > p1:
                asset1 = "LONG"
                asset2 = "SHORT"
                if not self.trade:
                    self.__open_new_position__(p1, p2, asset1, asset2)
                    print("----first trade info")
                    continue
                elif asset1 == self.open_1.open_asset:
                    self.new_trade = False  # flag
                elif asset1 == self.open_2.open_asset:
                    self.new_trade = True  # flag

            if self.new_trade:
                # close current position
                if self.open_1.open_asset == "SHORT":
                    # PnL of both trades
                    pnl_asset1 = ((self.open_1.open_price / p1) - 1) - transaction_cost
                    pnl_asset2 = ((p2 / self.open_2.open_price) - 1) - transaction_cost
                    print(
                        "trade summary:{: ^10.2f}{: ^10.2f}{: ^10.2f}{: ^10.2f}{: ^10s}{: ^10s}{: ^10.2f}{: ^10.2f}"
                        .format(self.open_1.open_price, p1, self.open_2.open_price, p2, self.open_1.open_asset, self.open_2.open_asset, pnl_asset1, pnl_asset2))
                    # update both accounts
                    self.account_1 += self.position * pnl_asset1
                    self.account_2 += self.position * pnl_asset2
                    print("accounts [USD] = {: ^10.2f}{: ^10.2f}".format(self.account_1, self.account_2))
                    if ((self.account_1 <= 0) or (self.account_2 <= 0)):
                        print("--trading halted")
                        break

                # close current position
                elif self.open_1.open_asset == "LONG":
                    # PnL of both trades
                    pnl_asset1 = ((p1 / self.open_1.open_price) - 1) - transaction_cost
                    pnl_asset2 = ((self.open_2.open_price / p2) - 1) - transaction_cost
                    print(
                        "trade summary:{: ^10.2f}{: ^10.2f}{: ^10.2f}{: ^10.2f}{: ^10s}{: ^10s}{: ^10.2f}{: ^10.2f}"
                            .format(self.open_1.open_price, p1, self.open_2.open_price, p2, self.open_1.open_asset,
                                    self.open_2.open_asset, pnl_asset1, pnl_asset2))
                    # update both accounts
                    self.account_1 += self.position * pnl_asset1
                    self.account_2 += self.position * pnl_asset2
                    print("accounts [USD] = {: ^10.2f}{: ^10.2f}".format(self.account_1, self.account_2))
                    if ((self.account_1 <= 0) or (self.account_2 <= 0)):
                        print("--trading halted")
                        break


                self.__plot_trading_summary__("append", viz, exp_name)
                self.__print_trading_summary__()
                self.__open_new_position__(p1, p2, asset1, asset2)
                print("----new trade info")

            else:
                print("{: ^10.2f}{: ^10.2f}{: ^10s}{: ^10s}{: ^10d}".format(p1, p2, asset1, asset2, self.new_trade))




