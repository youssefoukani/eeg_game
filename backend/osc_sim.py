import time
import random
from pythonosc.udp_client import SimpleUDPClient

class OSC_Sender:
    def __init__(self, ip = "127.0.0.1", port = 5005):
        self.ip = ip
        self.port = port
        self.client =  SimpleUDPClient(self.ip, self.port)

    def send_prediction(self, prediction):

        try:
            self.client.send_message("/bci/prediction", prediction)
            print(f" -> Inviata predizione: {prediction}")
            
        except KeyboardInterrupt:
            print("\n[MOCK BACKEND] Simulazione interrotta.")

    def send_quality(self, quality):
        try:
            self.client.send_message("/bci/quality", quality)
            print(f" -> Inviata qualità canali: {quality}")
            
        except KeyboardInterrupt:
            print("\n[MOCK BACKEND] Simulazione interrotta.")
    
  