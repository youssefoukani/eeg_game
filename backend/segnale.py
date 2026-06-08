import pyxdf
import numpy as np
import mne
import matplotlib.pyplot as plt

# 1. Carica il file
streams, fileheader = pyxdf.load_xdf('/Users/cristiansaracino/Desktop/eeg_game/backend/prova.xdf')

for stream in streams:
    name = stream['info']['name'][0]
    data = np.array(stream['time_series']).T
    srate = float(stream['info']['nominal_srate'][0])
    
    print(f"---")
    print(f"Stream: {name}, Frequenza: {srate}")
    
    # Se lo stream non ha frequenza (srate=0), lo trattiamo come eventi
    if srate <= 0:
        print(f"Saltando la visualizzazione EEG per {name} perché è uno stream di eventi.")
        # Puoi stampare i valori se vuoi vedere le predizioni:
        print(f"Contenuto marcatori: {stream['time_series']}")
        continue 

    # Per gli stream EEG normali (Raw e Filtered)
    ch_names = [f'CH{i+1}' for i in range(data.shape[0])]
    info = mne.create_info(ch_names=ch_names, sfreq=srate, ch_types='eeg')
    raw = mne.io.RawArray(data, info)
    
    raw.plot(scalings='auto', title=f"Visualizzazione: {name}", block=False)

plt.show()