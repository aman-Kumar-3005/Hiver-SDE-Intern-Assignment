from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data import load_examples
from .engine import SupportAgent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an auditable support-agent prediction")
    parser.add_argument("--message", required=True)
    parser.add_argument("--data", default="data/sample_conversations.jsonl")
    args = parser.parse_args()
    result = SupportAgent(load_examples(args.data)).predict(args.message)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()