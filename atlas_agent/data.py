from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Example:
    text: str
    intent: str
    response: str
    risky: bool = False


def load_examples(path: str | Path) -> list[Example]:
    source = Path(path)
    if source.suffix.lower() == ".csv":
        with source.open(encoding="utf-8", newline="") as handle:
            rows = csv.DictReader(handle)
            return [Example(row["text"], row["intent"], row.get("response", ""), row.get("risky", "false").lower() == "true") for row in rows]
    examples: list[Example] = []
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                examples.append(Example(row["text"], row["intent"], row.get("response", ""), bool(row.get("risky", False))))
    return examples