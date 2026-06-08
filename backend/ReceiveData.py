"""Example program to show how to read a multi-channel time series from LSL."""

from pylsl import StreamInlet, resolve_byprop
from DataBuffer import EEGDataBuffer
import time

def main():
    # first resolve an EEG stream on the lab network
    print("looking for an EEG stream...")
    streams = resolve_byprop("type", "EEG")

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])
    eeg_buffer = EEGDataBuffer(window_size=250)

    last_prediction = time.time()

    while True:

        sample, timestamp = inlet.pull_sample()

        eeg_buffer.add_sample(sample)

        if not eeg_buffer.is_ready():
            continue

        if time.time() - last_prediction < 0.2:
            continue
        last_prediction = time.time()

        snapshot = eeg_buffer.get_snapshot()
        print(f"Snapshot shape: {snapshot.shape}", time.time() - last_prediction)
        # prediction = model.predict(snapshot)


if __name__ == "__main__":
    main()