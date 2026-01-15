from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
import requests
import core.osc_handler as osc_handler


class osc:
    def __init__(self):
        self.name = "OSC Module"

    def get_params(self):
        resp = requests.get("http://127.0.0.1:9001")
        data = resp.json()

        def walk(node, prefix=""):
            for k,v in node.get("CONTENTS", {}).items():
                path = prefix + "/" + k
                print(path, v.get("TYPE"))
                walk(v, path)

        walk(data)

    def start_listener(self):
        self.disp = Dispatcher()
        self.disp.map("/avatar/parameters/*", osc_handler.OSCHandler.map_message) 
        self.server = BlockingOSCUDPServer(("127.0.0.1", 9002), self.disp)
        self.server.serve_forever()