#pip install beautifulsoup4
from bs4 import BeautifulSoup as bs
#pip install requests
import requests as r
#needed for bs4
import lxml



#asset you want to snipe
#asset is the asset id
#minprice is the price it needs to notify you
def asset(asset, minprice):
    return {"id" : asset, "price" : minprice}
print("Copyright J3ldo, 2022-2023\n")

n = input("Please put it in like so '0(asset id) 69(max price),(comma for another one) 1(asset id) 70(max price)'\n> ")
#splits the choice
choice = n.split(', ')
id = []
for i in choice:
    q = i.split()
    id.append(asset(q[0], q[1]))


#sees if you want to ping everyone
peveryone = input("Do you want to ping everyone Y/N ?\n> ")
ping_everyone = True if peveryone.lower() == 'y' else False
#webhook url
webhookurl = input("Whats the webhook url?\n> ")
webhook = webhookurl

print('The program will stop running when it will have found 1 item.')
running = True
while running:
    for i in id:
        url1 = f'https://www.roblox.com/catalog/{str(i["id"])}/'

        #gets site
        site = r.get(url1).text
        soup = bs(site, "lxml")

        #gets the item price
        price = soup.find("span", class_="text-robux-lg wait-for-i18n-format-render").text

        #removes the comma
        nprice = list(price)
        pprice = ""
        for f in list(price):
            if f == ',':
                nprice.remove(f)
            else:
                pprice += f



        if int(pprice) <= int(i["price"]):
            ping = "@everyone" if ping_everyone else ''
            r.post(webhook, data={"content" : f"<{url1}> is on sale for {price} robux! {ping}"})
            print(f'Found the item for {price}!')
            running = False
            break
        else:
            print("Did not find a price thats lower than", i["price"])
