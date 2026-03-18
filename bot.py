import gate_api
from gate_api.exceptions import ApiException
import time
import statistics

API_KEY = "0e55899786ef71cff766231058c44c60"
API_SECRET = "be7c266787af72de428abdb83d9a4a145eb61124720a60a0a8a9a1740d0dd318"

COIN = "BTC_USDT"
MIKTAR = "0.00028"
STOP_LOSS = 0.02
TAKE_PROFIT = 0.04
BEKLEME = 10

configuration = gate_api.Configuration(
    host="https://api.gateio.ws/api/v4",
    key=API_KEY,
    secret=API_SECRET
)
api_client = gate_api.ApiClient(configuration)
spot_api = gate_api.SpotApi(api_client)

def fiyat_al(coin):
    ticker = spot_api.list_tickers(currency_pair=coin)
    return float(ticker[0].last​​​​​​​​​​​​​​​​
