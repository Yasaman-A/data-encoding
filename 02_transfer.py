#!/usr/bin/env python3
"""
Send the same Event over a plain TCP socket — once as JSON, once as protobuf.

No HTTP. No gRPC. No RPC framework.
Just: encode → write bytes on a socket → read bytes → decode.

Setup (from this directory): see README.md
  python 02_transfer.py
"""

import json
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "generated"))
import event_pb2  # noqa: E402

HOST = "127.0.0.1"
PORT = 9000

EVENT = {
    "event_id": 1,
    "name": "Git workshop",
    "capacity": 12,
    "available_seats": 9,
}


# ---- encode / decode (the only format-specific part) ----------------------


def encode_json(event: dict) -> bytes:
    return json.dumps(event).encode("utf-8")


def decode_json(raw: bytes) -> dict:
    return json.loads(raw.decode("utf-8"))


def encode_protobuf(event: dict) -> bytes:
    msg = event_pb2.Event(
        event_id=event["event_id"],
        name=event["name"],
        capacity=event["capacity"],
        available_seats=event["available_seats"],
    )
    return msg.SerializeToString()


def decode_protobuf(raw: bytes) -> dict:
    msg = event_pb2.Event()
    msg.ParseFromString(raw)
    return {
        "event_id": msg.event_id,
        "name": msg.name,
        "capacity": msg.capacity,
        "available_seats": msg.available_seats,
    }


# ---- length-prefixed framing (so the receiver knows when a message ends) --
# Both formats need *some* framing on a raw byte stream. We use: 4-byte length + body.


def send_message(conn: socket.socket, body: bytes) -> None:
    conn.sendall(len(body).to_bytes(4, "big") + body)


def recv_exact(conn: socket.socket, n: int) -> bytes:
    chunks = []
    while n > 0:
        chunk = conn.recv(n)
        if not chunk:
            raise ConnectionError("connection closed")
        chunks.append(chunk)
        n -= len(chunk)
    return b"".join(chunks)


def recv_message(conn: socket.socket) -> bytes:
    length = int.from_bytes(recv_exact(conn, 4), "big")
    return recv_exact(conn, length)


# ---- one round trip: receiver listens, sender connects --------------------


def run_once(label: str, encode, decode) -> None:
    ready = threading.Event()
    received = {}

    def receiver():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((HOST, PORT))
            server.listen(1)
            ready.set()
            conn, _ = server.accept()
            with conn:
                raw = recv_message(conn)
                print(f"[{label}] receiver got {len(raw)} bytes: {raw!r}")
                print(f"[{label}] hex: {raw.hex(' ')}")
                received["event"] = decode(raw)

    thread = threading.Thread(target=receiver, daemon=True)
    thread.start()
    ready.wait()

    body = encode(EVENT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        send_message(client, body)
        print(f"[{label}] sender wrote {len(body)} bytes: {body!r}")

    thread.join()
    print(f"[{label}] decoded event: {received['event']}")
    print()


def main():
    print("Same Event, two encodings, one plain TCP socket.\n")
    run_once("JSON", encode_json, decode_json)
    run_once("protobuf", encode_protobuf, decode_protobuf)


if __name__ == "__main__":
    main()
