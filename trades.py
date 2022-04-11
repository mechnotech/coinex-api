import time

from logger import log

from client import Api
from settings import TICKER, MIN_PRICE
import random
from datetime import datetime


def get_middle(ticker_load):
    data = ticker_load['data']['ticker']
    buy = float(data.get('buy'))
    sell = float(data.get('sell'))
    middle = round((buy + sell) / 2, 10)

    log.info(f'покупка: {buy}, продажа:{sell}, середина спрэда: {middle}')

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


def get_order_id(order_resp):
    try:
        return order_resp['data']['id']
    except Exception as e:
        log.exception(f'Не могу получить ID ордера - {order_resp}, ошибка - {e}')
        return None


def check_status(order_resp):
    try:
        return order_resp['data']['status']
    except Exception as e:
        log.exception(f'Не могу получить статус ордера - {order_resp}, ошибка - {e}')
        return None


def spread_percent(ticker_load):
    a = get_best_sell(ticker_load)
    b = get_best_buy(ticker_load)

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        spread = round((a / b - 1) * 100, 4)
        log.debug(f'best_sell - {a}, best_buy - {b}, spread - {spread}')
        return spread


def is_price_above(price):
    return price < MIN_PRICE


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
            log.exception(f'Ошибка соединения: {e}')
            continue
        sell = get_best_sell(pair)
        spread = spread_percent(pair)
        if not spread:
            log.info(f'Не могу получить спред - spread, {cnt}')
            cnt += 1
            continue

        info = f'{cnt} Ожидаю исполнения: моя цена {order_price},' \
               f' лучший sell {sell}, ордер статус {check}, спрэд {spread}%'
        log.info(info)
        if cnt % 60 == 0:
            log.warning(info)
        cnt += 1
        if check == 'done' or check == 'cancel':
            log.warning(f'Ордер #{order_id} исполнен! {datetime.now()}')
            return
        elif sell < order_price:
            log.warning('Цена сдвинулась ниже ордера')
            return


def is_balance_empty():
    while True:
        balance = coinex.balance_info()
        log.warning(f' Баланс: {balance}')
        if balance['code'] == 0:
            amount = float(balance['data']['EMC']['available'])
            if amount < 60:
                return True
            else:
                return False


def main_loop():
    while True:

        while True:
            if is_balance_empty():
                log.error('Баланс исчерпан!')
                time.sleep(60)
            else:
                break

        while True:
            ticker = coinex.show_pair(TICKER)
            mid_price = get_middle(ticker)
            if is_price_above(mid_price):
                log.warning(f'Цена({mid_price}) ниже целевого значения: {MIN_PRICE}')
                time.sleep(60)
            else:
                break

        my_order = coinex.place_limit_order(
            ticker=TICKER,
            price=mid_price,
            amount=get_amount(),
            side='sell'
        )

        wait_order_change(order=my_order, order_price=mid_price)


if __name__ == '__main__':
    coinex = Api()
    log.info(coinex.cancel_all_orders(ticker=TICKER))
    main_loop()
