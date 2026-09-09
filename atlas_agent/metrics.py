from __future__ import annotations

from collections import Counter


def accuracy(actual: list[str], predicted: list[str]) -> float:
    return sum(a == p for a, p in zip(actual, predicted)) / max(1, len(actual))


def macro_f1(actual: list[str], predicted: list[str]) -> float:
    labels = sorted(set(actual) | set(predicted))
    values = []
    for label in labels:
        tp = sum(a == label and p == label for a, p in zip(actual, predicted))
        fp = sum(a != label and p == label for a, p in zip(actual, predicted))
        fn = sum(a == label and p != label for a, p in zip(actual, predicted))
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        values.append(2 * precision * recall / max(1e-12, precision + recall))
    return sum(values) / max(1, len(values))


def routing_metrics(actual_risky: list[bool], predicted_actions: list[str]) -> dict[str, float]:
    predicted_risky = [action == "escalate" for action in predicted_actions]
    tp = sum(a and p for a, p in zip(actual_risky, predicted_risky))
    fp = sum(not a and p for a, p in zip(actual_risky, predicted_risky))
    fn = sum(a and not p for a, p in zip(actual_risky, predicted_risky))
    return {"escalation_precision": tp / max(1, tp + fp), "escalation_recall": tp / max(1, tp + fn), "escalation_rate": sum(predicted_risky) / max(1, len(predicted_risky))}


def majority_label(labels: list[str]) -> str:
    return Counter(labels).most_common(1)[0][0]