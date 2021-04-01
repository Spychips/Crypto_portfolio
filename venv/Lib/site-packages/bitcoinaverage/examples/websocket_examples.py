from bitcoinaverage.clients.websocket_client import TickerWebsocketClient

if __name__ == '__main__':
    secret2 = input('Enter your secret key: ')
    public2 = input('Enter your public key: ')

    print('Connecting to the ticker websocket...')
    ws = TickerWebsocketClient(public2, secret2)
    ws.ticker_data('local', 'BTCUSD')
