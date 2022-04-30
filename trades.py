import time

from logger import log

from client import Api
from settings import TICKER, BORDER_PRICE, DIRECTION, DROP_ORDERS
import random
from datetime import datetime


def get_middle(ticker_load):
    data = ticker_load['data']['ticker']
    buy = float(data.get('buy'))
    sell = float(data.get('sell'))
    middle = round((buy + sell) / 2, 10)

    log.info(f'buy: {buy}, sell:{sell}, mid-spread: {middle}')

    return middle


def get_amount():
    r = random.randint(10000000, 15000000)
    return r / 200000


def get_best_sell(ticker_load):
    if ticker_load:
        data = ticker_load['data']['ticker']
        return float(data.get('sell'))


def get_best_buy(ticker_load):
    if ticker_load:
        data = ticker_load['data']['ticker']
        return float(data.get('buy'))


def check_error(response):
    if response['code'] == 227:
        log.exception(response['message'])
        exit()
    if not response['data']:
        log.exception(f'Error code {response["code"]}, {response["message"]}')
    return None


def get_order_id(order_resp):
    check_error(order_resp)
    return order_resp['data']['id']


def check_status(order_resp):
    check_error(order_resp)
    return order_resp['data']['status']


def spread_percent(ticker_load):
    a = get_best_sell(ticker_load)
    b = get_best_buy(ticker_load)

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        spread = round((a / b - 1) * 100, 4)
        log.debug(f'best_sell - {a}, best_buy - {b}, spread - {spread}')
        return spread


def is_price_above(price):
    return price < BORDER_PRICE


def wait_order_change(order, order_price):
    cnt = 1
    while True:
        order_id = get_order_id(order)
        try:
            check = coinex.check_order_status(order_id, TICKER)
            log.debug(check)
            check = check_status(order_resp=check)
            log.debug(check)
            pair = coinex.show_pair(TICKER)
        except ConnectionError as e:
            log.exception(f'Connection error: {e}')
            continue
        sell = get_best_sell(pair)
        buy = get_best_buy(pair)
        spread = spread_percent(pair)
        if not spread:
            log.info(f"Can't get spread - {cnt}")
            cnt += 1
            continue

        info = f'{cnt} Waiting for execution: my price is {order_price},' \
               f' best sell {sell}, order status {check}, spread {spread}%'
        log.info(info)
        if cnt % 60 == 0:
            log.warning(info)
        cnt += 1
        if check == 'done' or check == 'cancel':
            log.warning(f'Order #{order_id} filled! {datetime.now()}')
            return
        elif DIRECTION == 'sell' and sell < order_price:
            log.warning('The price moved below the order')
            return
        elif DIRECTION == 'buy' and buy > order_price:
            log.warning('The price moved above the order')
            return


def is_balance_empty():

    while True:
        balance = coinex.balance_info()
        if balance['code'] == 227:
            exit()
        if balance['code'] == 0:
            log.warning(f'  Balance: {balance["data"]}')
            if DIRECTION == 'sell':
                amount = float(balance['data']['EMC']['available'])
            else:
                amount = float(balance['data']['USDT']['available'])
            if amount < 60:
                return True
            else:
                return False


def main_loop():
    while True:

        while True:
            if is_balance_empty():
                log.error('The funds have been exhausted. Top up your balance!')
                time.sleep(60)
            else:
                break

        cnt_s = 0
        cnt_b = 0
        while True:
            ticker = coinex.show_pair(TICKER)
            mid_price = get_middle(ticker)
            if DIRECTION == 'sell' and is_price_above(mid_price):
                cnt_s += 1
                if cnt_s > 60:
                    log.warning(f'Sell price({mid_price}) below threshold: {BORDER_PRICE}')
                    cnt_s = 0

            elif DIRECTION == 'buy' and not is_price_above(mid_price):
                cnt_b += 1
                if cnt_b > 60:
                    log.warning(f'Buy price({mid_price}) above threshold: {BORDER_PRICE}')
                    cnt_b = 0
            else:
                break

        order = {'ticker': TICKER,
                 'price': mid_price,
                 'amount': get_amount(),
                 'side': DIRECTION
                 }
        my_order = coinex.place_limit_order(**order)
        log.warning(f'Order placed - {order}')

        wait_order_change(order=my_order, order_price=mid_price)


if __name__ == '__main__':
    coinex = Api()
    if DROP_ORDERS:
        log.info(coinex.cancel_all_orders(ticker=TICKER))
    main_loop()
