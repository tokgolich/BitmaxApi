#coding:utf-8
from pprint import pprint
from API.bitmax import *

if __name__ == "__main__":

    btmx = Bitmax()
    btmx.auth("api-key", "secret")
    pprint(btmx.get_current_fees())
    pprint(btmx.get_market_ticker("ETH-BTC"))
    pprint(btmx.get_market_depth("ETH-BTC", 5))
    account_group = btmx.get_user_info()[1]["accountGroup"]
    print(account_group)
    pprint(btmx.get_all_balance(account_group))
    pprint(btmx.get_one_balance(account_group, "BTMX"))
