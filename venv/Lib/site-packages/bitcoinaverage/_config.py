SIGNATURE_HEADER = "X-Signature"
BETA_PREFIX = 'https://apiv2.bitcoinaverage.com/'
DEV_PREFIX = 'https://apiv2-dev.bitcoinaverage.com/'
LOCAL_PREFIX = 'http://localhost:8888/'

BETA_WEBSOCKET_PREFIX = 'wss://apiv2.bitcoinaverage.com/websocket/'

WEBSOCKET_UPDATE_FREQUENCY = 3  # Send updates every 3 seconds

def construct_url(params, prefix=BETA_PREFIX):
    return '{}{}'.format(prefix, params)
