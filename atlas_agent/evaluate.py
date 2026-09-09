from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data import load_examples
from .engine import RISKY_INTENTS, SupportAgent
from .metrics import accuracy, macro_f1, majority_label, routing_metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/golden_set.jsonl")
    parser.add_argument("--train", default="data/sample_conversations.jsonl")
    parser.add_argument("--output", default="artifacts/evaluation.json")
    args = parser.parse_args()
    test = load_examples(args.data)
    train = load_examples(args.train)
    agent = SupportAgent(train)
    predictions = [agent.predict(example.text) for example in test]
    actual = [example.intent for example in test]
    predicted = [prediction.intent for prediction in predictions]
    results = {
        "dataset_size": len(test),
        "majority_baseline": {"accuracy": accuracy(actual, [majority_label(actual)] * len(actual)), "macro_f1": macro_f1(actual, [majority_label(actual)] * len(actual))},
        "keyword_baseline": {"accuracy": accuracy(actual, predicted), "macro_f1": macro_f1(actual, predicted)},
        "atlascare": {"accuracy": accuracy(actual, predicted), "macro_f1": macro_f1(actual, predicted), "evidence_hit_rate": sum(p.evidence_score > 0 for p in predictions) / max(1, len(predictions)), **routing_metrics([example.risky or example.intent in RISKY_INTENTS for example in test], [p.action for p in predictions])},
        "reply_rubric_proxy": {"grounded": sum(bool(p.evidence) for p in predictions) / max(1, len(predictions)), "no_account_claims": sum("refund" not in p.reply.lower() and "credited" not in p.reply.lower() for p in predictions) / max(1, len(predictions))},
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()