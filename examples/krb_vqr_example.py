import time
import requests
from config import TRADE
from occe_api_v3 import Occe
from coinpaprika import client
from pprint import pprint as pp

c_paprika = client.Client()
occe = Occe(access_key=TRADE['access'], secret_key=TRADE['secret'])


def get_krb_price():
    """

    :return: Цена карбо в USD округленная до 4х знаков после запятой
    :type: float
    """
    krb = c_paprika.price_converter(base_currency_id='krb-karbo',
                                    quote_currency_id="usd-us-dollars",
                                    amount=1)
    krb_price = krb['price']
    krb_price_format = f'{krb_price:.4f}'
    return float(krb_price_format)


def get_order_book_info():
    """
    ex.
    {'ask_info': {'krb_amount': 11.8,
              'krb_price': 19.99,
              'usd_price': 0.0043,
              'vqr_amount': 235.882},
    'bid_info': {'krb_amount': 10,
              'krb_price': 10,
              'usd_price': 0.0086,
              'vqr_amount': 100}}
    :return: ex.
    :type: dict
    """
    krb_median_price = get_krb_price()

    # Получаем стаканы по паре
    order_book = occe.get_market_orders('krb_vqr')

    # Выделяем значения крайнего ордера на продажу
    ask_price = order_book['data']['sellOrders'][0]['price']    # float
    ask_amount = order_book['data']['sellOrders'][0]['amount']  # krb
    ask_total = order_book['data']['sellOrders'][0]['total']    # vqr

    # Выделяем значения крайнего ордера на продажу
    bid_price = order_book['data']['buyOrders'][0]['price']    # float
    bid_amount = order_book['data']['buyOrders'][0]['amount']  # krb
    bid_total = order_book['data']['buyOrders'][0]['total']    # vqr

    vqr_ask_price = krb_median_price / ask_price
    vqr_ask_price_format = float(f'{vqr_ask_price:.4f}')

    vqr_bid_price = krb_median_price / bid_price
    vqr_bid_price_format = float(f'{vqr_bid_price:.4f}')

    # Создаем словари
    ask_info = dict(usd_price=vqr_ask_price_format, krb_price=ask_price,
                    krb_amount=ask_amount, vqr_amount=ask_total)
    bid_info = dict(usd_price=vqr_bid_price_format, krb_price=bid_price,
                    krb_amount=bid_amount, vqr_amount=bid_total)
    order_book_info = dict(ask_info=ask_info, bid_info=bid_info)
    return order_book_info


while True:
    try:
        extreme_orders = get_order_book_info()
        pp(extreme_orders)
        ask_amount = float(extreme_orders['ask_info']['krb_amount'])
        krb_ask_price = float(extreme_orders['ask_info']['krb_price'])
        bid_amount = float(extreme_orders['bid_info']['krb_amount'])
        bid_price = float(extreme_orders['bid_info']['krb_price'])

        ask_price_round = float(f'{krb_ask_price:.2}')
        sell_price = ask_price_round - 1

        bid_price_round = float(f'{bid_price:.2}')
        buy_price = bid_price_round + 1

        if ask_amount > 2:
            if sell_price > bid_price_round + 1:
                ask_amount_round = float(f'{ask_amount:.0}')
                sell_amount = ask_amount_round / 2
                krb_balance = occe.get_balance('krb')
                if krb_balance > sell_amount:
                    print(occe.create_order('krb_vqr', 'sell', sell_amount, sell_price))

                else:
                    if bid_amount > 2:
                        if buy_price < ask_price_round - 1:
                            bid_amount_round = float(f'{bid_amount:.0}')
                            buy_amount = bid_amount_round / 2
                            vqr_balance = occe.get_balance('vqr')
                            if vqr_balance > buy_amount:
                                print(occe.create_order('krb_vqr', 'buy', buy_amount, buy_price))
        print('-'*15)
        time.sleep(60)

    except requests.ConnectionError as connerr:
        print('Разрыв связи: [' + type(connerr).__name__ + ']', connerr)
        time.sleep(20)
