import time
import requests as r
from json import load, dump
from threading import Thread
from time import sleep, perf_counter
from re import compile
from os import system

'''
PIP INSTALLS:
pip install requests

'''

ID = '1'
x_token = None

# Create the file if it isnt already there.
with open("logs.txt", "w") as _:
    pass

# Get the current config file
with open("limiteds.json", "r") as f:
    config = load(f)

print("Logged in.")

debugging = config['DEBUG_MESSAGES']
roblosec = "_"+config["cookie"].split(".ROBLOSECURITY=_")[1]


# This function gets your x-csrf token from roblox. This is needed to buy the limited.
def get_xtoken():
    global x_token

    # Gets the x_token every 5 minutes.
    x_token = r.post("https://auth.roblox.com/v2/logout",
                     headers={'cookie': ".ROBLOSECURITY=" + roblosec}).headers["x-csrf-token"]
    sleep(600)


# This function will print all the results gotten.
def print_results(results: list, time_taken: float):
    system('cls')
    print("".join(i+"\n" for i in results))
    print(f"Time taken: {round(time_taken, 4)}s")


# The main function that checks an asset and snipes if possible.
def snipe_item(data):
    global results, perm_results
    out = r.get(f"https://www.roblox.com/catalog/{data['asset']}",
                headers={"cookie": config['cookie']}, cookies={".ROBLOSECURITY": roblosec}).content

    items = compile(r"data-expected-price=.*")

    matches = items.finditer(str(out))
    price = '-0'
    for i in matches:
        price = int(i.group()[21:].split("\"")[0])

    if debugging:
        results.append(f'Got price of {price}')
    if price <= int(data["price"]):
        print("Found limited under the specified price.")

        items = compile(r"data-expected-seller-id=.*")

        matches = items.finditer(str(out))
        seller_id = 0
        for i in matches:
            seller_id = int(i.group()[24:].split("\"")[1])

        print("Buying limited..")

        headers = {
            'cookie': config['cookie'],
            "x-csrf-token": x_token
        }
        payload = {
            "expectedCurrency": "1",
            "expectedPrice": str(price),
            "expectedSellerId": str(seller_id),
        }

        check = r.post(f"https://economy.roblox.com/v1/purchases/products/{data['productid']}",
                       headers=headers, data=payload)

        if check.ok:
            try:
                print("Bought the limited. With a response of 200 (Succes)\n\n"
                      f"Information: \n"
                      f"Purchased: {check.json()['purchased']}\n"
                      f"Asset bought: {check.json()['assetName']}\n"
                      f"Asset type: {check.json()['assetType']}\n\n"
                      f"All data: "
                      f"{check.json()}")

                perm_results.append(
                      "Bought the limited. With a response of 200 (Succes)\n\n"
                      f"Information: \n"
                      f"Purchased: {check.json()['purchased']}\n"
                      f"Asset bought: {check.json()['assetName']}\n"
                      f"Asset type: {check.json()['assetType']}\n"
                )
                with open("logs.txt", "a") as f:
                    f.write(f"\n\n\nGot a respone code of: {check.status_code}. Reason: {check.reason}\n\n"
                            f"All info: \n"
                            f"Json: \n"
                            f"{check.json()}\n\n"
                            f"Headers: \n"
                            f"{check.headers}\n"
                            f"Bought for: {price}\n\n\n")
                r.post(config["webhook"], data={'content': f"{'@everyone' if config['pingall'] else ''} | Just bought "
                                                           f"https://www.roblox.com/catalog/{data['asset']} for {price} robux"})

                if not data['buyagain']:
                    config['limiteds'].pop(data)
                    with open('limiteds.json', 'w') as f:
                        dump(config, f, indent=4)
            except:
                print("Tried to buy the limited but something went wrong.\n\n"
                      f"Information: \n"
                      f"Json: {check.json()}\n"
                      f"Asset bought: {check.headers}\n")
                with open("logs.txt", "a") as f:
                    f.write(
                        f"\n\n\nSomething went wrong whilst buying the item.\nGot a respone code of: {check.status_code}. "
                        f"Reason: {check.reason}\n\n"
                        f"All info: \n"
                        f"Json: \n"
                        f"{check.json()}\n\n"
                        f"Headers: \n"
                        f"{check.headers}\n\n\n")
                r.post(config["webhook"], data={
                    'content': f"{'@everyone' if config['pingall'] else ''} | Something went wrong whilst buying"
                               f" https://www.roblox.com/catalog/{data['asset']} for {price}. "
                               f"See logs for more information."})

        else:
            print("Tried to buy the limited but something went wrong.\n\n"
                  f"Information: \n"
                  f"Json: {check.json()}\n"
                  f"Asset bought: {check.headers}\n")
            with open("logs.txt", "a") as f:
                f.write(f"\n\n\nSomething went wrong whilst buying the item.\nGot a respone code of: {check.status_code}."
                        f" Reason: {check.reason}\n\n"
                        f"All info: \n"
                        f"Json: \n"
                        f"{check.json()}\n\n"
                        f"Headers: \n"
                        f"{check.headers}\n\n\n")
            r.post(config["webhook"], data={'content': f"{'@everyone' if config['pingall'] else ''} | Something went wrong whilst buying "
                                                       f"https://www.roblox.com/catalog/{data['asset']} for {price}. See the logs for more information."})


# Main function. Runs the sniping
def main():
    results = []
    perm_results = []
    x_get = Thread(target=get_xtoken)
    x_get.start()
    while len(config['limiteds']) > 0:
        threads = []

        # Initialize all the threads
        for i in range(len(config['limiteds'])):
            threads.append(Thread(target=snipe_item, args=(config['limiteds'][i],)))

        start = perf_counter()
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        time_taken = time.perf_counter()-start

        # Sleep to stop rate limiting. And print out the results
        print_results(results, time_taken)
        to_sleep = (0.255 - time_taken * 0.1) * len(config['limiteds'])
        sleep(to_sleep if to_sleep >= 0 else 0)

        results = perm_results


if __name__ == '__main__':
    main()
