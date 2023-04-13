"""
Примеры использования находятся в example.py,
не забудьте указать свои API ключи в файле .env
The usage examples are at example.py file,
don't forget to specify your API keys in the file .env

Если это полезно, вы можете сделать пожертвование
If it useful you can make a donation

USDT:
TRX-20: TJnXcu7XS5LCDMVG4XKYnVFgchUmmz24SS
BEP-20: 0x855e3d62917e755464a1ae54f9d89831542fea9b
ALTS:
TRX: TJnXcu7XS5LCDMVG4XKYnVFgchUmmz24SS
VQR: VQRgRevcdPYbtxQE3Lhsm6rYnnnRk1tgr9x9
UFO: Uf9cegWUWTYAx3Y9M6fbCF7JfWmA4ZHVPR
KRB: KhZnQRWPaVLiMqJPoULSDzPGMeqp5invzi4iVYmArnCTd1UiQU6CjgZVm5Xu2uFBTqTgqxjzTMJpGci7sR1fznpfT4kGPWm
"""

import json
import requests


class OcceException(Exception):
    def __init__(self, err_text=''):
        self.__err_text = err_text

    def __str__(self, *args, **kwargs):
        return self.__err_text


class Occe:

    def __init__(self, access_key: str = None,
                 secret_key: str = None) -> None:
        self.api_url_public: str = 'https://api.occe.io/public/'
        self.api_url: str = 'https://api.occe.io'
        self.access: str = access_key
        self.secret: str = secret_key
        self.version: str = '/v3/'
        self.headers: dict = {"x-api-key": secret_key}

    @staticmethod
    def __check_trade_api_response(resp_json: dict) -> bool:
        """
        Поднимает исключение, если данные с биржи содержат ошибку
        Raise exception, if data from exchange contain error

        :param resp_json: Данные с биржи в формате
            JSONData from stock exchange in JSON format
        :type resp_json: dict

        :return: Истина, если данные со склада успешны
            True, if data from stock is success
        :rtype : bool

        """
        try:
            retval = True if resp_json['result'] == 'success' else False
        except KeyError:
            retval = False
        try:
            estr = resp_json['message'] if not retval else ''
        except KeyError:
            estr = 'Unknown error.'

        if not retval:
            raise OcceException(estr)

        return retval

    def call_api(self, method: str, params: dict = None,
                 get: bool = True, delete: bool = False,
                 withdraw: dict = None,
                 withdraw_confirm: dict = None) -> dict:
        """
        Через эту функцию проходят все запросы на приватный API

        All requests to the private API pass through this function

        :param params: Различные параметры POST | Various POST parameters
        :type: dict

        :param method: Методы пользовательского API | User API methods ex. account/balance
        :type method: str

        :param get: HTTP-verb — GET or POST
        :type get: bool

        :param delete: HTTP-verb — DELETE
        :type delete: bool

        :param withdraw: Различные параметры POST | Various POST cashier parameters
        :type: dict

        :param withdraw_confirm: Различные параметры POST | Various POST cashier parameters
        :type: dict

        :return: Response API
        :type: dict
        """
        if params:
            query_url = \
                f"{self.api_url}{self.version}{method}?type{params['type']}" \
                f"&amount={params['amount']}&price={params['price']}" \
                f"&balanceVersion={params['balanceVersion']}"
        else:
            query_url = self.api_url + self.version + method

        if get:
            response = requests.get(query_url, headers=self.headers)
        else:
            if delete:
                response = requests.delete(query_url, headers=self.headers)
            else:
                response = requests.post(
                    query_url, headers=self.headers, data=json.dumps(params)
                )

        if withdraw:
            cashier_url = \
                f"{self.api_url}{self.version}{method}" \
                f"?currency={withdraw['currency']}" \
                f"&amount={withdraw['amount']}" \
                f"&receiverAddress={withdraw['receiverAddress']}" \
                f"&network={withdraw['network']}" \
                f"&saveAddress={withdraw['saveAddress']}" \
                f"&name={withdraw['name']}" \
                f"&paymentId={withdraw['paymentId']}" \
                f"&internal={withdraw['internal']}"
            response = requests.post(
                cashier_url, headers=self.headers, data=json.dumps(withdraw)
            )

        if withdraw_confirm:
            withdraw_url = \
                f"{self.api_url}{self.version}{method}" \
                f"?confirmationId={withdraw_confirm['confirmationId']}" \
                f"&code={withdraw_confirm['code']}" \
                f"&balanceVersion={withdraw_confirm['balanceVersion']}"
            response = requests.post(
                withdraw_url, headers=self.headers, data=json.dumps(withdraw)
            )

        # response.raise_for_status()
        obj = response.json()
        self.__check_trade_api_response(obj)
        return obj

    ''' Trade User Methods '''

    def get_balances(self) -> dict:
        """
        ex.

        {
            'result': 'success',
            'data': {
            'currencies': [
                {'name': 'KRB'              # currency
                'depositBlocked': False,
                'withdrawBlocked': False,
                'onOrder': 0,               # the locked amount
                'value': 0},                # the available amount
                ],
            'balanceVersion': 300           # the version of balance
            }
        }

        :return: Информация о Балансе Пользователя
            Information About Balance of User
        :type: dict
        """
        req = self.call_api('account/balance')
        return req

    def get_balance(self, coin: str) -> float:
        """

        :param coin: Сокращенное название монеты в любом регистре
            Abbreviated name of the coin in any case
        :type: str

        :return: Информация о доступном Балансе по выбранной монете
            Information about the available Balance of the selected coin
        :type: float
        """
        balances = self.get_balances()['data']['currencies']
        balance = []
        for info in balances:
            if info['name'] == coin.upper():
                balance.append(info['value'])
        return balance[0]

    def get_open_orders(self, pair: str) -> dict:
        """
        ex.

        {
          "result": "success",
          "buyOrders": [
            {
              "orderId": order ID,
              "userId": user ID,
              "type": "buy",
              "amount": volume of trading in BTC,
              "price": price for 1 BTC,
              "date": the time of placing the order,
              "pair": "krb_btc",
              "total": total
            }
          ],
          "sellOrders": [
            {
              "orderId": order ID,
              "userId": user ID,
              "type": "sell",
              "amount": volume of trading in BTC,
              "price": price for 1 BTC,
              "date": the time of placing the order,
              "pair": "krb_btc",
              "total": total
            }
          ]
        }


        :param pair: Pair in any case ex. krb_uah
        :type: str

        :return: Активные заказы пользователя | Active user orders
        :type: dict
        """
        req = self.call_api('account/orders/open/' + pair.lower())
        return req

    def get_orders_history(self, pair: str) -> dict:
        """
        ex.

        {
          "result": "success",
          "orders": [
            {
              "orderId": order ID,
              "orderType": buy or sell,
              "amount": amount,
              "price": price,
              "date": date,
              "total": total
            }
          ]
        }


        :param pair: Pair in any case ex. krb_uah
        :type: str

        :return: Историю заказов пользователя | User's order history
        :type: dict
        """
        req = self.call_api('account/orders_history/' + pair.lower())
        return req

    def get_orders_status(self, pair: str, order_id: int = 0) -> dict:
        """
        ex.

        {
          "result": "success",
          "orders": [
            {
              "id": ID,
              "order_id": order ID,
              "user_id": user ID,
              "status": status of order (open, filled, cancelled),
              "sum_buy": sum of buy,
              "sum_sell": sum of sell,
              "pair": current pair,
              "currency_buy": currency buy,
              "currency_sell": currency sell,
              "buy_remainder": buy remainder,
              "sell_remainder": sell remainder,
              "created": date,
            }
          ]
        }


        :param pair: Pair in any case ex. krb_uah
        :type: str
        
        :param order_id: Order ID
        :type: int or str
        
        :return: Статус заказов пользователя на выбранной паре
            The status of the user's orders on the selected pair
        :type: dict
        """
        req = self.call_api(pair + '/orders/status')
        if order_id:
            for order_info in req['data']['orders']:
                if int(order_id) == order_info['order_id']:
                    return order_info
        else:
            return req

    def cancel_order(self, pair: str, order_id: int) -> dict:
        """
            Отменяет ордер по ID на выбранной паре | Cancels an order by ID on the selected pair

        :param pair: Pair in any case ex. krb_uah
        :type: str

        :param order_id:
        :type: int or str

        :return:  {"result": "success", "info": "Order was deleted"}
        :type: dict
        """
        req = self.call_api(
            f"{pair.lower()}/orders/{order_id}", get=False, delete=True
        )
        return req

    def create_order(self, market: str, order_type: str, amount: int | float,
                     price: int | float) -> dict:
        """
            Создает ордер на выбранной паре | Creates an order on the selected pair

            Строковые параметры этой функции могут быть в любом регистре.
            The string parameters of this function can be in any case.

        :param market: Торговая пара | Trading pair ex. uah_rub
        :type: str

        :param order_type: Направление ордера | Order direction ex. buy or sell
        :type: str

        :param amount: Сумма заказа в базовой валюте | Order amount in base currency
        :type: int or float

        :param price: Цена заказа | Order price
        :type: int or float

        :return: {'result': 'success', 'data': {'info': 'Order was added'}}
        :type: dict
        """
        balance_version = str(self.get_balances()['data']['balanceVersion'])
        data = dict(type=order_type.lower(),
                    amount=amount,
                    price=price,
                    balanceVersion=balance_version)

        req = self.call_api(
            f"{market.lower()}/orders", params=data, get=False
        )
        return req

    ''' Public Methods '''

    def get_server_time(self) -> int:
        """

        :return: Server Time - unix timestamp
        :type: int
        """
        req = requests.get(f"{self.api_url_public}tradeview/time")
        return req.json()

    def get_trade_history(self, pair: str = None) -> dict:
        """
        ex.

        {
          "result": "success",
          "data": {
            "pair": "krb_btc",
            "coinInfo": {
              "lastPrice": last price,
              "volume24h": volume for last 24h,
              "highest24h": highest price for last 24h,
              "lowest24h": lowest price for last 24h,
              "change24h": change for last 24h
            },
            "pair": "krb_uah",
            "coinInfo": {
              ...
            },
            ...
          }
        }

        or

        {
          "result": "success",
          "coinInfo": {
            "lastPrice": last price,
            "volume24h": volume for last 24h,
            "highest24h": highest price for last 24h,
            "lowest24h": lowest price for last 24h,
            "change24h": change for last 24h
          }
        }


        :param pair: None or pair in any case ex. krb_uah
        :type: None or str

        :return: Публичная история торговли | Public trading history
        :type: dict
        """
        if pair:
            req = requests.get(self.api_url_public + 'info/' + pair.lower())
        else:
            req = requests.get(self.api_url_public + 'info/')
        return req.json()

    def get_markets_list(self, filter_by: bool = False,
                         quoted: str = None, base: str = None) -> list:
        """
            Получает список пар имеющихся на бирже | Gets a list of pairs available on the exchange

            Установка параметра filter_by в значение истина,
            позволяет фильтровать список по базовой и|или котируемой валюте(ам)

            Setting the filter_by parameter to true
            allows you to filter the list by the base and / or quoted currency (s)

        :param filter_by: Предоставляет доступ к фильтрам | Provides access to filters
        :type: bool

        :param quoted: Котируемая валюта | Quoted currency
        :type: str

        :param base: Базовая валюта | Base currency
        :type: str

        :return:
        :type: list
        """
        r = requests.get(self.api_url_public + 'info/').json()
        markets_data = r['data']['coinInfo']
        markets_list = []
        for market_info in markets_data:
            pair = market_info['pair']
            if filter_by:
                if base:
                    if pair.startswith(base.lower()):
                        markets_list.append(pair)
                if quoted:
                    if pair.endswith(quoted.lower()):
                        markets_list.append(pair)
            else:
                markets_list.append(pair)
        return markets_list

    def get_market_orders(self, pair: str) -> dict:
        """
        ex.

        {
          "result": "success",
          "buyOrders": [
            {
              "type": "buy",
              "amount": volume of trading in BTC,
              "price": price for 1 BTC,
              "date": the time of placing the order,
              "pair": "krb_btc"
            }
          ],
          "sellOrders": [
            {
              "type": "sell",
              "amount": volume of trading in BTC,
              "price": price for 1 BTC,
              "date": the time of placing the order,
              "pair": "krb_btc"
            }
          ]
        }


        :param pair: Pair in any case ex. krb_uah
        :type: str

        :return: Все активные ордера по выбранной паре | All active orders for the selected pair
        :type: dict
        """
        req = requests.get(
            f"{self.api_url_public}orders/{pair.lower()}"
        ).json()
        sell = sorted(
            req['data']['sellOrders'], key=lambda order: order['price']
        )
        buy = sorted(
            req['data']['buyOrders'], key=lambda order: order['price'],
            reverse=True
        )
        orders = dict(
            result='success', data=dict(buyOrders=buy, sellOrders=sell)
        )
        return orders

    '''Cashier User Methods'''

    def get_deposit_address(self, coin: str) -> dict:
        """
        ex.
        {'result': 'success', 'data': {'address': 'address'}}

        :param coin: Сокращенное название монеты в любом регистре
            Abbreviated name of the coin in any case
        :type: str

        :return: Создает адрес для выбранной монеты
            Creates an address for the selected coin
        :type: dict
        """
        req = self.call_api(f"currency/deposit_address/{coin.lower()}")
        return req

    def create_withdraw_confirmation(self, coin: str,
                                     amount: int | float | str,
                                     receiver_addr: str,
                                     usdt_network: str = None,
                                     save_addr: bool = False,
                                     name_addr: str = None,
                                     krb_paymentid: str = None,
                                     internal: bool = False) -> dict:
        """
        ex.
            {'result': 'success',
               'data': {
                'info': 'Email confirmation sent successfully.',
                'confirmationId': 3423, 'internal': False}
                }`

        :param coin: currency (required)
        :type: str
        :param amount: amount (required)
        :type: int, float or str
        :param receiver_addr: address of receiver (required)
        :type: str
        :param usdt_network: network for usdt currency (required)
        :type: str
        :param save_addr: save address (not required)
        :type: bool
        :param name_addr: name of adress for saving (not required)
        :type: str
        :param krb_paymentid: only for krb (not required)
        :type: str
        :param internal: internal or external TX (required)
        :type: bool
        :return: ex.
        :type:dict
        """

        data = dict(currency=coin.lower(),
                    amount=amount,
                    receiverAddress=receiver_addr,
                    network=usdt_network,
                    saveAddress=save_addr, name=name_addr,
                    paymentId=krb_paymentid,
                    internal=internal)

        req = self.call_api('currency/withdraw_confirmation', withdraw=data)
        return req

    def confirm_withdraw(self, confirmation_id: int | str,
                         code: str) -> dict:
        """
        :param confirmation_id: from create_withdraw_confirmation
        :type: int or str
        :param code: code from email or google authenticator
        :type: str
        :return: Withdraw completed successfully
        :type: dict
        """
        balance_version = str(self.get_balances()['data']['balanceVersion'])
        data = dict(confirmationId=confirmation_id, code=code,
                    balanceVersion=balance_version)
        req = self.call_api('currency/withdraw', withdraw_confirm=data)
        return req

    def confirm_internal_withdraw(self, confirmation_id: int | str,
                                  code: str) -> dict:
        """
        :param confirmation_id: from create_withdraw_confirmation
        :type: int or str
        :param code: code from email or google authenticator
        :type: str
        :return: Withdraw completed successfully
        :type: dict
        """
        balance_version = str(self.get_balances()['data']['balanceVersion'])
        data = dict(confirmationId=confirmation_id, code=code,
                    balanceVersion=balance_version)
        req = self.call_api('currency/internal_withdraw', withdraw_confirm=data)
        return req
