import pandas as pd
import ccxt
import time
from time import strftime, gmtime

# My motivation for writing this was to combat excessive costs in a running a real-time trading bot. Constantly checking
# trade status, streaming real-time prices, calculating multiple metrics on the fly, and updating records can really start to add
# up in costs for a casual retail trader. The point of this script is to create a simple MA crossover trading bot that executes only
# as often as you want it to.

def api_connection(key: str,
                   secret: str,
                   password: str,
                   ):
    """Establish API connection to Coinbase Pro."""
    cbpro = ccxt.coinbasepro()
    cbpro.apiKey = key
    cbpro.secret = secret
    cbpro.password = password

def update_prices(csv: str, # csv file path
                    csv_size: int # number of records you want to keep
                  ):
    """Pull current price for given ticker and update a CSV with new price + truncate length to keep file size small."""
    market = cbpro.fetch_ticker('BTC/USD')
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

def mac_trade(short_ma: int, # number of periods to calculate the short MA from
              long_ma: int # number of periods to calculate the long MA from
              ):
    """Caclulate two moving averages and trade if a crossover has happened."""
    """Balance comparison is to prevent future trading attempts if a trade has already been made."""
    short = price_updated['price'].iloc[-short_ma:].mean()
    long = price_updated['price'].iloc[-long_ma:].mean()

    balances = cbpro.fetch_balance()
    ex_status = cbpro.fetch_status()

    
    if ex_status['status'] == 'ok':
   
        if short > long:

            if (float(balances['info'][1]['balance']) * price) <= float(balances['info'][7]['balance']):
                usd_bal = float(balances['info'][7]['balance'])
                amount = str(usd_bal / price)
                cbpro.create_market_buy_order('BTC/USD', amount)

        elif short <= long:

            if (float(balances['info'][1]['balance']) * price) > float(balances['info'][7]['balance']):
                amount = float(balances['info'][1]['balance'])
                cbpro.create_market_sell_order('BTC/USD', amount)

    # remove cached orders from over an hour ago
    before = cbpro.milliseconds() - 24 * 60 * 60 * 1000
    cbpro.purge_cached_orders(before)


starttime = time.time()

while True:
  # input function parameters here
  api_connection()
  update_prices()
  mac_trade()
  time.sleep(300.0 - ((time.time() - starttime) % 300.0))
  # change both numbers to how long you want it to wait before it runs again in seconds (both should be same number)
