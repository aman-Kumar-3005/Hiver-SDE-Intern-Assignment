# AtlasCare report

## Problem framing

The target is an AppleSupport-style social-support queue built from the supplied Customer Support on Twitter export. Good means: identify the customer goal, avoid unsafe account claims, use language consistent with previous resolutions, and escalate high-impact or ambiguous cases. This version does not access accounts, issue refunds, diagnose a live network, or send public messages.

## Results and baselines

The reported run uses 500 inbound AppleSupport messages prepared from `twcs.csv`. The preparation script links each customer message to its referenced AppleSupport response and applies transparent bootstrap intent labels; these labels are not independent human annotations.

| System | Accuracy | Macro-F1 |
| --- | ---: | ---: |
| Majority baseline | 0.934 | 0.121 |
| Keyword baseline | 0.934 | 0.121 |
| AtlasCare | 0.934 | 0.121 |

AtlasCare additionally achieved an evidence hit rate of **1.000**, escalation precision of **0.970**, escalation recall of **1.000**, and a deterministic reply-rubric proxy of **1.000 grounded** and **1.000 no-account-claims**. The observed escalation rate was **1.000**. These figures come from `artifacts/evaluation.json`; they are a reproducibility smoke test, not a claim of production quality.

## Failure analysis

1. **Label imbalance:** 93.4% of the bootstrap slice receives the majority label, so accuracy and macro-F1 expose different behavior. A stratified human-labelled set is required before comparing models.
2. **Short messages:** “help” has little lexical signal; collect conversation context or ask a clarification question.
3. **Overlapping intents:** billing, service, and device issues can share words; add pairwise examples and evaluate confusion by intent.
4. **Misspellings and social shorthand:** character n-grams or spelling normalization should complement token matching.
5. **Multi-intent messages and policy drift:** support posts may contain multiple requests and historical replies may become stale; use multi-label annotation and versioned policy retrieval.

## What is misleading about my headline number?

The headline accuracy of **0.934** is misleading because the 500-row run uses deterministic bootstrap labels and is evaluated with the same prepared slice used for retrieval. The majority baseline gets exactly the same accuracy, while macro-F1 is only **0.121**, showing that accuracy is dominated by class imbalance. The **1.000** grounded proxy and **1.000** escalation recall also do not establish an LLM judge or production safety: every example was escalated, and the proxy only checks simple deterministic conditions. A trustworthy claim requires an independently held-out, temporally separated, human-labelled set, annotator agreement, confidence intervals, and cost-weighted errors.

## One more week

Build a leakage-checked temporal split from the Kaggle export, add two independent annotators, calibrate confidence, test character n-grams, and run a blinded human review of 100 replies. Then compare an API model and this offline baseline under the same evidence constraints.

## Decision log

* Chose AppleSupport because it is present as a clear brand author in the supplied TWCS export.
* Kept eight intents to balance coverage and label reliability.
* Made outage, account, cancellation, and unknown cases human-routed.
* Used retrieval evidence instead of free-form invented answers.
* Never include account-specific claims in templates.
* Added an unknown class rather than forcing every message into a known intent.
* Used macro-F1 because class imbalance is expected.
* Reported escalation precision and recall separately from intent metrics.
* Kept the Kaggle adapter separate from the agent and disclosed its bootstrap labels.
* Limited the raw-data preparation to 500 rows for fast, reproducible local runs.
* Joined inbound customer tweets to the referenced outbound brand response.
* Added a judge rubric but kept its agreement requirement explicit.
* Chose standard-library runtime dependencies for a sub-15-minute reproduction.

## Sources

* Customer Support on Twitter, thoughtvector, Kaggle: https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter
* Hiver SDE Intern take-home prompt supplied with this repository.