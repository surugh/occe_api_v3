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
    # bid_info = bid_price, bid_amount, bid_total

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


pp(get_order_book_info())
