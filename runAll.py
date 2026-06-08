import subprocess
import sys
import time

def main():
    # Elenco degli script da avviare
    scripts = ["backend/SendData.py", "backend/ReceiveData.py", "frontend/main.py"]
    processes = []

    print(f"Avvio di {len(scripts)} moduli...")

    try:
        # Avvia ogni script come un sottoprocesso separato
        for script in scripts:
            p = subprocess.Popen([sys.executable, script])
            processes.append(p)
            print(f"Avviato {script} (PID: {p.pid})")
            # Breve pausa per evitare conflitti nell'inizializzazione LSL
            time.sleep(1)

        print("\nTutti i moduli sono in esecuzione. Premi Ctrl+C per fermarli.")
        
        # Mantiene il launcher in vita finché non premi Ctrl+C
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterruzione richiesta. Chiusura dei processi in corso...")
    finally:
        # Chiude tutti i processi aperti
        for p in processes:
            p.terminate()
        print("Tutti i moduli sono stati terminati.")

if __name__ == "__main__":
    main()