import json
import sys
from pathlib import Path
from .audit import audit_document


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 -m core.cli <input.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        result = audit_document(document)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
