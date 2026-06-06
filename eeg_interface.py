# ─── eeg_interface.py ─────────────────────────────────────────────────────────
# Receives motor-imagery predictions via OSC UDP from an external BCI backend.
#
# Integration notes:
#   - The game listens on (ip, port) for OSC messages at address /bci/prediction.
#   - The BCI backend (Python script, MATLAB, BrainFlow, etc.) sends:
#       /bci/prediction  "LEFT"  |  "RIGHT"  |  "NONE"
#   - The server runs in a daemon thread; it is automatically killed when the
#     main process exits.
#
# Timing contract:
#   The game gives OBSTACLE_TRAVEL_TIME = 2.8 s from obstacle spawn to
#   collision line.  The backend must deliver a prediction within that window.

import threading
from typing import Optional

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class EEGInterface:
    """OSC UDP receiver for real-time BCI predictions."""

    # Unicorn Hybrid Black channel layout (8-ch MI subset)
    CHANNELS = ["Fz", "C3", "Cz", "C4", "Pz", "PO7", "Oz", "PO8"]

    def __init__(self, ip: str = "127.0.0.1", port: int = 5005):
        self.ip   = ip
        self.port = port

        self._connected                  = False
        self._latest_prediction: Optional[str] = None
        self._lock                       = threading.Lock()
        self._server: Optional[BlockingOSCUDPServer] = None
        self._server_thread: Optional[threading.Thread] = None

    # ── public API ────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """Start the OSC server in a background daemon thread."""
        if self._connected:
            return True
        try:
            dispatcher = Dispatcher()
            dispatcher.map("/bci/prediction", self._handle_prediction)

            self._server = BlockingOSCUDPServer((self.ip, self.port), dispatcher)
            self._server_thread = threading.Thread(
                target=self._server.serve_forever, daemon=True
            )
            self._server_thread.start()

            self._connected = True
            print(f"[EEG] OSC server listening on {self.ip}:{self.port}")
            return True

        except Exception as exc:
            print(f"[EEG] Could not start OSC server: {exc}")
            return False

    def get_prediction(self) -> Optional[str]:
        """Return the latest decoded command ("LEFT" | "RIGHT" | None).
        Called every frame by InputManager; must be non-blocking."""
        with self._lock:
            return self._latest_prediction

    # def get_signal_quality(self) -> dict[str, str]:
    #     """Return per-channel quality map used by SignalQualityCheck.
    #     Returns GOOD for all channels while the OSC server is running."""
    #     status = "GOOD" if self._connected else "N/A"
    #     return {ch: status for ch in self.CHANNELS}

    
    # ── internal ──────────────────────────────────────────────────────────────

    def _handle_prediction(self, address: str, *args):
        """OSC message handler – runs on the server thread."""
        if args and args[0] in ("LEFT", "RIGHT", "NONE"):
            with self._lock:
                self._latest_prediction = args[0] if args[0] != "NONE" else None