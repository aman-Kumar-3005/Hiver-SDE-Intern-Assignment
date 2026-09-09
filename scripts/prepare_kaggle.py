from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


INTENT_TERMS = {
    "billing_payment": {"charge", "charged", "bill", "billing", "payment", "pay", "refund"},
    "plan_change": {"plan", "upgrade", "downgrade", "data", "add-on", "addon"},
    "sim_activation": {"sim", "activate", "activation", "esim"},
    "service_outage": {"signal", "service", "network", "outage", "data", "call", "calls"},
    "account_access": {"login", "log", "account", "password", "verify", "verification"},
    "cancellation": {"cancel", "cancellation", "leave", "leaving", "complaint"},
    "delivery_tracking": {"delivery", "deliver", "shipping", "shipped", "order", "track"},
}


def infer_intent(text: str) -> str:
    words = set(text.lower().replace("/", " ").split())
    scores = {intent: len(words & terms) for intent, terms in INTENT_TERMS.items()}
    best_intent, best_score = max(scores.items(), key=lambda item: item[1])
    return best_intent if best_score else "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter a Kaggle Twitter-support export into an agent input file")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--brand", default="AppleSupport")
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()
    output = Path(args.output)
    rows_by_id: dict[str, dict[str, str]] = {}
    with Path(args.input).open(encoding="utf-8", errors="replace", newline="") as source:
        for row in csv.DictReader(source):
            rows_by_id[row.get("tweet_id", "")] = row

    kept = 0
    with Path(args.input).open(encoding="utf-8", errors="replace", newline="") as source, output.open("w", encoding="utf-8") as target:
        rows = csv.DictReader(source)
        for row in rows:
            text = (row.get("text") or row.get("tweet_text") or "").strip()
            author = row.get("author_id") or row.get("author") or ""
            if kept >= args.limit:
                break
            if not text or text.lower() in {"[deleted]", "deleted"} or (row.get("inbound") or "").lower() != "true":
                continue
            response = rows_by_id.get(row.get("response_tweet_id", ""), {})
            response_text = (response.get("text") or "").strip()
            if (response.get("author_id") or "").lower() != args.brand.lower() or not response_text:
                continue
            intent = infer_intent(text)
            target.write(json.dumps({"text": text, "intent": intent, "response": response_text, "risky": intent in {"service_outage", "account_access", "cancellation", "unknown"}}) + "\n")
            kept += 1
    print(f"Wrote {kept} inbound {args.brand} rows with linked responses to {output}.")


if __name__ == "__main__":
    main()