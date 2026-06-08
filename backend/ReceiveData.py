"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_byprop
from DataBuffer import EEGDataBuffer

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_byprop("type", "EEG")

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    eeg_buffer = EEGDataBuffer(window_size=250)

    while True:
        # get a new sample (you can also omit the timestamp part if you're not
        # interested in it)
        sample, timestamp = inlet.pull_sample()
        eeg_buffer.add_sample(sample)
        if eeg_buffer.is_ready():
            snapshot = eeg_buffer.get_snapshot()
            # Qui puoi inserire il codice per processare "snapshot" con il tuo classificatore
            # Ad esempio: prediction = model.predict(snapshot)
            # E poi inviare la predizione al frontend tramite OSC o altro metodo
            print("Buffer pronto per la classificazione. Ultimo campione ricevuto:", sample, len(eeg_buffer.buffer))
            


if __name__ == "__main__":
    main()