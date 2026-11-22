#!/usr/bin/env python3
"""
Exercise: in protobuf, field NUMBERS are the contract — not names, not file order.

1. Encode an Event with the sender schema.
2. Decode the *same bytes* with three different receiver schemas:
   - renamed fields, same numbers     → still correct
   - same names, swapped numbers      → values land in the wrong fields
   - fields listed in a new order, same numbers → still correct

Setup (from this directory): see README.md
  python 03_numbers_not_names.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXERCISE = ROOT / "exercise"
GEN = EXERCISE / "generated"


def generate_protos() -> None:
    """Compile the four exercise .proto files into exercise/generated/."""
    GEN.mkdir(parents=True, exist_ok=True)
    (GEN / "__init__.py").touch()
    protos = [
        "sender.proto",
        "receiver_renamed.proto",
        "receiver_swapped_numbers.proto",
        "receiver_reordered.proto",
    ]
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{EXERCISE}",
        f"--python_out={GEN}",
        *[str(EXERCISE / p) for p in protos],
    ]
    subprocess.check_call(cmd)


def as_dict(msg) -> dict:
    return {field.name: value for field, value in msg.ListFields()}


def main() -> None:
    generate_protos()
    sys.path.insert(0, str(GEN))

    import sender_pb2  # noqa: E402
    import receiver_renamed_pb2  # noqa: E402
    import receiver_swapped_numbers_pb2  # noqa: E402
    import receiver_reordered_pb2  # noqa: E402

    # --- sender encodes once ---
    sent = sender_pb2.Event(
        event_id=1,
        name="Git workshop",
        capacity=12,
        available_seats=9,
    )
    wire = sent.SerializeToString()

    print("Sender encoded:")
    print(f"  {as_dict(sent)}")
    print(f"  wire hex: {wire.hex(' ')}")
    print()

    # --- 1. renamed names, same numbers ---
    renamed = receiver_renamed_pb2.Event()
    renamed.ParseFromString(wire)
    print("1) Receiver RENAMED (name → title, numbers unchanged)")
    print(f"   decoded: {as_dict(renamed)}")
    print("   → title still holds 'Git workshop'. Names changed; numbers did not.")
    print()

    # --- 2. same names, swapped numbers (same types, so bytes still parse) ---
    swapped = receiver_swapped_numbers_pb2.Event()
    swapped.ParseFromString(wire)
    print("2) Receiver SWAPPED NUMBERS (capacity=4, available_seats=3)")
    print(f"   decoded: {as_dict(swapped)}")
    print("   → capacity and available_seats are swapped (12 ↔ 9). Numbers changed.")
    print()

    # --- 3. reordered lines in the .proto, same numbers ---
    reordered = receiver_reordered_pb2.Event()
    reordered.ParseFromString(wire)
    print("3) Receiver REORDERED (fields listed differently in the .proto, same numbers)")
    print(f"   decoded: {as_dict(reordered)}")
    print("   → still correct. Declaration order in the file does not matter.")
    print()

    print("Takeaway: agree on field NUMBERS. Names and line order are local labels.")


if __name__ == "__main__":
    main()
