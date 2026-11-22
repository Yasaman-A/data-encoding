#!/usr/bin/env python3
"""
What does the same Event look like as JSON vs as protobuf bytes?

No network. No RPC. Just encode and print.

Setup (from this directory): see README.md
  python 01_look_at_bytes.py
"""

import json
import sys
from pathlib import Path

# Make the generated protobuf module importable.
sys.path.insert(0, str(Path(__file__).parent / "generated"))
import event_pb2  # noqa: E402


def same_event_as_dict():
    return {
        "event_id": 1,
        "name": "Git workshop",
        "capacity": 12,
        "available_seats": 9,
    }


def same_event_as_protobuf():
    event = event_pb2.Event()
    event.event_id = 1
    event.name = "Git workshop"
    event.capacity = 12
    event.available_seats = 9
    return event


def show(label, raw: bytes):
    print(f"--- {label} ---")
    print(f"size:  {len(raw)} bytes")
    print(f"text:  {raw!r}")          # Python's view of the bytes
    print(f"hex:   {raw.hex(' ')}")   # byte-by-byte hex
    print()


def main():
    data = same_event_as_dict()

    # JSON: field names travel with every message (human-readable text).
    json_bytes = json.dumps(data).encode("utf-8")

    # Protobuf: field numbers from event.proto; values only (binary).
    proto_bytes = same_event_as_protobuf().SerializeToString()

    show("JSON", json_bytes)
    show("protobuf", proto_bytes)

    print(
        f"protobuf is {len(json_bytes) - len(proto_bytes)} bytes smaller "
        f"for this message ({len(proto_bytes)} vs {len(json_bytes)})."
    )


if __name__ == "__main__":
    main()
