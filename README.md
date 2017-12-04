# PyChromeDevTools

# 1. Description
PyChromeDevTools is a python module that allows one to interact with Google Chrome using [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) within a Python script.
To use this tool, you must run an instance of Google Chrome with the `remote-debugging` option, like in the following example.
```
google-chrome --remote-debugging-port=9222
```
You may want to enable further Chrome benchmarking capabilities using the `--enable-benchmarking` and `--enable-net-benchmarking` options. You can run Chrome in headless mode using the option `--headless`.

For information about this Readme file and this tool please write to
[martino.trevisan@polito.it](mailto:martino.trevisan@polito.it)

# 2. Prerequisites and Installation
Very few dependencies must be satisfied: an updated Google-Chrome version and the python packages `requests` and `websocket`.
You can install them using the `pip` tool.

You can install `PyChromeDevTools` issuing the git command:
```
git clone https://github.com/marty90/PyChromeDevTools
```
Or, better, you install it and its dependencies by using `pip`:
```
sudo pip3 install requests websocket-client git+git://github.com/marty90/PyChromeDevTools.git
```

# 3. Operation
## 3.1 Init
In your python script, as first, you must create a ChromeInterface object, like in the following:
```
chrome = PyChromeDevTools.ChromeInterface()
```
You can specify the host and the port of Chrome manually writing:
```
chrome = PyChromeDevTools.ChromeInterface(host="1.1.1.1",port=1234)
```
By default it uses `localhost:9222`.

You can connect directly to a `targetID` using the method `connect_targetID`. 
You must pass the `targetID` as parameter to this function.
In this case, you avoid querying the json and finding the `tab id`. 

## 3.1 Run commands
To send a command to Chrome, just invoke the corresponding method on the ChromeInterface object, and pass the desired parameters.
For example, to visit a page write:
```
chrome.Page.navigate(url="http://example.com/")
```
The return value of the command is passed as return value of the function, already interpreted as JSON.

## 3.1 Receive Events
Chrome sends back messages for particular events in the browser.
You can get them in three ways; they are returned already interpreted as JSON.
All unread events are erased before any new command is run.

a) You can pop one message from the queue of received ones writing:
```
message=chrome.wait_message()
```
The method accepts an optional parameter `timeout` which is the value in seconds after which it gives up and returns `None`.
Default is 1.

b) You can wait for a specific event writing:
```
matching_event,all_events=chrome.wait_event(event_name)
```
It waits until an event with the name `event_name` arrives, or a timeout elapses.
`matching_event` contains the first found event that has `event_name`, while `all_events` contains all events arrived before.
Timeout value can be configured as in the previous method.

c) You can get all already received messages writing:
```
messages=chrome.pop_messages()
```
This method is not blocking, and, thus, no timeout is used.

# 4. Examples
## 4.1 Page Loading Time
```
import PyChromeDevTools
import time

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

start_time=time.time()
chrome.Page.navigate(url="http://www.google.com/")
chrome.wait_event("Page.loadEventFired", timeout=60)
end_time=time.time()

print ("Page Loading Time:", end_time-start_time)
```

## 4.2 Print all installed cookies
```
import PyChromeDevTools
import time

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

chrome.Page.navigate(url="http://www.nytimes.com/")
chrome.wait_event("Page.frameStoppedLoading", timeout=60)

#Wait last objects to load
time.sleep(5)

cookies=chrome.Network.getCookies()
for cookie in cookies["result"]["cookies"]:
    print ("Cookie:")
    print ("\tDomain:", cookie["domain"])
    print ("\tKey:", cookie["name"])
    print ("\tValue:", cookie["value"])
    print ("\n")
```

## 4.3 Print all object URLs of a page
```
import PyChromeDevTools

chrome = PyChromeDevTools.ChromeInterface()
chrome.Network.enable()
chrome.Page.enable()

chrome.Page.navigate(url="http://www.facebook.com")
event,messages=chrome.wait_event("Page.frameStoppedLoading", timeout=60)

for m in messages:
    if "method" in m and m["method"] == "Network.responseReceived":
        try:
            url=m["params"]["response"]["url"]
            print (url)
        except:
            pass
```


