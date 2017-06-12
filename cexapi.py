# -*- coding: utf-8 -*-
# Author:	t0pep0

import hmac
import hashlib
import time
import json
import requests


class API(object):
    __username = ''
    __api_key = ''
    __api_secret = ''
    __nonce_v = ''

    # Init class
    def __init__(self, username, api_key, api_secret):
        self.__username = username
        self.__api_key = api_key
        self.__api_secret = api_secret

    # get timestamp as nonce
    def __nonce(self):
        self.__nonce_v = '{:.10f}'.format(time.time() * 1000).split('.')[0]

    # generate signature
    def __signature(self):
        string = self.__nonce_v + self.__username + self.__api_key  # create string
        signature = hmac.new(bytes(self.__api_secret, 'latin-1'), bytes(string, 'latin-1'),
                             digestmod=hashlib.sha256).hexdigest().upper()  # create signature
        return signature

    def __post(self, url, param):  # Post Request (Low Level API call)
        page = requests.post(url, param)
        return page.text

    def api_call(self, method, param={}, private=0,
                 couple=''):  # api call (Middle level)
        url = 'https://cex.io/api/' + method + '/'  # generate url
        if couple != '':
            url = url + couple + '/'  # set couple if needed
        if private == 1:  # add auth-data if needed
            self.__nonce()
            param.update({
                'key'      : self.__api_key,
                'signature': self.__signature(),
                'nonce'    : self.__nonce_v})
        answer = self.__post(url, param)  # Post Request
        return json.loads(answer)  # generate dict and return

    def ticker(self, couple='ETH/EUR'):
        return self.api_call('ticker', {}, 0, couple)

    def order_book(self, couple='ETH/EUR'):
        return self.api_call('order_book', {}, 0, couple)

    def trade_history(self, since=1, couple='ETH/EUR'):
        return self.api_call('trade_history', {"since": str(since)}, 0, couple)

    def balance(self):
        return self.api_call('balance', {}, 1)

    def current_orders(self, couple='ETH/EUR'):
        return self.api_call('open_orders', {}, 1, couple)

    def cancel_order(self, order_id):
        return self.api_call('cancel_order', {"id": order_id}, 1)

    def place_order(self, ptype='buy', amount=1, price=1, couple='ETH/EUR'):
        return self.api_call('place_order',
                             {"type" : ptype, "amount": str(amount),
                              "price": str(price)}, 1, couple)

    def price_stats(self, last_hours, max_resp_arr_size, couple='ETH/EUR'):
        return self.api_call(
                'price_stats',
                {"lastHours": last_hours, "maxRespArrSize": max_resp_arr_size},
                0, couple)

    def converter(self, amount, couple='ETH/EUR'):
        return self.api_call('convert', {"amnt": amount}, 0, couple)
