#coding:utf-8
import hmac
import hashlib
import requests
import base64
import random, string
from datetime import datetime

def uuid32():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))

def utc_timestamp():
    tm = datetime.utcnow().timestamp()
    return int(tm * 1e3)

def make_auth_header(timestamp, api_path, api_key, secret, coid=None):
    # convert timestamp to string
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode("utf-8")
    elif isinstance(timestamp, int):
        timestamp = str(timestamp)

    if coid is None:
        msg = bytearray(f"{timestamp}+{api_path}".encode("utf-8"))
    else:
        msg = bytearray(f"{timestamp}+{api_path}+{coid}".encode("utf-8"))

    hmac_key = base64.b64decode(secret)
    signature = hmac.new(hmac_key, msg, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")
    header = {
        "x-auth-key": api_key,
        "x-auth-signature": signature_b64,
        "x-auth-timestamp": timestamp,
    }

    if coid is not None:
        header["x-auth-coid"] = coid

    return header

class Bitmax():

    def __init__(self, base_url = 'https://bitmax.io/'):
        self.base_url = base_url

    def auth(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def public_request(self, method, base_path, payload = None):
        """request public url"""
        full_url = self.base_url + base_path
        try:
            if method == "GET":
                r = requests.request(method, full_url, params=payload)
            else:
                r = requests.request(method, full_url, json=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except requests.exceptions.ConnectionError as err:
            return False, {'error': 'E10001', 'data': err}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def signed_request(self, method, base_path, api_path, ts, coid = None, payload = None):
        """request a signed url"""
        full_url = self.base_url + base_path
        headers = make_auth_header(ts, api_path, self.api_key, self.secret, coid)

        try:
            if method == "GET":
                r = requests.request(method, full_url, headers=headers, params=payload)
            else:
                r = requests.request(method, full_url, headers=headers, json=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except requests.exceptions.HTTPError as err:
            return False, {'error': 'E10001', 'data': err}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def get_all_assets(self):
        """List of all assets"""
        return self.public_request('GET', 'api/v1/assets')

    def get_all_products(self):
        """List all products"""
        return self.public_request('GET', 'api/v1/products')

    def get_current_fees(self):
        """Get Current Trading Fees"""
        return self.public_request('GET', 'api/v1/fees')

    def get_market_ticker(self, symbol):
        """Market Quote (Level 1 Order Book Data) of One Product"""
        return self.public_request('GET', f'api/v1/quote?symbol={symbol}')

    def get_market_depth(self, symbol, n):
        """Market Depth (Level 2 Order Book Data) of One Product"""
        params = {
            "symbol": symbol,
            "n": n
        }
        return self.public_request('GET', 'api/v1/depth', params)

    def get_market_trades(self, symbol, n):
        """Market Trades"""
        params = {
            "symbol": symbol,
            "n": n
        }
        return self.public_request('GET', 'api/v1/trades', params)

    def get_all_products_24h(self):
        """24-hour Rolling Statistics of All Products"""
        return self.public_request('GET', 'api/v1/ticker/24hr')

    def get_one_products_24h(self, symbol):
        """24-hour Rolling Statistics of All Products"""
        return self.public_request('GET', f'api/v1/ticker/24hr?symbol={symbol}')

    def get_bar_history_info(self):
        """Bar History Info"""
        return self.public_request('GET', 'api/v1/barhist/info')

    def get_bar_history_data(self, symbol, start, end, interval):
        """Bar History Data"""
        params = {
            "symbol": symbol,
            "from": start,
            "to": end,
            "interval": interval
        }
        return self.public_request('GET', 'api/barhist', params)

    def get_user_info(self):
        """User Info"""
        ts = utc_timestamp()
        return self.signed_request('GET', 'api/v1/user/info', 'user/info', ts)

    def get_all_balance(self, account_group):
        """List all Balances"""
        ts = utc_timestamp()
        return self.signed_request('GET', f'{account_group}/api/v1/balance', 'balance', ts)

    def get_one_balance(self, account_group, asset):
        """Get Balance of one Asset"""
        ts = utc_timestamp()
        return self.signed_request('GET', f'{account_group}/api/v1/balance/{asset}', 'balance', ts)

    def creat_new_order(self, account_group, symbol, price, quantity, order_type, side):
        """Place a New Order"""
        ts = utc_timestamp()
        coid = uuid32()
        params = dict(
            coid=coid,
            time=ts,
            symbol=symbol.replace("-", "/"),
            orderPrice=str(price),
            orderQty=str(quantity),
            orderType=order_type,
            side=side.lower()
        )
        return self.signed_request('POST', f'{account_group}/api/v1/order', 'order', ts, coid=coid, payload=params)

    def cancel_one_order(self, account_group, symbol, orig_coid):
        """Cancel an Order"""
        ts = utc_timestamp()
        coid = uuid32()
        params = dict(
            coid=coid,
            time=ts,
            symbol=symbol.replace("-", "/"),
            origCoid = orig_coid
        )
        return self.signed_request('DELETE', f'{account_group}/api/v1/order', 'order', ts, coid=coid, payload=params)

    def cancel_all_open_order(self, account_group, symbol = None):
        """Cancel All Open Orders"""
        ts = utc_timestamp()
        if symbol is not None:
            return self.signed_request('DELETE', f'{account_group}/api/v1/order/all?symbol={symbol.replace("-", "/")}', 'order/all', ts)
        else:
            return self.signed_request('DELETE', f'{account_group}/api/v1/order/all', 'order/all', ts)

    def get_all_open_orders(self, account_group):
        """List of All Open Orders"""
        ts = utc_timestamp()
        return self.signed_request('GET', f'{account_group}/api/v1/order/open', 'order/open', ts)

    def get_history_orders(self, account_group, start, end, symbol, n):
        """List Historical Orders"""
        ts = utc_timestamp()
        params = dict(
            startTime=start,
            endTime=end,
            symbol=symbol,
            n = n
        )
        return self.signed_request('GET', f'{account_group}/api/v1/order/history', 'order/history', ts, payload=params)

    def get_one_order(self, account_group, coid):
        """Get Basic Order Data of One Order"""
        ts = utc_timestamp()
        return self.signed_request('GET', f'{account_group}/api/v1/order/{coid}', 'order', ts)

    def get_fills_one_order(self, account_group, coid):
        """Get Fills of One Order"""
        ts = utc_timestamp()
        return self.signed_request('GET', f'{account_group}/api/v1/order/fills/{coid}', 'order/fills', ts)

