"""Single bidirectional RS-232 serial port (REQ-SW-06, Decision 02).

Replaces the incorrect dual-port architecture. Most retail scales
(CAS ER-Plus, LP, AP, etc.) have ONE optional RS-232 port.

Integrity guarantees on a single port:
  1. Allowlist: only pre-approved commands are sent (Decision 03)
  2. State machine: config changes blocked during transactions (Decision 06)
  3. Audit log: every TX/RX is logged with hash chain (Decision 04)
  4. Secure Boot: software cannot be modified in the field (Decision 07)
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


class SerialPort:
    """Bidirectional RS-232 port — read and write on a single device."""

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: int = 1,
        timeout: float = 0.2,
        on_frame: Optional[FrameCallback] = None,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._timeout = timeout
        self.on_frame = on_frame
        self._serial: Optional[object] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._running = False
        self._buffer = bytearray()
        self._write_lock = threading.Lock()

    @property
    def is_open(self) -> bool:
        return self._serial is not None

    def open(self) -> None:
        import serial  # type: ignore[import-untyped]

        parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
        self._serial = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            bytesize=self._bytesize,
            parity=parity_map.get(self._parity, serial.PARITY_NONE),
            stopbits=self._stopbits,
            timeout=self._timeout,
        )
        logger.info(
            "Serial port opened: %s @ %d %d%s%d",
            self._port, self._baudrate, self._bytesize, self._parity, self._stopbits,
        )

    def start_reader(self) -> None:
        if self._reader_thread is not None:
            return
        self._running = True
        self._reader_thread = threading.Thread(
            target=self._read_loop, daemon=True, name="serial-reader",
        )
        self._reader_thread.start()

    def write(self, frame: bytes) -> None:
        if self._serial is None:
            raise RuntimeError("Serial port not opened")
        with self._write_lock:
            self._serial.write(frame)  # type: ignore[union-attr]
            self._serial.flush()  # type: ignore[union-attr]
        logger.debug("TX [%d bytes]: %s", len(frame), frame.hex())

    def close(self) -> None:
        self._running = False
        if self._reader_thread is not None:
            self._reader_thread.join(timeout=2.0)
            self._reader_thread = None
        if self._serial:
            self._serial.close()  # type: ignore[union-attr]
            self._serial = None

    def _read_loop(self) -> None:
        while self._running:
            if self._serial is None:
                time.sleep(0.5)
                continue
            try:
                chunk = self._serial.read(512)  # type: ignore[union-attr]
            except Exception:
                logger.exception("Serial read error")
                time.sleep(1.0)
                continue
            if chunk:
                self._buffer.extend(chunk)
                self._extract_frames()
            else:
                time.sleep(0.05)

    def _extract_frames(self) -> None:
        """Extract STX/ETX-delimited frames. Discard junk before STX."""
        while True:
            stx_pos = self._buffer.find(bytes([STX]))
            if stx_pos == -1:
                if self._buffer:
                    logger.debug("Discarding %d junk bytes", len(self._buffer))
                self._buffer.clear()
                return
            if stx_pos > 0:
                logger.debug("Discarding %d bytes before STX", stx_pos)
                del self._buffer[:stx_pos]
            etx_pos = self._buffer.find(bytes([ETX]))
            if etx_pos == -1:
                return
            frame = bytes(self._buffer[: etx_pos + 1])
            del self._buffer[: etx_pos + 1]
            logger.debug("RX frame [%d bytes]: %s", len(frame), frame.hex())
            if self.on_frame:
                try:
                    self.on_frame(frame)
                except Exception:
                    logger.exception("Frame callback error")


class MockSerialPort(SerialPort):
    """In-memory serial port for testing without hardware."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._port = "MOCK"
        self._sent: list[bytes] = []
        self._inject_queue: queue.Queue[bytes] = queue.Queue()

    def open(self) -> None:
        logger.info("Mock serial port opened")

    def write(self, frame: bytes) -> None:
        self._sent.append(frame)
        logger.debug("Mock TX: %s", frame.hex())

    def start_reader(self) -> None:
        self._running = True
        self._reader_thread = threading.Thread(
            target=self._mock_read_loop, daemon=True, name="mock-serial-reader",
        )
        self._reader_thread.start()

    def inject_frame(self, frame: bytes) -> None:
        self._inject_queue.put(frame)

    def close(self) -> None:
        self._running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=2.0)
            self._reader_thread = None

    def _mock_read_loop(self) -> None:
        while self._running:
            try:
                frame = self._inject_queue.get(timeout=0.2)
                if self.on_frame:
                    self.on_frame(frame)
            except queue.Empty:
                continue
