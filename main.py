import requests as r
from json import load, dump
from threading import Thread
from time import sleep, perf_counter
from re import compile
from os import system
from datetime import datetime

'''
PIP INSTALLS:
pip install requests

'''

ID = '1'
x_token = None

# Checks for updates
print("Checking for updates...")
script = r.get("https://raw.githubusercontent.com/J3ldo/LimitedSniper/main/main.py").text
with open("main.py", "r") as f:
    if f.read() != script:
        print("Updating...")
        with open("main.py", "w") as f:
            f.write(script)
            input("Updated please reopen the script")
            exit(0)

# Create the file if it isnt already there.
with open("logs.txt", "w") as _:
    pass

# Get the current config file
with open("limiteds.json", "r") as f:
    config = load(f)

print("Logging in..")

debugging = config['DEBUG_MESSAGES']
roblosec = "_"+config["cookie"].split(".ROBLOSECURITY=_")[1]
results = []
perm_results = []
rate_limit = False
times_taken = []
time_to_sleep = 2


# This function gets your x-csrf token from roblox. This is needed to buy the limited.
def get_xtoken():
    global x_token

    x_token = r.post("https://auth.roblox.com/v2/logout",
                     headers={'cookie': ".ROBLOSECURITY=" + roblosec}).headers["x-csrf-token"]
    print("Logged in.")

    while 1:
        # Gets the x_token every 5 minutes.
        x_token = r.post("https://auth.roblox.com/v2/logout",
                         headers={'cookie': ".ROBLOSECURITY=" + roblosec}).headers["x-csrf-token"]
        sleep(120)


# This function will print all the results gotten.
def print_results(results: list, time_taken: float):
    system('cls')
    print("".join(i+"\n" for i in results))
    print(f"Time taken: {round(time_taken, 4)}s")


# The main function that checks an asset and snipes if possible.
def snipe_item(data):
    global results, perm_results, rate_limit
    start = perf_counter()

    out = r.get(f"https://www.roblox.com/catalog/{data['asset']}",
                headers={"cookie": config['cookie']}, cookies={".ROBLOSECURITY": roblosec}).content

    items = compile(r"data-expected-price=.*")

    matches = items.finditer(str(out))
    price = 9e+10
    for i in matches:
        price = int(i.group()[21:].split("\"")[0]) if i.group()[21:].split("\"")[0] != "" else price

    if price == 9e+10:
        rate_limit = True
        return

    if debugging:
        results.append(f'Got price of {price}')

    times_taken.append(perf_counter() - start)
    if price >= int(data["price"]):
        sleep(time_to_sleep)
        return

    print("Found limited under the specified price.")

    # The the user id of the seller
    items = compile(r"data-expected-seller-id=.*")

    matches = items.finditer(str(out))
    seller_id = "0"
    for i in matches:
        seller_id = str(i.group()[24:].split("\"")[1])

    # Gets the special id for the limited
    items = compile(r"data-lowest-private-sale-userasset-id.*")

    matches = items.finditer(str(out))
    unique_id = "0"
    for i in matches:
        unique_id = str(i.group()[38:].split("\"")[1])

    # Start buying the limited
    print("Buying limited..")

    headers = {
        'cookie': config['cookie'],
        "x-csrf-token": x_token
    }
    payload = {
        "expectedCurrency": "1",
        "expectedPrice": str(price),
        "expectedSellerId": seller_id,
        "userAssetId": unique_id
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
                    "Information: \n"
                    f"Purchased: {check.json()['purchased']}\n"
                    f"Asset bought: {check.json()['assetName']}\n"
                    f"Asset type: {check.json()['assetType']}\n"
            )
            with open("logs.txt", "a") as f:
                f.write(f"\n\n\nGot a respone code of: {check.status_code}. Reason: {check.reason}\n\n"
                        f"All info: \n"
                        f"Sent request: {payload}\n"
                        f"Json: \n"
                        f"{check.json()}\n\n"
                        f"Sent info: \n{payload}\n\n"
                        f"Headers: \n"
                        f"{check.headers}\n"
                        f"Bought for: {price}\n\n\n")
            r.post(config["webhook"], data={'content': f"{'@everyone' if config['pingall'] else ''} | Just bought "
                                                        f"https://www.roblox.com/catalog/{data['asset']} for {price} robux"})

            if not data['buyagain']:
                config['limiteds'].remove(data)
                with open('limiteds.json', 'w') as f:
                    dump(config, f, indent=4)
        except Exception as e:
            import traceback
            print("Tried to buy the limited but something went wrong.\n\n"
                    f"Information: \n"
                    f"Exception: {e}\n"
                    f"Sent request: {payload}\n"
                    f"Json: {check.json()}\n"
                    f"Reason: {check.reason}\n"
                    f"Asset bought: {check.headers}\n"
                    f"CSRF TOKEN: {x_token}")
            with open("logs.txt", "a") as f:
                f.write(
                    f"\n\n\nSomething went wrong whilst buying the item.\nGot a respone code of: {check.status_code}. "
                    f"Reason: {check.reason}\n\n"
                    f" Exception: {e}\n\n"
                    f"All info: \n"
                    f"Json: \n"
                    f"{check.json()}\n\n"
                    f"Sent info: \n{payload}\n\n"
                    f"Headers: \n"
                    f"{check.headers}\n\n\n")
            r.post(config["webhook"], data={
                'content': f"{'@everyone' if config['pingall'] else ''} | Something went wrong whilst buying"
                            f" https://www.roblox.com/catalog/{data['asset']} for {price}. "
                            f"See logs for more information."})

    else:
        print("Tried to buy the limited but something went wrong.\n\n"
                f"Information: \n"
                f"Sent request: {payload}\n"
                f"Json: {check.json()}\n"
                f"Reason: {check.reason}\n"
                f"Asset bought: {check.headers}\n"
                f"CSRF TOKEN: {x_token}")
        with open("logs.txt", "a") as f:
            f.write(f"\n\n\nSomething went wrong whilst buying the item.\nGot a respone code of: {check.status_code}."
                    f" Reason: {check.reason}\n\n"
                    f"All info: \n"
                    f"Json: \n"
                    f"{check.json()}\n\n"
                    f"Send info: \n{payload}\n\n"
                    f"Headers: \n"
                    f"{check.headers}\n\n\n")
        r.post(config["webhook"], data={'content': f"{'@everyone' if config['pingall'] else ''} | Something went wrong whilst buying "
                                                    f"https://www.roblox.com/catalog/{data['asset']} for {price}. See the logs for more information."})


# Main function. Runs the sniping
def main():
    global results, perm_results, rate_limit, time_to_sleep, times_taken
    x_get = Thread(target=get_xtoken)
    x_get.start()

    while len(config['limiteds']) > 0:
        times_taken = []

        if rate_limit:
            # Uptime is 40 seconds for 10 limiteds.
            # Rate limit is 200 limiteds
            print("Ran in to a rate limit. Waiting for the next minute to start..")
            sleep(60 - datetime.now().second)
            rate_limit = False

        threads = []

        # Initialize all the threads
        for i in range(len(config['limiteds'])):
            threads.append(Thread(target=snipe_item, args=(config['limiteds'][i],)))

        start = perf_counter()
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        try: time_to_sleep = 0.325789474*len(config['limiteds'])-sum(times_taken)/len(times_taken) # 3.15789474 should be the right time but its an average
        except ZeroDivisionError: time_to_sleep = time_to_sleep
        time_to_sleep = time_to_sleep if time_to_sleep >= 0 else 0

        time_taken = perf_counter()-start

        # Sleep to stop rate limiting. And print out the results
        print_results(results, time_taken)
        # to_sleep = (0.255 - time_taken * 0.1) * len(config['limiteds'])
        # sleep(time_taken*0.6)#to_sleep if to_sleep >= 0 else 0)

        results = perm_results[:]


if __name__ == '__main__':
    main()
