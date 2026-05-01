import json
from pathlib import Path

path = Path("outputs/result.json")

if not path.exists():
    raise SystemExit("FAIL: outputs/result.json missing")

data = json.loads(path.read_text(encoding="utf-8"))

required = [
    "tool",
    "version",
    "observer_only",
    "thread_sha256",
    "fit",
    "recommendation",
    "scores",
    "reasons"
]

missing = [k for k in required if k not in data]

if missing:
    raise SystemExit(f"FAIL: missing fields {missing}")

if data["observer_only"] is not True:
    raise SystemExit("FAIL: observer_only must be true")

if data["fit"] not in ["PASS", "HOLD", "LOW"]:
    raise SystemExit("FAIL: invalid fit")

print("PASS: signal_enhancer output verified")