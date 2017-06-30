#!/usr/bin/python3

import json
import time

import requests
import websocket


TIMEOUT = 1

message_id = 0


class GenericElement(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = self.name + "." + attr

        def generic_function(**args):
            global message_id
            self.parent.pop_messages()
            message_id += 1
            call_obj = {"id": message_id, "method": func_name, "params": args}
            self.parent.ws.send(json.dumps(call_obj))
            result, _ = self.parent.wait_result(message_id)
            return result
        return generic_function


class ChromeInterface(object):
    def __init__(self, host='localhost', port=9222, tab=0):
        self.host = host
        self.port = port
        self.ws = None
        self.tabs = None
        self.get_tabs()
        self.connect(tab=tab)

    def get_tabs(self):
        response = requests.get("http://%s:%s/json" % (self.host, self.port))
        self.tabs = json.loads(response.text)

    def connect(self, tab=0, update_tabs=True):
        wsurl = self.tabs[tab]['webSocketDebuggerUrl']
        self.ws = websocket.create_connection(wsurl)
        self.ws.settimeout(TIMEOUT)

    def close(self):
        if self.ws:
            self.ws.close()

    # Blocking
    def wait_message(self, timeout=TIMEOUT):
        self.ws.settimeout(timeout)
        try:
            message = self.ws.recv()
        except:
            self.ws.settimeout(TIMEOUT)
            return None
        self.ws.settimeout(TIMEOUT)
        return json.loads(message)

    # Blocking
    def wait_event(self, event, timeout=TIMEOUT):
        start_time = time.time()
        messages = []
        matching_message = None
        while True:
            now = time.time()
            if now-start_time > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if "method" in parsed_message and parsed_message["method"] == event:
                    matching_message = parsed_message
                    break
            except:
                break
        return (matching_message, messages)

    # Blocking
    def wait_result(self, result_id, timeout=TIMEOUT):
        start_time = time.time()
        messages = []
        matching_result = None
        while True:
            now = time.time()
            if now-start_time > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if "result" in parsed_message and parsed_message["id"] == result_id:
                    matching_result = parsed_message
                    break
            except:
                break
        return (matching_result, messages)

    # Non Blocking
    def pop_messages(self):
        messages = []
        self.ws.settimeout(0)
        while True:
            try:
                message = self.ws.recv()
                messages.append(json.loads(message))
            except:
                break
        self.ws.settimeout(TIMEOUT)
        return messages

    def __getattr__(self, attr):
        genericelement = GenericElement(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement
