from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading

class OSCSniffer:
    def __init__(self, port=9001):
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        self.last_address = None
        self.listeners = []

    def add_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def remove_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def start(self):
        if self.running:
            return
        
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._handler)
        
        try:
            self.server = ThreadingOSCUDPServer(("0.0.0.0", self.port), dispatcher)
            self.running = True
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            print(f"OSC Sniffer started on port {self.port}")
        except Exception as e:
            print(f"Failed to start OSC Sniffer: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        self.running = False
        print("OSC Sniffer stopped")

    def _handler(self, address, *api_args):
        self.last_address = address
        # print(f"Sniffed: {address}")
        for listener in self.listeners:
            try:
                listener(address, api_args)
            except Exception as e:
                print(f"Error in OSC listener: {e}")
