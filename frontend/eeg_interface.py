# ─── eeg_interface.py ─────────────────────────────────────────────────────────
# OSC UDP receiver for real-time BCI predictions.
#
# The BCI backend sends to (ip, port):
#   /bci/prediction  "LEFT" | "RIGHT" | "NONE"
#
# The server runs in a daemon thread and is killed automatically on exit.

import threading
from typing import Optional

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class EEGInterface:

    CHANNELS = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "Oz", "PO8"]

    def __init__(self, ip: str = "127.0.0.1", port: int = 5005):
        self.ip   = ip
        self.port = port
        self._connected  = False
        self._prediction: Optional[str] = None
        self._lock       = threading.Lock()

        self._channel_quality = [0] * 8  # Placeholder for channel quality metrics

    def connect(self) -> bool:
        if self._connected:
            return True
        try:
            dispatcher = Dispatcher()
            dispatcher.map("/bci/prediction", self._handle_prediction)

            dispatcher.map("/bci/quality",self._handle_quality) #dispatcher per ricevere la qualità dei canali

            server = BlockingOSCUDPServer((self.ip, self.port), dispatcher)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self._connected = True
            print(f"[EEG] Listening on {self.ip}:{self.port}")
            return True
        except Exception as exc:
            print(f"[EEG] Could not start OSC server: {exc}")
            return False

    def get_prediction(self) -> Optional[str]:
        """Non-blocking read of the latest decoded command."""
        with self._lock:
            return self._prediction

    def _handle_prediction(self, address: str, *args):
        if args and args[0] in ("LEFT", "RIGHT", "NONE"):
            with self._lock:
                self._prediction = args[0] if args[0] != "NONE" else None

    def _handle_quality(self, address, *args):
        with self._lock:
            self._channel_quality = list(args)
    
    def get_channel_quality(self):
        with self._lock:
            return self._channel_quality.copy()