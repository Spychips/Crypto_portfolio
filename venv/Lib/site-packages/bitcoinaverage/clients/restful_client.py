import requests

from bitcoinaverage.clients._base_client import _BaseClient
from bitcoinaverage._config import construct_url, SIGNATURE_HEADER
from bitcoinaverage.exceptions import BitcoinaverageResponseException


class RestfulClient(_BaseClient):
    def __init__(self, secret_key, public_key):
        super(RestfulClient, self).__init__(secret_key, public_key)

    @property
    def headers(self):
        return {SIGNATURE_HEADER: self.signature_header, "Authentication": self.signature_header}

    @classmethod
    def checked_result(cls, result, format='json', exception=BitcoinaverageResponseException):
        if result.status_code != 200:
            raise exception(result.status_code, result.reason)
        if format == 'json':
            return result.json()
        return 'csv'

    def write_csv(self, url, dest_file):
        result = requests.get(url=url, headers=self.headers)
        with open(dest_file, 'wb') as f:
            f.write(result.content)

    def get_result_from_url(self, url, format='json'):
        result = requests.get(url=url, headers=self.headers)
        # if format == 'json':
        return self.checked_result(result, format=format)
        # raise BitcoinaverageResponseException('Response is not valid json format')

    # region Constants

    # region Supported Symbols
    def all_symbols(self):
        '''
        Returns all symbols - local and global.
        '''
        url = construct_url('constants/symbols')
        return self.get_result_from_url(url)

    def symbols_per_market(self, market=None):
        '''
        Returns a list of symbols for a specific market
        '''
        url = construct_url('constants/symbols{}'.format('/{}'.format(market) if market else ''))
        return self.get_result_from_url(url=url)

    def symbols_local(self):
        '''
        Returns symbols for local market.
        '''
        return self.symbols_per_market('local')

    def symbols_global(self):
        '''
        Returns symbols for global market.
        '''
        return self.symbols_per_market('global')

    # endregion

    # region Rates
    def exchange_rates(self, market):
        '''
        Returns fiat exchange rates used in the current indices calculations
        '''
        url = construct_url('constants/exchangerates/{}'.format(market))
        return self.get_result_from_url(url)

    def exchange_rates_local(self):
        '''
        Returns local fiat exchange rates used in the current indices calculations
        '''
        return self.exchange_rates('local')

    def exchange_rates_global(self):
        '''
        Returns global fiat exchange rates used in the current indices calculations
        '''
        return self.exchange_rates('global')

    # endregion

    # region Time
    def server_time(self):
        '''
        Returns our server time that can be used as a check when using API Key authentication
        '''
        url = construct_url('constants/time')
        return self.get_result_from_url(url)

    # endregion

    # endregion

    # region Indices

    # region Ticker Data
    def ticker_all(self, market, crypto='', fiat=''):
        '''
        Returns ticker data for the given market and supported symbols (combinations of crypto+fiat)
        '''
        url = construct_url('indices/{}/ticker/all?crypto={}&fiat={}'.format(market, crypto, fiat))
        return self.get_result_from_url(url)

    def ticker_all_local(self, crypto='', fiat=''):
        '''
        Returns local ticker data for every all the given combinations of crypto+fiat.
        If crypto is omitted all cryptos are used. If fiat is omitted all fiats are used.
        '''
        return self.ticker_all('local', crypto, fiat)

    def ticker_all_global(self, crypto='', fiat=''):
        '''
        Returns global ticker data for every all the given combinations of crypto+fiat.
        If crypto is omitted all cryptos are used. If fiat is omitted all fiats are used.
        '''
        return self.ticker_all('global', crypto, fiat)

    def get_ticker_data_per_symbol(self, market, symbol):
        '''
        Returns ticker data for specified market and symbol
        :param market: global or local
        :param symbol: valid crypto-fiat pair
        :return:
        '''
        url = construct_url('indices/{}/ticker/{}'.format(market, symbol))
        return self.get_result_from_url(url=url)

    def ticker_local_per_symbol(self, symbol):
        '''
        Returns ticker local data for specified symbol
        '''
        return self.get_ticker_data_per_symbol('local', symbol)

    def ticker_global_per_symbol(self, symbol):
        '''
        Returns ticker global data for specified symbol
        '''
        return self.get_ticker_data_per_symbol('global', symbol)

    def ticker_short(self, market, crypto, fiat):
        '''
        Returns basic ticker denoting last and daily average price for all symbols
        '''
        url = construct_url('indices/{}/ticker/short?crypto={}&fiat={}'.format(market, crypto, fiat))
        return self.get_result_from_url(url)

    def ticker_short_local(self, crypto='', fiat=''):
        '''
        Returns basic local ticker denoting last and daily average price for all symbols
        '''
        return self.ticker_short('local', crypto, fiat)

    def ticker_short_global(self, crypto='', fiat=''):
        '''
        Returns basic global ticker denoting last and daily average price for all symbols
        '''
        return self.ticker_short('global', crypto, fiat)

    def _ticker_custom_generic_handler(self, symbol, exchanges, include_or_exclude):
        '''
        This endpoint can be used to generate a custom index in a certain currency. The "inex" path parameter represents
        "include" or "exclude", you can choose to generate an index removing a specified exchanges, or only including
        the few that you require.
        :return:
        '''
        url = construct_url('indices/ticker/custom/{}/{}?exchanges={}'.format(include_or_exclude, symbol, exchanges))
        return self.get_result_from_url(url=url)

    def ticker_custom_include(self, symbol, exchanges):
        '''
        Returns ticker values using only the exchanges added as argument in a comma separated format.
        '''
        return self._ticker_custom_generic_handler(symbol, exchanges, 'include')

    def ticker_custom_exclude(self, symbol, exchanges):
        '''
        Returns ticker values using all exchanges except the ones added as argument in a comma separated format.
        '''
        return self._ticker_custom_generic_handler(symbol, exchanges, 'exclude')

    # region Ticker Changes
    def ticker_changes_all_local(self):
        '''
        Returns ticker values and price changes.
        '''
        url = construct_url('indices/local/ticker/changes/all')
        return self.get_result_from_url(url)

    def ticker_changes_generic(self, market, symbol):
        '''
        Returns ticker values and price changes for given market and symbol.
        '''
        url = construct_url('indices/{}/ticker/{}/changes'.format(market, symbol))
        return self.get_result_from_url(url)

    def ticker_changes_local(self, symbol):
        '''
        Returns local ticker values and price changes for given symbol.
        '''
        return self.ticker_changes_generic('local', symbol)

    def ticker_changes_global(self, symbol):
        '''
        Returns global ticker values and price changes for given symbol.
        '''
        return self.ticker_changes_generic('global', symbol)

    # endregion

    # endregion

    # region Historical Data
    def get_history(self, market, symbol, period='', format='json', csv_path=None):
        '''
        :param market: local or global
        :param symbol: valid symbol - example BTCUSD
        :param period: daily, monthly, alltime
        :param format: json, csv
        '''
        url = construct_url('indices/{}/history/{}?period={}&format={}'.format(market, symbol, period, format))
        if format == 'json':
            return self.get_result_from_url(url, format)
        self.write_csv(url, csv_path)

    def save_history_local(self, symbol, period, csv_path):
        '''
        Save local history in the specified file.
        :param symbol: crytpo-fiat pair (ex. BTCUSD)
        :param period: daily, monthly, alltime - default=alltime
        :param csv_path: where do you want to store the file (need to be .csv file)
        :return:
        '''
        if not csv_path.endswith('.csv'):
            raise BitcoinaverageResponseException('You can only save history as .csv file')
        self.get_history('local', symbol, period, 'csv', csv_path=csv_path)

    def save_history_global(self, symbol, period, csv_path):
        '''
        Save local history in the specified file.
        :param symbol: crytpo-fiat pair (ex. BTCUSD)
        :param period: daily, monthly, alltime - default=alltime
        :param csv_path: where do you want to store the file (need to be .csv file)
        :return:
        '''
        if not csv_path.endswith('.csv'):
            raise BitcoinaverageResponseException('You can only save history as .csv file')
        self.get_history('global', symbol, period, 'csv', csv_path=csv_path)

    def history_local(self, symbol, period='', format='json', csv_path=None):
        '''
        Returns list containing historical data for the given symbol (volume traded and average price for every day).
        :param symbol (required): valid symbol - example BTCUSD
        :param period: daily, monthly, alltime - default=alltime
        :param format: json, csv - default=json
        '''
        return self.get_history('local', symbol, period, format)

    def history_global(self, symbol, period='', format='json'):
        '''
        Returns list containing historical data for the given symbol (volume traded and average price for every day).
        :param symbol (required): valid symbol - example BTCUSD
        :param period: daily, monthly, alltime - default=alltime
        :param format: json, csv - defalt=json
        '''
        return self.get_history('global', symbol, period, format=format)

    def data_since_timestamp(self, market, symbol, since=''):
        '''
        Return historical ticker data since 'timestamp' only
        :param market: local or global
        :param symbol: crypto-fiat pair
        :param since: integer timestamp
        '''
        url = construct_url('indices/{}/history/{}?since={}'.format(market, symbol, since))
        return self.get_result_from_url(url)

    def data_since_timestamp_local(self, symbol, since=''):
        '''
        Return local historical ticker data since 'timestamp' only
        :param symbol: crypto-fiat pair
        :param since: integer timestamp
        '''
        return self.data_since_timestamp('local', symbol, since)

    def data_since_timestamp_global(self, symbol, since=''):
        '''
        Return global historical ticker data since 'timestamp' only
        :param symbol: crypto-fiat pair
        :param since: integer timestamp
        '''
        return self.data_since_timestamp('global', symbol, since)

    def price_at_timestamp(self, market, symbol, timestamp):
        '''
        Return price at specified timestamp (unix format).
        If timestamp is in per_minute data range, returns price closest to minute.
        If timestamp is in per_hour data range, returns price closest to hour.
        If timestamp is in per_day data range, returns price closest to timestamp at 00:00 that day
        :param market: local or global
        :param symbol: crypto-fiat pair
        :param timestamp: valid unix timestamp
        '''
        url = construct_url('indices/{}/history/{}?at={}'.format(market, symbol, timestamp))
        return self.get_result_from_url(url)

    def price_at_timestamp_local(self, symbol, timestamp):
        '''
        Return price at specified timestamp (unix format).
        If timestamp is in per_minute data range, returns price closest to minute.
        If timestamp is in per_hour data range, returns price closest to hour.
        If timestamp is in per_day data range, returns price closest to timestamp at 00:00 that day
        :param market: local or global
        :param symbol: crypto-fiat pair
        :param timestamp: valid unix timestamp
        '''
        return self.price_at_timestamp('local', symbol, timestamp)

    def price_at_timestamp_global(self, symbol, timestamp):
        '''
        Return price at specified timestamp (unix format).
        If timestamp is in per_minute data range, returns price closest to minute.
        If timestamp is in per_hour data range, returns price closest to hour.
        If timestamp is in per_day data range, returns price closest to timestamp at 00:00 that day
        :param market: local or global
        :param symbol: crypto-fiat pair
        :param timestamp: valid unix timestamp
        '''
        return self.price_at_timestamp('global', symbol, timestamp)

    # endregion


    # endregion

    # region Exchanges
    def all_exchange_data(self, crypto='', fiat=''):
        '''
        Returns a list of all exchanges with their integrated symbols and data. Data can be filtered by crypto or fiat currency
        '''
        suffix = 'exchanges/all?crypto={}&fiat={}'.format(crypto, fiat)
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    def all_exchange_data_for_symbol(self, symbol=''):
        '''
        Returns a list of all exchanges with their integrated symbols and data.
        By specifying symbol, data will be filtered and only shown for that symbol.
        '''
        suffix = 'exchanges/all?symbol={}'.format(symbol)
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    def per_exchange_data(self, exchange_name):
        '''
        Returns specified exchange's symbols and data
        '''
        suffix = 'exchanges/{}'.format(exchange_name)
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    def exchange_count(self):
        '''
        Return a total of integrated exchanges along with ignored, included and inactive status counts
        '''
        return self.per_exchange_data('count')

    def outlier_exchanges(self):
        '''
        Returns a list of exchanges that failed our sanity checks. Provides what value failed and on what orderbook
        '''
        suffix = 'exchanges/outliers'
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    def ignored_exchanges(self):
        '''
        Returns exchanges that are either ignored or inactive according to specified state parameter.
        With ignored exchanges a "ignore_reason" is provided
        '''
        suffix = 'exchanges/ignored'
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    def inactive_exchanges(self):
        '''
        Returns list of inactive exchanges.
        '''
        suffix = 'exchanges/inactive'
        url = construct_url(suffix)
        return self.get_result_from_url(url)

    # endregion

    # region Weighting
    def currency_weights(self):
        '''
        Returns a list of currencies and their weights that are used to produce our Global Bitcoin Price Index
        '''
        url = construct_url('weighting/currencies')
        return self.get_result_from_url(url)

    def exchange_weights(self):
        '''
        Returns a list of exchanges, their symbols, and their associated weights
        '''
        url = construct_url('weighting/exchanges')
        return self.get_result_from_url(url)
        # endregion

    # region Conversion
    def perform_conversion(self, market, _from, _to, amount):
        '''
        Return conversion from _from currency to _to currency, where one of _from and _to is valid crypto and the other
        valid fiat.
        '''
        url = construct_url('convert/{}?from={}&to={}&amount={}'.format(market, _from, _to, amount))
        return self.get_result_from_url(url)

    def perform_conversion_local(self, _from, _to, amount):
        '''
        Return conversion from _from currency to _to currency, where one of _from and _to is valid crypto and the other
        valid fiat.
        '''
        return self.perform_conversion('local', _from, _to, amount)

    def perform_conversion_global(self, _from, _to, amount):
        '''
        Return conversion from _from currency to _to currency, where one of _from and _to is valid crypto and the other
        valid fiat.
        '''
        return self.perform_conversion('global', _from, _to, amount)

    # endregion

    def blockchain_tx_price(self, symbol, hash):
        '''
        Returns the price for the specified symbol at the time the hash transaction was confirmed.
        '''
        url = construct_url('blockchain/tx_price/{}/{}'.format(symbol, hash))
        return self.get_result_from_url(url)

    def get_ticket(self):
        '''
        Returns ticket used in the websocket authentication process.
        '''
        url = construct_url('websocket/get_ticket')
        return self.get_result_from_url(url)

    def get_ticket_v2(self):
        url = construct_url('websocket/v2/get_ticket')
        return self.get_result_from_url(url)