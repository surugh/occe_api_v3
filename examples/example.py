import os

from dotenv import load_dotenv
from occe_api import api

# from config import TRADE, CASHIER
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    TRADE_ACCESS = os.getenv('TRADE_ACCESS')
    TRADE_SECRET = os.getenv('TRADE_SECRET')
    CASHIER_ACCESS = os.getenv('CASHIER_ACCESS')
    CASHIER_SECRET = os.getenv('CASHIER_SECRET')

    # Примеры использования | Usage examples
    occe = Occe(access_key=TRADE_ACCESS, secret_key=TRADE_SECRET)
    occe_cashier = Occe(access_key=CASHIER_ACCESS, secret_key=CASHIER_SECRET)
    try:
        # print(occe_cashier.get_deposit_address('vqr'))
        # print(occe_cashier.create_withdraw_confirmation(
        # 'TRX', 5, 'TTjmYoZtbCPdjhwJ6tue5PPLpSRTBhK64d'
        # ))
        # print(occe.get_server_time())
        # print(occe.get_trade_history())
        # print(occe.get_trade_history('krb_uah'))
        # print(occe.get_market_orders('idna_usdt'))
        print(occe.get_balances())
        # print(occe.get_balance('UAH'))
        # print(occe.get_open_orders('uni_usdt'))
        # print(occe.get_orders_history('idna_rub'))
        # print(occe.get_orders_status('uni_usdt'))
        # print(occe.get_markets_list(filter_by=True, quoted='btc'))
        """
        {'id': 39555, 'order_id': 40271, 'pair': 'tlr_rub', 'status': 'open',
        'sum_buy': '159.289473680', 'sum_sell': '302.649000000',
        'buy_remainder': '159.289473680', 'sell_remainder': '302.649000000',
        'currency_buy': 'tlr', 'currency_sell': 'rub',
        'created': '2021-05-14T19:24:58.638Z', 
        'user_id': '932c2e12-7b30-4961-a453-1d17aa8ddf5b'}
        """
        # print(occe.cancel_order('trx_uah', 44803))
        # print(occe.create_order('trx_uah', 'sell', 6, 2))

    except OcceException as ex_err:
        print('! [' + type(ex_err).__name__ + ']\n! Ошибочный ответ с биржи\n'
                                              '! Stock API response error\n!',
              ex_err)
