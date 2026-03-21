#!/usr/bin/env python3
"""
Serial capture utility for CAS ER-Plus.

Run this on the Pi with the scale connected to record raw frames.
Use the output to finalize the CAS adapter protocol.

Usage:
    python capture_serial.py --port /dev/ttyUSB1 --baud 9600 --output capture.log
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture RS-232 frames from CAS ER-Plus")
    parser.add_argument("--port", default="/dev/ttyUSB1", help="Serial port")
    parser.add_argument("--baud", type=int, default=9600, help="Baud rate")
    parser.add_argument("--output", default="capture.log", help="Output file")
    args = parser.parse_args()

    try:
        import serial  # type: ignore[import-untyped]
    except ImportError:
        print("Install pyserial: pip install pyserial", file=sys.stderr)
        sys.exit(1)

    ser = serial.Serial(port=args.port, baudrate=args.baud, timeout=0.5)
    out = Path(args.output).open("a", encoding="utf-8")

    print(f"Listening on {args.port} @ {args.baud} baud...")
    print(f"Writing to {args.output}")
    print("Press Ctrl+C to stop.\n")

    buf = bytearray()
    try:
        while True:
            chunk = ser.read(512)
            if chunk:
                buf.extend(chunk)
                while b"\x03" in buf:
                    end = buf.index(b"\x03")
                    frame = bytes(buf[: end + 1])
                    del buf[: end + 1]

                    ts = datetime.now(timezone.utc).isoformat()
                    hex_repr = frame.hex()
                    ascii_repr = frame.decode("ascii", errors="replace")
                    line = f"{ts} | HEX: {hex_repr} | ASCII: {ascii_repr}"
                    print(line)
                    out.write(line + "\n")
                    out.flush()
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()
        out.close()


if __name__ == "__main__":
    main()
