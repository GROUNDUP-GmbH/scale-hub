"""
GroundUp Scale Hub – Dual-Port RS-232 Serial Layer

Manages two physical serial ports for the CAS ER-Plus RS232 x2 module:
  - Port A (Full Duplex): write PLU commands, read acknowledgements
  - Port B (TX only from scale): read completed sale frames

Uses pyserial. Falls back to a mock for development without hardware.
"""
from __future__ import annotations

import logging
import queue
import threading
import time
from typing import Callable, Optional, Protocol

logger = logging.getLogger(__name__)

STX = 0x02
ETX = 0x03


class FrameCallback(Protocol):
    def __call__(self, raw: bytes) -> None: ...


# -- Writer (Port A) ---------------------------------------------------------


class SerialWriter:
    """Sends commands to the scale via Port A (Full Duplex)."""

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        timeout: float = 0.5,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._serial: Optional[object] = None

    def open(self) -> None:
        import serial  # type: ignore[import-untyped]

        self._serial = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        )
        logger.info("Port A opened: %s @ %d baud", self._port, self._baudrate)

    def write(self, frame: bytes) -> None:
        if self._serial is None:
            raise RuntimeError("Port A not opened")
        self._serial.write(frame)  # type: ignore[union-attr]
        self._serial.flush()  # type: ignore[union-attr]
        logger.debug("Port A TX: %s", frame.hex())

    def close(self) -> None:
        if self._serial:
            self._serial.close()  # type: ignore[union-attr]
            self._serial = None


# -- Reader (Port B) ---------------------------------------------------------


class SerialReader(threading.Thread):
    """
    Continuously reads completed sale frames from Port B (TX only).
    Frames are delimited by STX/ETX bytes.
    """

    def __init__(
        self,
        port: str = "/dev/ttyUSB1",
        baudrate: int = 9600,
        timeout: float = 0.2,
        on_frame: Optional[FrameCallback] = None,
    ) -> None:
        super().__init__(daemon=True, name="scale-reader-portB")
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self.on_frame = on_frame
        self._running = False
        self._serial: Optional[object] = None
        self._buffer = bytearray()

    def open(self) -> None:
        import serial  # type: ignore[import-untyped]

        self._serial = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=self._timeout,
        )
        logger.info("Port B opened: %s @ %d baud", self._port, self._baudrate)

    def run(self) -> None:
        self._running = True
        while self._running:
            if self._serial is None:
                time.sleep(0.5)
                continue
            try:
                chunk = self._serial.read(512)  # type: ignore[union-attr]
            except Exception:
                logger.exception("Port B read error")
                time.sleep(1.0)
                continue

            if chunk:
                self._buffer.extend(chunk)
                self._extract_frames()
            else:
                time.sleep(0.05)

    def stop(self) -> None:
        self._running = False

    def close(self) -> None:
        self.stop()
        if self._serial:
            self._serial.close()  # type: ignore[union-attr]
            self._serial = None

    def _extract_frames(self) -> None:
        while True:
            stx_pos = self._buffer.find(bytes([STX]))
            if stx_pos == -1:
                self._buffer.clear()
                return
            etx_pos = self._buffer.find(bytes([ETX]), stx_pos)
            if etx_pos == -1:
                if stx_pos > 0:
                    del self._buffer[:stx_pos]
                return
            frame = bytes(self._buffer[stx_pos : etx_pos + 1])
            del self._buffer[: etx_pos + 1]
            logger.debug("Port B RX frame: %s", frame.hex())
            if self.on_frame:
                try:
                    self.on_frame(frame)
                except Exception:
                    logger.exception("Frame callback error")


# -- Mock layer for development without hardware ------------------------------


class MockSerialWriter(SerialWriter):
    """Logs writes instead of sending to a real port."""

    def __init__(self, **kwargs: object) -> None:
        self._port = "MOCK"
        self._baudrate = 9600
        self._timeout = 0.5
        self._serial = None
        self._sent: list[bytes] = []

    def open(self) -> None:
        logger.info("Mock Port A opened")

    def write(self, frame: bytes) -> None:
        self._sent.append(frame)
        logger.info("Mock Port A TX: %s", frame.hex())

    def close(self) -> None:
        pass


class MockSerialReader(SerialReader):
    """Allows injecting frames for testing."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._port = "MOCK"  # type: ignore[assignment]
        self._inject_queue: queue.Queue[bytes] = queue.Queue()

    def open(self) -> None:
        logger.info("Mock Port B opened")

    def inject_frame(self, frame: bytes) -> None:
        self._inject_queue.put(frame)

    def run(self) -> None:
        self._running = True
        while self._running:
            try:
                frame = self._inject_queue.get(timeout=0.2)
                if self.on_frame:
                    self.on_frame(frame)
            except queue.Empty:
                continue
