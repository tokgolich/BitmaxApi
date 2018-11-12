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

    def __init__(self, base_url = 'https://bitmax.io/', base_path = 'api/v1/'):
        self.base_url = base_url
        self.base_path = base_path

    def auth(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret

    def public_request(self, method, api_url, **payload):
        """request public url"""
        full_url = self.base_url + self.base_path + api_url
        try:
            r = requests.request(method, full_url, params=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except requests.exceptions.ConnectionError as err:
            return False, {'error': 'E10001', 'data': err}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def signed_request(self, method, api_url, api_path, coid = None, account_group = None, **payload):
        """request a signed url"""
        if account_group is None:
            full_url = self.base_url + self.base_path + api_url
        else:
            full_url = self.base_url + str(account_group) + '/' + self.base_path + api_url
        ts = utc_timestamp()
        #coid = uuid32()
        headers = make_auth_header(ts, api_path, self.api_key, self.secret, coid)

        try:
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
        return self.public_request('GET', 'assets')

    def get_all_products(self):
        """List all products"""
        return self.public_request('GET', 'products')

    def get_current_fees(self):
        """Get Current Trading Fees"""
        return self.public_request('GET', 'fees')

    def get_market_ticker(self, symbol):
        """Market Quote (Level 1 Order Book Data) of One Product"""
        return self.public_request('GET', f'quote?symbol={symbol}')

    def get_market_depth(self, symbol, n):
        """Market Depth (Level 2 Order Book Data) of One Product"""
        return self.public_request('GET', 'depth', symbol=symbol, n=n)

    def get_market_trades(self, symbol, n):
        """Market Trades"""
        return self.public_request('GET', 'trades', symbol=symbol, n=n)

    def get_user_info(self):
        """User Info"""
        return self.signed_request('GET', 'user/info', 'user/info')

    def get_all_balance(self, account_group):
        """List all Balances"""
        return self.signed_request('GET', 'balance', 'balance', account_group = account_group)

    def get_one_balance(self, account_group, asset):
        """Get Balance of one Asset"""
        return self.signed_request('GET', f'balance/{asset}', 'balance', account_group=account_group)

