# Encoding demo: JSON vs protobuf on the wire

Tiny Python examples for seeing what actually crosses the network when the
same `Event` is encoded as **JSON** versus **protobuf**.

No HTTP. No gRPC. No RPC. Just encode → bytes → socket → decode.

## Requirements

- Python 3.9 or newer

## Setup

From this directory (`encoding/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt   # note the -r (read from file)

mkdir -p generated
python -m grpc_tools.protoc \
  -I . --python_out=generated event.proto
```

The `-r` flag matters. `pip install requirements.txt` (without `-r`) looks for a
PyPI package named `requirements.txt` and fails with
`No matching distribution found for requirements.txt`.

Re-run the `protoc` step whenever you change `event.proto`.

## Run

With the venv activated:

```bash
python 01_look_at_bytes.py
python 02_transfer.py
python 03_numbers_not_names.py
```

## What each demo does

### `01_look_at_bytes.py` — encode only (no network)

Builds the same Event twice: once as a Python dict, once as a protobuf message.
Encodes each to bytes (`json.dumps` vs `SerializeToString`) and prints size,
text, and hex side by side. Use this to see that JSON is readable text with
field names, while protobuf is compact binary.

### `02_transfer.py` — encode, send over TCP, decode

Same Event and encodings, but over a plain TCP socket on localhost. A small
receiver listens; a sender connects and writes the bytes. The receiver reads
them and decodes back to an Event. Runs once for JSON and once for protobuf.
A 4-byte length prefix frames each message so the receiver knows where it ends.

### `03_numbers_not_names.py` — field numbers are the contract

Encodes one Event with a sender schema, then decodes those **same bytes** with
three different receiver schemas (see `exercise/`):

1. **Renamed** (`name` → `title`, number still `= 2`) → still correct  
2. **Swapped numbers** (`capacity` ↔ `available_seats` numbers) → values land in the wrong fields  

3. **Reordered** (fields listed differently in the file, same numbers) → still correct  

Takeaway: agree on field **numbers**. Names and line order in the `.proto` are
local labels. Details: `exercise/README.md`.

## Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python packages (`protobuf`, `grpcio-tools`) |
| `event.proto` | Schema for one message (`Event`). No `service`, no `rpc`. |
| `generated/` | Output of `protoc` (gitignored; do not edit by hand). |
| `01_look_at_bytes.py` | Compare JSON vs protobuf bytes locally (no network). |
| `02_transfer.py` | Send each encoding over a plain TCP socket and decode on the other end. |
| `03_numbers_not_names.py` | Show that field numbers matter; names and file order do not. |
| `exercise/` | Sender + three receiver `.proto` files for that exercise. |

## What to notice

1. **JSON** is text. Field names (`"event_id"`, `"name"`, …) are in every message.
   You can read the payload in the terminal.

2. **Protobuf** is binary. Field *numbers* from `event.proto` travel instead of
   names. The payload is smaller and not human-readable without the schema.

3. Both sides must agree on the format. For protobuf that agreement is the
   `.proto` file (and the generated code). For JSON it is usually an informal
   convention about keys and types.

4. On a raw TCP stream you still need framing (here: a 4-byte length prefix)
   so the receiver knows where one message ends. That is separate from JSON vs
   protobuf.

## The message

```proto
message Event {
  int64  event_id        = 1;
  string name            = 2;
  int32  capacity        = 3;
  int32  available_seats = 4;
}
```
