from client import Api
from settings import TICKER
import random

MIN_PRICE = 0.25


def get_middle(ticker_load):
    data = ticker_load['data']['ticker']
    buy = float(data.get('buy'))
    sell = float(data.get('sell'))
    middle = round((buy + sell) / 2, 6)
    print('покупка:', buy, 'продажа:', sell)
    print('середина спреда:', middle)
    return middle


def get_ammount():
    r = random.randint(5000000, 15000000)
    return r / 1000000


def get_best_sell(ticker_load):
    data = ticker_load['data']['ticker']
    return float(data.get('sell'))

def get_best_buy(ticker_load):
    data = ticker_load['data']['ticker']
    return float(data.get('buy'))

def get_order_id(order_resp):
    return order_resp['data']['id']


def check_status(order_resp):
    return order_resp['data']['status']


def spread_percent(ticker_load):
    a = get_best_sell(ticker_load)
    b = get_best_buy(ticker_load)
    return round((a/b-1)*100, 2)


def is_price_above(price):
    return price < MIN_PRICE


def wait_order_change(order, order_price):
    cnt = 1
    while True:
        order_id = get_order_id(order)
        check = coinex.check_order_status(order_id, TICKER)
        check = check_status(order_resp=check)
        pair = coinex.show_pair(TICKER)
        sell = get_best_sell(pair)
        spread = spread_percent(pair)
        print(f'{cnt} Ожидаю исполнения: моя цена {order_price},'
              f' лучший sell {sell}, ордер статус {check}, спрэд {spread}%')
        cnt += 1
        if check == 'done' or check == 'cancel':
            print(f'Ордер #{order_id} исполнен!')
            return
        elif sell < order_price:
            print('Цена сдвинулась ниже ордера')
            return


def is_balance_empty():
    while True:
        balance = coinex.balance_info()
        print(balance)
        if balance['code'] == 0:
            ammount = float(balance['data']['EMC']['available'])
            if ammount < 50:
                return True
            else:
                return False


def main_loop():
    ticker = coinex.show_pair(TICKER)
    mid_price = get_middle(ticker)
    while not is_price_above(mid_price):
        ticker = coinex.show_pair(TICKER)
        mid_price = get_middle(ticker)
        my_order = coinex.place_limit_order(
            ticker=TICKER,
            price=mid_price,
            amount=get_ammount(),
            side='sell'
        )
        if is_balance_empty():
            print('Баланс исчерпан!')
            exit()
        # Ждем исполнения ордера или смещения спреда ниже ордера
        wait_order_change(order=my_order, order_price=mid_price)
    print(f'Цена({mid_price}) ниже целевого значения: {MIN_PRICE}')


if __name__ == '__main__':
    coinex = Api()
    main_loop()

    print(coinex.cancel_all_orders(ticker=TICKER))
