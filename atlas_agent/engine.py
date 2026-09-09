from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from .data import Example

TOKEN_RE = re.compile(r"[a-z0-9']+")
RISKY_INTENTS = {"service_outage", "account_access", "cancellation", "unknown"}


def tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(text.lower()))


@dataclass(frozen=True)
class Prediction:
    intent: str
    confidence: float
    action: str
    reason: str
    reply: str
    evidence: str
    evidence_score: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class SupportAgent:
    def __init__(self, examples: list[Example]):
        self.examples = examples
        self.labels = sorted({example.intent for example in examples})
        self.label_terms: dict[str, Counter[str]] = defaultdict(Counter)
        for example in examples:
            self.label_terms[example.intent].update(tokens(example.text))
        self.idf = self._idf()

    def _idf(self) -> dict[str, float]:
        documents = [tokens(example.text) for example in self.examples]
        count = Counter(term for document in documents for term in document)
        return {term: math.log((1 + len(documents)) / (1 + frequency)) + 1 for term, frequency in count.items()}

    def _score(self, query: set[str], intent: str) -> float:
        weights = self.label_terms[intent]
        overlap = sum(self.idf.get(term, 1.0) * (1 + math.log(count)) for term, count in weights.items() if term in query)
        return overlap / max(1.0, math.sqrt(sum(self.idf.get(term, 1.0) ** 2 for term in query)))

    def _classify(self, text: str) -> tuple[str, float]:
        query = tokens(text)
        scores = sorted(((self._score(query, intent), intent) for intent in self.labels), reverse=True)
        if not scores or scores[0][0] == 0:
            return "unknown", 0.0
        best, second = scores[0], scores[1] if len(scores) > 1 else (0.0, "")
        margin = max(0.0, best[0] - second[0]) / max(best[0], 1.0)
        confidence = min(0.99, 0.55 + 0.35 * min(best[0] / 4, 1) + 0.10 * margin)
        return best[1], confidence

    def _retrieve(self, text: str, intent: str) -> tuple[Example | None, float]:
        query = tokens(text)
        candidates = [example for example in self.examples if example.intent == intent]
        scored = []
        for example in candidates:
            example_tokens = tokens(example.text)
            score = len(query & example_tokens) / max(1, len(query | example_tokens))
            scored.append((score, example))
        return max(scored, default=(0.0, None), key=lambda pair: pair[0])[1], max(scored, default=(0.0, None), key=lambda pair: pair[0])[0]

    def predict(self, text: str) -> Prediction:
        intent, confidence = self._classify(text)
        evidence, evidence_score = self._retrieve(text, intent)
        if intent in RISKY_INTENTS:
            action = "escalate"
            reason = "High-impact issue or out-of-scope message; a human should verify account and customer context."
        elif confidence < 0.72 or evidence_score < 0.08:
            action = "escalate"
            reason = "The model lacks enough signal or a close historical example to answer safely."
        else:
            action = "auto_handle"
            reason = "Intent and historical evidence pass the confidence and similarity thresholds."
        reply = self._reply(intent, action)
        return Prediction(intent, round(confidence, 3), action, reason, reply, evidence.text if evidence else "", round(evidence_score, 3))

    @staticmethod
    def _reply(intent: str, action: str) -> str:
        opening = {
            "billing_payment": "Sorry for the billing confusion.",
            "plan_change": "We can help with your plan options.",
            "sim_activation": "Sorry you are having trouble activating your SIM.",
            "service_outage": "Sorry your service is not working.",
            "account_access": "We can help you regain access securely.",
            "cancellation": "We are sorry to hear you may want to leave.",
            "delivery_tracking": "We can help check the delivery status.",
            "unknown": "Thanks for getting in touch.",
        }.get(intent, "Thanks for getting in touch.")
        if action == "escalate":
            return f"{opening} Please send us a private message with the relevant details so a support specialist can check this securely."
        return f"{opening} Please send us a private message with your mobile number so we can check this securely and help with the next step."