import random

def eval_quality(normalized_snapshot):
    # Simulazione di una valutazione della qualità del segnale
    n_channels = 8
    quality = [random.randint(60, 100) for _ in range(n_channels)]  # Simulazione qualità canali
    return quality