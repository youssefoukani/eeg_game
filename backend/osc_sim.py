import time
import random
from pythonosc.udp_client import SimpleUDPClient

def run_mock_backend():
    # IP locale (lo stesso computer) e porta concordata
    ip = "127.0.0.1"
    port = 5005
    
    # Inizializziamo il client OSC che invia i pacchetti
    client = SimpleUDPClient(ip, port)
    print(f"[MOCK BACKEND] Connesso. Invio predizioni random su {ip}:{port}...")
    print("Premi Ctrl+C per interrompere.")

    comandi_disponibili = ["LEFT", "RIGHT", "NONE"]
    
    try:
        while True:
            # Sceglie un comando a caso
            cmd = random.choice(comandi_disponibili)
            
            # Inviamo il comando all'indirizzo specifico "/bci/prediction"
            # Se è "NONE", inviamo una stringa vuota o non inviamo nulla, 
            # simulando il comportamento del tuo classificatore reale.
            
            client.send_message("/bci/prediction", cmd)
            print(f" -> Inviata predizione: {cmd}")
            
                
            # Aspetta 2s
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[MOCK BACKEND] Simulazione interrotta.")

if __name__ == "__main__":
    run_mock_backend()