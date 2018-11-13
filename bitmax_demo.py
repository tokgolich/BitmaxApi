#coding:utf-8
import time
from pprint import pprint
from bitmax import *

if __name__ == "__main__":

    btmx = Bitmax()
    btmx.auth("api-key", "secret")
    #pprint(btmx.get_current_fees())
    #pprint(btmx.get_market_ticker("ETH-BTC"))
    #pprint(btmx.get_market_depth("ETH-BTC", 5))
    #tm = int(time.time()) * 1000
    #pprint(btmx.get_bar_history_data("ETH-BTC", tm - 60000, tm - 300000, 1))
    account_group = btmx.get_user_info()[1]["accountGroup"]
    print(account_group)
    #pprint(btmx.get_all_balance(account_group))
    time.sleep(1)
    #pprint(btmx.get_one_balance(account_group, "BTMX"))
    #pprint(btmx.creat_new_order(account_group, "ETH-BTC", "0.03", "1", "limit", "sell"))
    #pprint(btmx.cancel_one_order(account_group, "ETH-BTC", "12345"))
    #pprint(btmx.cancel_all_open_order(account_group))
    #pprint(btmx.cancel_all_open_order(account_group, symbol="ETH-BTC"))
    #pprint(btmx.get_all_open_orders(account_group))
    #pprint(btmx.get_fills_one_order(account_group, "1234"))

