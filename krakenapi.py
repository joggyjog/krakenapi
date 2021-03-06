import httplib2
import urllib
import json
import hmac
import base64
import hashlib
import time

class krakenapi:

    def __init__(self):
        self.key = ''
        self.secret = ''
        self.signature = ''
        self.uri = 'https://api.kraken.com'
        
    def load_key(self):
        f = open('kraken.key', 'r')
        self.key = f.readline().strip()
        f.close()

    def load_secret(self):
        f = open('kraken.secret', 'r')
        self.secret = f.readline().strip()
        f.close()
        
    def sign(self, path, nonce, data):
        key = base64.b64decode(self.secret.encode())
        digestmod = hashlib.sha512
        msg = path.encode() + hashlib.sha256(nonce.encode() + data.encode()).digest()
        self.signature = base64.b64encode(hmac.new(key, msg, digestmod).digest())

    def public_request(self, method, body={}):
        h = httplib2.Http()
        resp, content = h.request(self.uri + '/0/public/' + method, 'POST', body=urllib.parse.urlencode(body));
        if resp['status'] == '200':
            data = json.loads(content.decode())
            if data['error'] == []:
                return(data['result'])
            print('[ERROR] => ' + method + ': ' + data['error'][0])
        return(None)

    def get_server_time(self):
        data = self.public_request('Time')
        if data:
            return(data['unixtime'], data['rfc1123'])
        return(None, None)

    def get_asset_info(self, info='info', aclass='currency', asset=None):
        body = {}
        body['info'] = info
        body['aclass'] = aclass
        if asset:
            body['asset'] = asset
        data = self.public_request('Assets', body)
        if data:
            return(data)
        return(None)

    def get_tradable_asset_pairs(self, info='info', pair=None):
        body = {}
        body['info'] = info
        if pair:
            body['pair'] = info
        data = self.public_request('AssetPairs', body)
        if data:
            return(data)
        return(None)

    def get_ticker_information(self, pair):
        body = {'pair': pair}
        data = self.public_request('Ticker', body)
        if data:
            return(data)
        return(None)

    def get_balance(self):
        path = '/0/private/Balance'
        nonce = int(time.time() * 1000)
        body = {
            'nonce': str(nonce)
            }
        self.sign(path, str(nonce), urllib.parse.urlencode(body))
        headers = {
            'API-Key': self.key,
            'API-Sign': self.signature.decode()
            }
        h = httplib2.Http()
        resp, content = h.request(self.uri + path, 'POST', headers=headers, body=urllib.parse.urlencode(body));
        data = json.loads(content.decode())
        return(data)

    def get_trade_balance(self):
        path = '/0/private/TradeBalance'
        nonce = int(time.time() * 1000)
        body = {
            'nonce': str(nonce)
            }
        self.sign(path, str(nonce), urllib.parse.urlencode(body))
        headers = {
            'API-Key': self.key,
            'API-Sign': self.signature.decode()
            }
        h = httplib2.Http()
        resp, content = h.request(self.uri + path, 'POST', headers=headers, body=urllib.parse.urlencode(body));
        data = json.loads(content.decode())
        print(content)

    def openorders(self):
        path = '/0/private/OpenOrders'
        nonce = int(time.time() * 1000)
        body = {
            'nonce': str(nonce)
            }
        self.sign(path, str(nonce), urllib.parse.urlencode(body))
        headers = {
            'API-Key': self.key,
            'API-Sign': self.signature.decode()
            }
        h = httplib2.Http()
        resp, content = h.request(self.uri + path, 'POST', headers=headers, body=urllib.parse.urlencode(body));
        if resp['status'] == '200':
            data = json.loads(content.decode())
            return(data['result']['open'])
        return(None)

    def get_order_book(self, pair, count=None):
        body = {}
        body['pair'] = pair
        if count:
            body['count'] = count
        data = self.public_request('Depth', body)
        if data:
            return(data[pair])
        return(None)

    def add_standard_order(self, pair, action, order_type, price, volume):
        path = '/0/private/AddOrder'
        nonce = int(time.time() * 1000)
        price = round(price, 8)
        volume = round(volume, 8)
        body = {
            'nonce': str(nonce),
            'pair': pair,
            'type': action,
            'ordertype': order_type,
            'price': str(price),
            'volume': str(volume)
            }
        self.sign(path, str(nonce), urllib.parse.urlencode(body))
        headers = {
            'API-Key': self.key,
            'API-Sign': self.signature.decode()
            }
        h = httplib2.Http()
        resp, content = h.request(self.uri + path, 'POST', headers=headers, body=urllib.parse.urlencode(body));
        if resp['status'] == '200':
            data = json.loads(content.decode())
            return(data)
        return(None)
