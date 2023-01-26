# LimitedSniper 
### A project by Jeldo#9587

## Please read before using!
## Getting your roblox cookie

### Method 1
**THE ROBLOX COOKIE THAT CAN BE FOUND IN YOUR COOKIES IS NOT THE SAME COOKIE PLEASE FOLLOW THIS GUIDE**
* Open roblox in your browser.
* Open the developer console by pressing: "CTRL+SHIFT+F11"
* Navigate to the "Network"
* Reload the page
* Scroll all the way up to the start and open the tab thats there. It should a blue box with blue lines in it.
* Scroll down to the Request headers tab. Then search for the cookie item.
* Thats it you're now done!

### Method 2
* Install https://github.com/J3ldo/Roblox-Token-Fetcher
* Follow the steps
* Get the full roblox token.

**Any problems or bugs? Please message J3ldo#9587 on discord or create an issue.**

## How to use
Here you will read a simple step-by-step guide about how the program works and how to install it.
* Git clone the repository or install it from the releases
* install pythin and after that the requests module   
* Run the config.exe or the config.py file and fill in the needed information.
* Open the sniper.exe or sniper.py file and see as it snipes limiteds!   
If you run in to any issues message **Jeldo#9587** on discord for help.

### Notes: 
* More then 10 limiteds is not reccommended as you will run into ratelimits
* This DOES NOT steal your roblox cookie. You can check the source code.
* The .exe is the same as the .py files
* Feel free to make suggestions or fork this repository.


## How it works
### Simple explanation
Once the program is opened it will go through all items in parralel and then ask roblox for the price on the item. If the price equals or is lower then the expected price it will start buying it. The buying will be done by replecating a real user on the site by asking roblox to buy it using your roblox cookie. Once this is done the program will send the notification through the webhook if on, print out the status to the console, and finally log all information to the logs file.


### In-depth explanation
Once the programs starts it will initialize a continiously running thread that grabs the x-csrf-token every 10 minutes. After that every asset id gets assigned its own thread and sends a request to the store page then grabs the price using regex. If the price is lower or equeals the expected price then it will start buying the item.  
Since the x-csrf-token is already gotten it will put it in. After that it grabs the already gotten product id from the config. And finally it will give the roblox token and send the request to roblox.  
When a response comes back a log is generated based upon it. And then if the webhook is on sends a notification using said webhook.
