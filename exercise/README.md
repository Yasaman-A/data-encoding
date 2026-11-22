# Exercise: field numbers, not names

Protobuf puts **field numbers** on the wire (`= 1`, `= 2`, …). Field **names**
are only for humans and generated code. The order of lines in a `.proto` file
also does not matter, as long as the numbers stay the same.

## What you will do

The script `../03_numbers_not_names.py` encodes one Event with `sender.proto`,
then decodes those **same bytes** with three different receiver schemas:

| Receiver schema | What changed | Expected result |
|-----------------|--------------|-----------------|
| `receiver_renamed.proto` | `name` → `title`, number still `= 2` | Still correct (`title` = "Git workshop") |
| `receiver_swapped_numbers.proto` | `capacity` and `available_seats` swap numbers | Values land in the wrong fields (12 ↔ 9) |
| `receiver_reordered.proto` | Fields listed in a different order, same numbers | Still correct |

## Run

From the `encoding/` directory (venv activated, packages installed):

```bash
python 03_numbers_not_names.py
```

## Regenerate after editing `.proto` files

**Easiest:** run the script again. It recompiles every exercise `.proto` into
`exercise/generated/` on each run:

```bash
# from encoding/
python 03_numbers_not_names.py
```

**By hand** (only if you want the stubs without running the demo):

```bash
# from encoding/
mkdir -p exercise/generated
python -m grpc_tools.protoc \
  -I exercise \
  --python_out=exercise/generated \
  exercise/sender.proto \
  exercise/receiver_renamed.proto \
  exercise/receiver_swapped_numbers.proto \
  exercise/receiver_reordered.proto
```

Do not edit files under `exercise/generated/` by hand; change the `.proto`
files and regenerate.
## Try it yourself

1. Open `sender.proto` and `receiver_renamed.proto`. Confirm only the **name**
   of field 2 differs.
2. Open `receiver_swapped_numbers.proto`. Confirm the **numbers** for
   `capacity` and `available_seats` differ from the sender.
3. Run the script and match the printed results to the table above.
4. Optional: change a number in `receiver_renamed.proto`, re-run, and watch
   decode break even though the Python attribute names look fine.

