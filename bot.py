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

configuration = gate_api.Configuration(host="https://api.gateio.ws/api/v4", key=API_KEY, secret=API_SECRET)
api_client = gate_api.ApiClient(configuration)
spot_api = gate_api.SpotApi(api_client)

def fiyat_al(coin):
    ticker = spot_api.list_tickers(currency_pair=coin)
    return float(ticker[0].last)

def rsi_hesapla(fiyatlar, periyot=14):
    if len(fiyatlar) < periyot + 1:
        return None
    kazanlar, kayipler = [], []
    for i in range(1, len(fiyatlar)):
        fark = fiyatlar[i] - fiyatlar[i-1]
        if fark > 0:
            kazanlar.append(fark)
            kayipler.append(0)
        else:
            kazanlar.append(0)
            kayipler.append(abs(fark))
    ort_kazanc = statistics.mean(kazanlar[-periyot:])
    ort_kayip = statistics.mean(kayipler[-periyot:])
    if ort_kayip == 0:
        return 100
    rs = ort_kazanc / ort_kayip
    return 100 - (100 / (1 + rs))

def al(coin, miktar):
    try:
        fiyat = fiyat_al(coin)
        emir = gate_api.Order(currency_pair=coin, side="buy", amount=miktar, price=str(round(fiyat * 1.001, 1)), type="limit", time_in_force="ioc")
        sonuc = spot_api.create_order(emir)
        print("ALINDI: " + coin)
        return sonuc
    except ApiException as e:
        print("Alim hatasi: " + str(e))
        return None

def sat(coin, miktar):
    try:
        fiyat = fiyat_al(coin)
        emir = gate_api.Order(currency_pair=coin, side="sell", amount=miktar, price=str(round(fiyat * 0.999, 1)), type="limit", time_in_force="ioc")
        sonuc = spot_api.create_order(emir)
        print("SATILDI: " + coin)
        return sonuc
    except ApiException as e:
        print("Satis hatasi: " + str(e))
        return None

print("Bot baslatildi!")

fiyat_gecmisi = []
pozisyon = None
giris_fiyati = 0

while True:
    try:
        fiyat = fiyat_al(COIN)
        fiyat_gecmisi.append(fiyat)
        if len(fiyat_gecmisi) > 50:
            fiyat_gecmisi.pop(0)
        rsi = rsi_hesapla(fiyat_gecmisi)
        saat = time.strftime("%H:%M:%S")
        if rsi:
            print("[" + saat + "] Fiyat: " + str(fiyat) + " RSI: " + str(round(rsi, 1)) + " Pozisyon: " + ("ACIK" if pozisyon else "YOK"))
            if pozisyon is None:
                if rsi < 40:
                    print("[" + saat + "] AL SINYALI!")
                    sonuc = al(COIN, MIKTAR)
                    if sonuc:
                        pozisyon = "long"
                        giris_fiyati = fiyat
            elif pozisyon == "long":
                degisim = (fiyat - giris_fiyati) / giris_fiyati
                if degisim >= TAKE_PROFIT:
                    print("[" + saat + "] TAKE PROFIT!")
                    sat(COIN, MIKTAR)
                    pozisyon = None
                elif degisim <= -STOP_LOSS:
                    print("[" + saat + "] STOP LOSS!")
                    sat(COIN, MIKTAR)
                    pozisyon = None
        else:
            print("[" + saat + "] Veri toplaniyor: " + str(len(fiyat_gecmisi)) + "/15")
        time.sleep(BEKLEME)
    except Exception as e:
        print("Hata: " + str(e))
        time.sleep(10)
