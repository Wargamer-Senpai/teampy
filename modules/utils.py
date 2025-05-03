import os
import requests
import inspect

from modules.logger import func_write_to_log

def func_touch_file(filename):
  """touch a file to refresh the timestamp, is used inside a container as a keep alive

  Args:
      filename (str): file to touch
  """
  with open(filename, 'a'):
      os.utime(filename, None)

def func_container_check():
  """check if the bot runs inside an container

  Returns:
      bool: returns if it runs inside a container
  """
  if 'CONTAINER_BOOL' in os.environ:
    return True
  else:
    return False    

def func_fetch_coin_prices(coin_id, currencies):
  """fetch the coin price 

  Args:
      coin_id (str): the identifier of the coin (e.g. "BTC" or "ETH")
      currencies (list): a list of currency codes (e.g. ["gbp", "eur", "usd"]) to convert the coin price into

  Returns:
      dict: a dictionary with currency codes as keys and the corresponding coin prices as values
  """
  base_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies="
  prices = {}
  for currency in currencies:
    response = requests.get(base_url + currency)
    try: 
      prices[currency] = response.json()[coin_id][currency]
    except KeyError:
      prices[currency] = "N/A (Rate Limit Exceeded)"
      func_write_to_log(f"Error fetching price for {coin_id} in {currency}: {response.text}", "ERROR", inspect.currentframe().f_code.co_name)
  return prices