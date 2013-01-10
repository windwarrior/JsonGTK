import threading
import requests
import json

from requests import RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects
"""
Extend this class to provide notify/observer functionality
"""
class Subject():
    def __init__(self):
        self.observer = []
    
    """
    Attaches a new observer to this object
    """
    def attach(self, observer):
        self.observers.append(observer)

    """
    Detaches a specified observer
    """
    def detach(self, observer):
        try:
            self.observers.remove(observer)
        except:
            pass

    """
    Notifies observers that something changed
    """
    def notify(self):
        print "updating observers!"
        for observer in self.observers:
            print "update obs: %s" % str(observer)
            observer.update(self)

"""
Representation of a JSON-RPC request
"""
class JSONRequest(Subject):
    def __init__(self, server, method, arguments):
        self.server = server
        self.method = method
        self.arguments = arguments
        self.observers = []
        self.result = None

    def do_json_request(self):
        json_thread = threading.Thread(target=self._request)
        json_thread.start()

    """
    This method is blocking
    """
    def _request(self):
        payload =  {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.arguments,
            "id": 9001,
        }

        try:
            r = requests.post(self.server, data=json.dumps(payload))
            self.result = r.json
            self.error = None
        except (RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects) as e:
            print e
            self.result = None
            self.error = "Dat ging mis"

        self.notify()
