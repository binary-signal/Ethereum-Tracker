import requests
import time
import datetime
import json
import cexapi
from twilio.rest import Client
from config import twilio_num, my_num, api_key, api_secret, account_sid, \
    username, auth_token
from sys import argv


# color for terminal output
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# cexapi
api = 'https://api.coinmarketcap.com/v1'
endpoint = '/ticker/'
params = '?convert=EUR&limit=10'
update_int = 500  # every 5 minutes

url = api + endpoint + params

client = Client(account_sid, auth_token)

cex = cexapi.API(username, api_key, api_secret)
investement = 50  # in euro
fees = 2.96

past_values = ['-']
holds = 10  # past_values limit

while True:
    resp = requests.get(url)
    if resp.status_code != 200:
        print("api error: {}".format(resp.text))
    else:
        data = json.loads(resp.text)
        for entry in data:

            if isinstance(entry, dict):
                if 'id' in entry and entry['id'] == 'ethereum':
                    print(entry['name'], "CEX.IO Tracker",
                          time.strftime('%l:%M%p %Z on %b %d, %Y'), '\n')

                    print("Change 1 hour:  {} %  | ".format(
                        entry['percent_change_1h']), end="")
                    print(
                        "24 hour: {} % | ".format(entry['percent_change_24h']),
                        end="")
                    print("7 days:  {} %".format(entry['percent_change_7d']))

                    ticker_usd = cex.ticker('ETH/USD')['last']
                    print("Price in USD:   {0:.2f} ".format(
                        float(ticker_usd)), end="")

                    ticker_eur = cex.ticker('ETH/EUR')['last']
                    print(" | Euro:  {0:.2f}".format(
                        float(ticker_eur)))

                    wallet = cex.balance()
                    eth_wallet = float(wallet['ETH']['available'])

                    net = eth_wallet * float(ticker_eur)
                    print("Net:         {0:.2f} EUR  |".format(net))
                    profit = net - investement - fees
                    if profit > 0:
                        print(
                            "Profit:      " + bcolors.OKGREEN + "{0:.2f} EUR  ".format(
                                profit) + bcolors.ENDC + "| ", end="")
                    else:
                        print(
                            "Profit:      " + bcolors.FAIL + "{0:.2f} EUR  ".format(
                                profit) + bcolors.ENDC + "| ", end="")

                    if net / float(investement) <= 1:
                        calc = (1 - (net / float(investement)))
                        print("ROI: " + bcolors.FAIL + "-{0:.2f} %".format(
                            100 * calc) + bcolors.ENDC)
                    else:
                        calc = (net / float(investement)) - 1
                        print("ROI:  " + bcolors.OKGREEN + "{0:.2f} %".format(
                            100 * calc) + bcolors.ENDC)

                    print("Wallet:   {} ETH".format(eth_wallet))

                    ohlc = cex.ticker('ETH/EUR')
                    print("\nLow: {0:.2f} EUR / High: {0:.2f} EUR".format(
                        float(ohlc['low']), float(ohlc['high'])))
                    if past_values[-1] < entry['price_eur']:
                        past_values.append("up")
                    elif past_values[-1] == entry['price_eur']:
                        past_values.append("steady")
                    else:
                        past_values.append("down")
                    if len(past_values) == holds + 1:
                        past_values.pop(0)

                    print("Past ticks: ", end="")
                    for val in past_values:
                        print("{} ".format(val), end="")
                    print("")
                    print(bcolors.WARNING + "Last Updated:   {}".format(
                        datetime.datetime.fromtimestamp(
                            int(entry['last_updated'])).strftime(
                            '%d-%m-%Y %H:%M:%S')) + bcolors.ENDC)

                    print('\n')
                    if len(argv) == 2 and argv[1] in "-m":
                        print("Sending trading summary sms to mobile... ")
                        message_body = "\nEth Track \n" + "Wallet: {0:.2f} ETH\n".format(
                            eth_wallet) + "Net: {0:.2f} EUR\n".format(
                            net) + "Profit: {0:.2f} EUR".format(profit)
                        message = client.api.account.messages.create(
                            to=my_num,
                            from_=twilio_num,
                            body=message_body)
                    print("Converter {} EUR".format(
                        cex.converter(eth_wallet, 'ETH/EUR')['amnt']))
                    print("\n\n\n")

    time.sleep(update_int)
