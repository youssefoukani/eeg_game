import time
import random
from pythonosc.udp_client import SimpleUDPClient



def send_prediction(prediction):

    # IP locale (lo stesso computer) e porta concordata
    ip = "127.0.0.1"
    port = 5005

    client = SimpleUDPClient(ip, port)

    print(f"[MOCK BACKEND] Connesso. Invio predizioni random su {ip}:{port}...")
    print("Premi Ctrl+C per interrompere.")
    try:
        
            
        # Inviamo il comando all'indirizzo specifico "/bci/prediction"
        # Se è "NONE", inviamo una stringa vuota o non inviamo nulla, 
        # simulando il comportamento del tuo classificatore reale.
        
        client.send_message("/bci/prediction", prediction)
        print(f" -> Inviata predizione: {prediction}")
        
            
            
    except KeyboardInterrupt:
        print("\n[MOCK BACKEND] Simulazione interrotta.")

