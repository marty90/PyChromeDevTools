#!/usr/bin/python3
import json
import requests
import websocket
import time

TIMEOUT=1

class GenericElement(object):
    def __init__(self,name,parent):
        self.name=name
        self.parent=parent
    def __getattr__(self, attr):
        func_name=self.name+"."+attr
        def GenericFunction(**args):
            self.parent.pop_messages()
            call_obj={"id": 0, "method": func_name, "params": args}
            self.parent.soc.send(json.dumps(call_obj))
            return json.loads(self.parent.soc.recv())
        return GenericFunction

class ChromeInterface(object):
    def __init__(self, host='localhost', port=9222,tab=0):
        self.host = host
        self.port = port
        self.soc = None
        self.tablist = None
        self.find_tabs()
        self.connect(tab=tab)
    def find_tabs(self):
        response = requests.get("http://%s:%s/json" % (self.host, self.port))
        self.tablist = json.loads(response.text)
    def connect(self, tab=0, update_tabs=True):
        wsurl = self.tablist[tab]['webSocketDebuggerUrl']
        self.soc = websocket.create_connection(wsurl)
        self.soc.settimeout(TIMEOUT)
    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = None
    # Blocking
    def wait_message(self, timeout=TIMEOUT):
        self.soc.settimeout(timeout)
        try:
            message = self.soc.recv()
        except:
            self.soc.settimeout(TIMEOUT)
            return None
        self.soc.settimeout(TIMEOUT)
        return json.loads(message)
    # Blocking
    def wait_event(self, event,timeout=TIMEOUT):
        start_time=time.time()
        messages=[]
        matching_message=None
        while True:
            now=time.time()
            if now-start_time>timeout:
                break
            try:
                message = self.soc.recv()
                parsed_message=json.loads(message)
                messages.append(parsed_message)
                if "method" in parsed_message and parsed_message["method"]==event:
                    matching_message=parsed_message
                    break
            except:
                break
        return (matching_message, messages)

    # Non Blocking
    def pop_messages(self):
        messages=[]
        self.soc.settimeout(0)
        while True:
            try:
                message = self.soc.recv()
                messages.append(json.loads(message))
            except:
                break
        self.soc.settimeout(TIMEOUT)
        return messages

    def __getattr__(self, attr):
        genericelement=GenericElement(attr,self)
        self.__setattr__(attr,genericelement)
        return genericelement


