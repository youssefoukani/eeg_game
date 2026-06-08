import threading
import numpy as np
from collections import deque

class EEGDataBuffer:
    def __init__(self, window_size=250, num_channels=8):
        self.window_size = window_size
        self.num_channels = num_channels
        # deque è la struttura perfetta: circolare per design
        self.buffer = deque(maxlen=window_size)
        self.lock = threading.Lock()

    def add_sample(self, sample):
        """Aggiunge un campione (lista di 8 valori) al buffer."""
        with self.lock:
            self.buffer.append(sample)

    def get_snapshot(self):
        """Restituisce una copia del buffer come matrice (window_size x 8)."""
        with self.lock:
            # Verifica che il buffer sia pieno
            if len(self.buffer) < self.window_size:
                return None
            
            # Converte in array numpy per il Machine Learning
            return np.array(list(self.buffer))

    def is_ready(self):
            """Controlla se il buffer è pieno e pronto per la classificazione."""
            with self.lock:
                return len(self.buffer) == self.window_size