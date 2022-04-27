import hashlib
import json
import logging
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Optional

import requests

import backoff
from logger import log
from settings import (
    ACCESS_ID, SECRET_KEY, API_WAIT_TIME, URL_API, LOGGING,
    TIMEOUT
)

log = log.getChild('client')


class Api:

    @property
    def _headers(self):

        headers = {
            "User-Agent": "Python/CoinEx API client",
            "Content-Type": "application/json",
            "Authorization": ""
        }
        return headers

    @property
    def ts(self):
        now = int(datetime.now().timestamp() * 1000)
        return now + self.ts_shift

    def __init__(self, access_id=ACCESS_ID, secret_key=SECRET_KEY,
                 api_url=URL_API):
        self.access_id = access_id
        self.secret_key = secret_key
        self.api_url = api_url
        self.ts_shift = 0

    def _sign(self, data):
        string_to_sign = ''
        for k, v in sorted(data.items()):
            string_to_sign += f'{k}={v}&'
        string_to_sign += f'secret_key={self.secret_key}'
        sign = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest()
        return sign.upper()

    def _check_results(self, res):
        if res.status_code != 200:
            self.error = True
            if LOGGING:
                log.error(f'Ошибка: {res.status_code}')
            return
        try:
            result = json.loads(res.content)
            self.error = False
            return result
        except JSONDecodeError as e:
            self.error = True
            if LOGGING:
                log.error(f'Ошибка декодирования JSON: {e}')

    @backoff.on_exception(backoff.fibo, Exception, logger=log, max_value=10, backoff_log_level=logging.WARNING)
    def show_pair(self, ticker: str):
        time.sleep(API_WAIT_TIME)
        res = requests.get(
            url=f'{URL_API}market/ticker',
            params={'market': ticker},
            timeout=TIMEOUT,
        )
        results = self._check_results(res)
        if results.get('data').get('date'):
            self.ts_shift = results.get('data').get('date') - self.ts
        return results

    @backoff.on_exception(backoff.fibo, Exception, logger=log, max_value=10, backoff_log_level=logging.WARNING)
    def place_limit_order(self, ticker: str, price: float,
                          amount: Optional[float], side: str
                          ):
        time.sleep(API_WAIT_TIME)
        headers = self._headers
        payload = {
            "access_id": self.access_id,
            "amount": amount,  # order count
            "price": price,  # order price
            "type": side,  # order type
            "market": ticker,  # market type
            "tonce": self.ts,
            "hide": True
        }
        headers['Authorization'] = self._sign(payload)
        res = requests.post(
            url=f'{URL_API}order/limit',
            headers=headers,
            json=payload
        )
        return self._check_results(res)

    @backoff.on_exception(backoff.fibo, Exception, logger=log, max_value=10, backoff_log_level=logging.WARNING)
    def check_order_status(self, order_id: int, ticker: str):
        time.sleep(API_WAIT_TIME)
        headers = self._headers
        payload = {
            "access_id": self.access_id,
            "id": order_id,
            "market": ticker,
            "tonce": self.ts,
        }
        headers['Authorization'] = self._sign(payload)
        res = requests.get(
            url=f'{URL_API}order/status',
            headers=headers,
            params=payload,
            timeout=TIMEOUT,
        )
        return self._check_results(res)

    @backoff.on_exception(backoff.fibo, Exception, logger=log, max_value=10, backoff_log_level=logging.WARNING)
    def balance_info(self):
        time.sleep(API_WAIT_TIME)
        headers = self._headers
        payload = {
            "access_id": self.access_id,
            "tonce": self.ts,
        }
        headers['Authorization'] = self._sign(payload)
        res = requests.get(
            url=f'{URL_API}balance/info',
            headers=headers,
            params=payload,
            timeout=TIMEOUT,
        )
        return self._check_results(res)

    @backoff.on_exception(backoff.fibo, Exception, logger=log, max_value=10, backoff_log_level=logging.WARNING)
    def cancel_all_orders(self, ticker, account_id: int = 0):
        time.sleep(API_WAIT_TIME)
        headers = self._headers
        payload = {
            "access_id": self.access_id,
            "account_id": account_id,
            "market": ticker,
            "tonce": self.ts,
        }
        headers['Authorization'] = self._sign(payload)
        res = requests.delete(
            url=f'{URL_API}order/pending',
            headers=headers,
            params=payload
        )
        return self._check_results(res)
