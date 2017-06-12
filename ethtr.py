import requests
import time
import datetime
import json
import cexapi
from twilio.rest import Client
from config import *
from sys import argv


# colors for terminal output
class bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


""" cex api public endpoint"""
api = 'https://api.coinmarketcap.com/v1'
endpoint = '/ticker/'
params = '?convert=EUR&limit=10'


url = api+endpoint+params

""" update interval for api calls """
update_int = 600  # every 10 minutes

""" setup twilio client """
client = Client(account_sid, auth_token)

""" setup cex.io api '"""
cex = cexapi.API(username, api_key, api_secret)

""" holds past values of price """
past_values = ['0']
past_values_numeric = []
holds = 10  # max length of past_values list

while True:
    resp = requests.get(url)
    if resp.status_code != 200:
        print("api error: {}".format(resp.text))
    else:
        data = json.loads(resp.text)
        for entry in data:

            if isinstance(entry, dict):
                if 'id' in entry and entry['id'] == 'ethereum':
                    print(entry['name'], "CEX.IO Tracker", time.strftime('%l:%M%p %Z on %b %d, %Y'), '\n')

                    """ percentage changes 1 hour 1 day 7 days """
                    print("Change 1 hour:  {} %  | ".format(entry['percent_change_1h']), end="")
                    print("24 hour: {} % | ".format(entry['percent_change_24h']),end="")
                    print("7 days:  {} %".format(entry['percent_change_7d']))

                    """ latest price in EUR """
                    last_price = cex.ticker()['last']
                    print(ticker +":        {:.2f}".format(float(last_price)))

                    """ get wallet balance """
                    wallet = cex.balance()
                    if wallet is None:
                        print("Api error ")
                        break
                    eth_wallet = float(wallet['ETH']['available'])

                    """ calculate net  """
                    net = eth_wallet * float(last_price)
                    print("Net:         {:.2f} EUR  |".format(net))

                    """ calculate profit or loss """
                    profit = net - investment - fees
                    if profit > 0:
                        print("Profit:      " + bcolors.GREEN+"{:.2f} EUR  ".format(profit) +bcolors.ENDC+  "| ", end="")
                    else:
                        print("Profit:      " + bcolors.FAIL + "{:.2f} EUR  ".format(profit) +bcolors.ENDC+  "| ", end="")

                    """ calculate return of investment percentage """
                    if net / float(investment) <= 1:
                        calc = (1 - (net / float(investment)))
                        print("ROI: " + bcolors.FAIL + "-{:.2f} %".format(100 * calc) +bcolors.ENDC)
                    else:
                        calc = (net / float(investment)) - 1
                        print("ROI:  " + bcolors.GREEN + "+{:.2f} %".format(100 * calc) + bcolors.ENDC)

                    print("Wallet:   {} ETH".format(eth_wallet))

                    """ get high low values """
                    hl = cex.ticker(ticker)
                    if hl is None:
                        print("Api error")
                        break
                    print("\nLow: {0:.2f} EUR  ".format(float(hl['low'])), end="")
                    print("High: {0:.2f} EUR".format(float(hl['high'])))

                    """ update history of previews price update """
                    past_values_numeric.append(float(entry['price_eur']))   # store always numeric value price
                    if past_values[-1] < entry['price_eur']:     # use new  price is up use green color
                        past_values.append(bcolors.GREEN + entry['price_eur'][:6] + bcolors.ENDC)
                    elif past_values[-1] == entry['price_eur']:  # use new  price hasn't changed use no color
                        past_values.append(entry['price_eur'][:6])
                    else:  # use new  price is less use red color
                        past_values.append(bcolors.FAIL + entry['price_eur'][:6] + bcolors.ENDC)
                    if len(past_values) == holds + 1:      # remove values very old price value
                        past_values.pop(0)
                        past_values_numeric.pop(0)


                    """ print historic data """
                    print("Past ticks: ", end="")
                    for val in past_values:
                        print(val+" ", end="")
                    print("")

                    minutes = (update_int/60) * len(past_values_numeric)
                    mean_price = sum(past_values_numeric) / float(len(past_values_numeric))
                    print("Average price {:d}m : {:.2f}".format(int(minutes), mean_price))

                    human_time = datetime.datetime.fromtimestamp(int(entry['last_updated'])).strftime('%d-%m-%Y %H:%M:%S')
                    print(bcolors.MAGENTA + "Last Updated:   {:s}".format(human_time) + bcolors.ENDC)

                    print('\n')
                    """ send message to mobile  with latest infos """
                    if len(argv) == 2 and argv[1] in "-m":
                        print("Sending trading summary sms to mobile... ")
                        message_body = "Eth Track \n" +\
                                       "Wallet: {:.2f} ETH\n".format(eth_wallet) +\
                                       "Net: {:.2f} EUR\n".format(net) +\
                                       "Profit: {:.2f} EUR".format(profit)

                        message = client.api.account.messages.create(
                                                            to=my_num,
                                                            from_=twilio_num,
                                                            body=message_body)
                        if message is None:
                            print("Api error")
                            break
                    """
                    print("Converter {} EUR \n\n\n".format(cex.converter(eth_wallet, 'ETH/EUR')['amnt']))
                    """

    time.sleep(update_int)
