import json

from ws4py.client.threadedclient import WebSocketClient
from ws4py.manager import WebSocketManager

from bitcoinaverage.clients.restful_client import RestfulClient
from bitcoinaverage.clients._base_client import _BaseClient

WebsocketManager = WebSocketManager()


class BitcoinAverageWsClient(_BaseClient, WebSocketClient):
    def __init__(self, public_key, secret_key, url=None, subscription=None):
        """
        Base class which establishes connection with the websockets.
        The subclasses should be used to subscribe to the specific websockets.
        """
        super(BitcoinAverageWsClient, self).__init__(secret_key, public_key)
        if url:
            WebSocketClient.__init__(self, url, headers=self.headers)
        self.subscription = subscription

    @property
    def headers(self):
        return [("Authentication", self.signature_header)]

    def handshake_ok(self):
        WebsocketManager.add(self)

    def opened(self):
        print('opened')
        self.send(self.subscribe_message())

    def subscribe_message(self):
        return json.dumps(self.subscription)

    def closed(self, code, reason=None):
        print('Closed', code, reason)

    def received_message(self, message):
        # This method should be overriden
        pass

    def construct_url(self, ticket):
        """
        Appends public key and ticket as parameters to the url.
        """
        return '{}?public_key={}&ticket={}'.format(self.url, self.public_key, ticket)

    def connect_to_websocket(self):
        try:
            self.connect()
        except KeyboardInterrupt:
            WebsocketManager.close_all()
            WebsocketManager.stop()
            WebsocketManager.join()


class TickerWebsocketClient(BitcoinAverageWsClient, WebSocketClient):
    def __init__(self, public_key, secret_key, url='wss://apiv2.bitcoinaverage.com/websocket/ticker',
                 subscription=None):
        super(TickerWebsocketClient, self).__init__(public_key, secret_key, url, subscription)

    def received_message(self, message):
        # override for custom usage
        print(message)

    def ticker_data(self, market, currency):
        '''
        Connects to the websocket which gives ticker data for the given exchange. Override received_message() for custom usage.
        '''
        WebsocketManager.start()

        ticket = RestfulClient(self.secret_key, self.public_key).get_ticket()['ticket']
        self.url = self.construct_url(ticket)

        self.subscription = {"event": "message",
                             "data": {
                                 "operation": "subscribe",
                                 "options": {
                                     "market": market,
                                     "currency": currency
                                 }
                             }
                             }
        self.__init__(self.public_key, self.secret_key, self.url, self.subscription)

        self.connect_to_websocket()


class TickerWebsocketClientV2(BitcoinAverageWsClient, WebSocketClient):
    def __init__(self, public_key, secret_key, url='wss://apiv2.bitcoinaverage.com/websocket/v2/ticker',
                 subscription=None):
        super(TickerWebsocketClientV2, self).__init__(public_key, secret_key, url, subscription)

    def received_message(self, message):
        # override for custom usage
        print(message)

    def ticker_data(self, symbol_set, currency_list):
        '''
        Connects to the websocket which gives ticker data for the given exchange. Override received_message() for custom usage.
        '''
        WebsocketManager.start()

        ticket = RestfulClient(self.secret_key, self.public_key).get_ticket_v2()['ticket']
        self.url = self.construct_url(ticket)

        self.subscription = {"event": "message",
                             "data": {
                                 "operation": "subscribe",
                                 "options": {
                                     "symbol_set": symbol_set,
                                     "currency_list": currency_list
                                 }
                             }
                             }
        self.__init__(self.public_key, self.secret_key, self.url, self.subscription)

        self.connect_to_websocket()


class ExchangeWebsocketClient(BitcoinAverageWsClient, WebSocketClient):
    def __init__(self, public_key, secret_key, url='wss://apiv2.bitcoinaverage.com/websocket/exchanges',
                 subscription=None):
        super(ExchangeWebsocketClient, self).__init__(public_key, secret_key, url, subscription)

    def received_message(self, message):
        # override for custom usage
        print(message)

    def exchange_data(self, exchange_name):
        '''
        Connects to the websocket which gives data for the given exchange. Override received_message() for custom usage.
        '''
        WebsocketManager.start()

        ticket = RestfulClient(self.secret_key, self.public_key).get_ticket()['ticket']
        self.url = self.construct_url(ticket)
        self.subscription = {"event": "message",
                             "data": {
                                 "operation": "subscribe",
                                 "options": {
                                     "exchange": exchange_name
                                 }
                             }
                             }
        self.__init__(self.public_key, self.secret_key, self.url, self.subscription)

        self.connect_to_websocket()


class ExchangeWebsocketClientV2(BitcoinAverageWsClient, WebSocketClient):
    def __init__(self, public_key, secret_key, url='wss://apiv2.bitcoinaverage.com/websocket/v2/exchanges',
                 subscription=None):
        super(ExchangeWebsocketClientV2, self).__init__(public_key, secret_key, url, subscription)

    def received_message(self, message):
        # override for custom usage
        print(message)

    def exchange_data(self, exchange_list):
        '''
        Connects to the websocket which gives data for the given exchange. Override received_message() for custom usage.
        '''
        WebsocketManager.start()

        ticket = RestfulClient(self.secret_key, self.public_key).get_ticket_v2()['ticket']
        self.url = self.construct_url(ticket)
        self.subscription = {"event": "message",
                             "data": {
                                 "operation": "subscribe",
                                 "options": {
                                     "exchange_list": exchange_list
                                 }
                             }
                             }
        self.__init__(self.public_key, self.secret_key, self.url, self.subscription)

        self.connect_to_websocket()

