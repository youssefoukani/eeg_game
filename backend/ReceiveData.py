"""
Programma per leggere un flusso EEG da LSL con un overlap del 50%
tra snapshot consecutivi, basato sul numero di campioni.
"""

from pylsl import StreamInlet, resolve_byprop, StreamInfo, StreamOutlet
from DataBuffer import EEGDataBuffer
from PreProcessor import pre_process
from ModelManager import predict
from osc_sim import send_prediction

SRATE = 250
CHANNELS = 8

from pylsl import StreamInlet, resolve_byprop, StreamInfo, StreamOutlet

def setup_outlets():
    """Crea e ritorna gli stream LSL attivi."""
    info_raw = StreamInfo('Unicorn_Raw', 'EEG', CHANNELS, SRATE, 'float32', 'raw_001')
    info_proc = StreamInfo('Unicorn_Filtered', 'EEG', CHANNELS, SRATE, 'float32', 'proc_001')
    info_pred = StreamInfo('Predictions', 'Markers', 1, 0, 'string', 'pred_001')
    
    # QUI stava l'errore: devi creare l'Outlet passando l'info
    return StreamOutlet(info_raw), StreamOutlet(info_proc), StreamOutlet(info_pred)


def main():
    # 1. Configurazione
    WINDOW_SIZE = 250
    SNAP_SAMPLE_FREQ = 250  # Ogni quanti campioni viene creato un nuovo snapshot
    
    # 2. Inizializzazione stream LSL
    print("Ricerca di un flusso EEG sulla rete locale...")
    streams = resolve_byprop("type", "EEG")
    
    if not streams:
        print("Nessuno stream EEG trovato. Assicurati che LSL sia attivo.")
        return

    inlet = StreamInlet(streams[0])
    eeg_buffer = EEGDataBuffer(window_size=WINDOW_SIZE)
    outlet_raw, outlet_proc, outlet_pred = setup_outlets()
    # Contatori
    sample_counter = 0
    samples_since_last_snapshot = 0
    
    print(f"Stream trovato. Buffer: {WINDOW_SIZE} campioni, Overlap: {SNAP_SAMPLE_FREQ } campioni.")
    print("Inizio acquisizione...")

    try:
        while True:
            # Recupero singolo campione
            sample, timestamp = inlet.pull_sample()

            outlet_raw.push_sample(sample)
            
            # Aggiornamento buffer e contatori
            eeg_buffer.add_sample(sample)
            sample_counter += 1
            samples_since_last_snapshot += 1

            # 3. Logica di estrazione basata sull'overlap
            # Aspettiamo di aver riempito il buffer la prima volta E 
            # di aver accumulato almeno 125 nuovi campioni.
            if eeg_buffer.is_ready() and samples_since_last_snapshot >= SNAP_SAMPLE_FREQ:
                
                snapshot = eeg_buffer.get_snapshot()
                
                # Resettiamo il contatore dei campioni, NON il buffer intero
                # (il buffer mantiene i 125 campioni precedenti necessari per l'overlap)
                samples_since_last_snapshot = 0
                
                # Output di verifica
                # print("-" * 30)
                # print(f"Snapshot estratto a campione n. {sample_counter}")
                # print(f"Shape snapshot: {snapshot.shape}")
                # print(snapshot) 
                normalized_snapshot = pre_process(snapshot)
                
                print(normalized_snapshot)

                for sample_filtered in normalized_snapshot:
                    outlet_proc.push_sample(sample_filtered)  

                prediction = predict(normalized_snapshot)
                outlet_pred.push_sample([str(prediction)])

                print(f"Predizione: {prediction}")
                send_prediction(prediction)

    except KeyboardInterrupt:
        print("\nAcquisizione interrotta dall'utente.")

if __name__ == "__main__":
    main()