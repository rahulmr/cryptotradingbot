import pandas as pd
import ccxt
import time
from time import strftime, gmtime

def api_connection(key: str,
                   secret: str,
                   password: str,
                   ):
    cbpro = ccxt.coinbasepro()
    cbpro.apiKey = key
    cbpro.secret = secret
    cbpro.password = password

def update_prices(csv: str,
                    csv_size: int,
                    ticker: str = 'BTC/USD',
                  ):
    market = cbpro.fetch_ticker(ticker)
    price = market['last']

    price_data = pd.read_csv(csv)
    date_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    new_data = {'datetime':[date_time], 'price':[price]}
    new_row = pd.DataFrame(data = new_data)
    price_updated = pd.concat([price_data, new_row], ignore_index=True)

    if len(price_updated) > csv_size:
        price_updated = price_updated.iloc[-csv_size:]
        price_updated.to_csv(csv, index=False)
    else:
        price_updated.to_csv(csv, index=False)

def mac_trade(short_ma: int,
              long_ma: int,
              ticker: str = 'BTC/USD'
              ):
    short = price_updated['price'].iloc[-short_ma:].mean()
    long = price_updated['price'].iloc[-long_ma:].mean()

    balances = cbpro.fetch_balance()
    ex_status = cbpro.fetch_status()

    # checking if exchange is up and trading is live
    if ex_status['status'] == 'ok':
        # checking if the short MA is above the long MA (bullish)
        if short > long:
            # checking if you have an adequate balance
            if (float(balances['info'][1]['balance']) * price) <= float(balances['info'][7]['balance']):
                usd_bal = float(balances['info'][7]['balance'])
                amount = str(usd_bal / price)
                cbpro.create_market_buy_order(ticker, amount)

        elif short <= long:

            if (float(balances['info'][1]['balance']) * price) > float(balances['info'][7]['balance']):
                amount = float(balances['info'][1]['balance'])
                cbpro.create_market_sell_order(ticker, amount)

    # remove cached orders from over an hour ago
    before = cbpro.milliseconds() - 24 * 60 * 60 * 1000
    cbpro.purge_cached_orders(before)


starttime = time.time()

while True:
  api_connection()
  update_prices()
  mac_trade()
  time.sleep(300.0 - ((time.time() - starttime) % 300.0))
  # change both numbers to how long you want it to wait before it runs again in seconds (both should be same number)
