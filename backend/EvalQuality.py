import numpy as np

def eval_quality(normalized_snapshot):
    """

    snapshot: matrice (250, 8)

    ritorna: lista di 8 valori normalizzati tra 50 e 100

    """

    # Media per ogni canale (8 valori)

    channel_means = np.mean(normalized_snapshot, axis=0)

    min_val = np.min(channel_means)

    max_val = np.max(channel_means)

    # Caso limite: tutti i canali uguali

    if max_val == min_val:

        return [100] * len(channel_means)

    quality = 50 + (channel_means - min_val) * 50 / (max_val - min_val)

    return quality.astype(int).tolist()