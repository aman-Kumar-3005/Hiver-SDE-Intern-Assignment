# AtlasCare Support Agent

An offline, reproducible customer-support agent for **AppleSupport** conversations from the supplied Customer Support on Twitter export. The project demonstrates the complete decision loop required by the Hiver assignment:

1. classify an incoming message into a small, auditable intent taxonomy;
2. retrieve a historically similar resolution and draft a grounded reply;
3. route low-confidence or high-risk cases to a human with a reason;
4. evaluate intent accuracy, retrieval quality, routing safety, and reply quality.

The implementation intentionally works without an API key. It is a deterministic baseline and fallback when an LLM is unavailable. The supplied `twcs.csv` is converted into a bounded normalized slice by the preparation command below.

## Quick start

Requires Python 3.10+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
py -m atlas_agent.cli --message "My iPhone cannot connect to Wi-Fi"
py -m atlas_agent.evaluate
```

Expected evaluation runs in seconds and writes [`artifacts/evaluation.json`](artifacts/evaluation.json). A sample CLI prediction is saved in [`artifacts/prediction.json`](artifacts/prediction.json). The agent consumes JSONL examples containing `text`, `intent`, `response`, and `risky` fields.

## Example

```text
Intent: service_outage
Action: escalate
Reason: High-impact service issue or low-confidence prediction; a human should verify account and network status.
Reply: Sorry your service is not working. Please send us a private message with your postcode and mobile number so we can check the network and your account securely.
Evidence: "network is down" (service_outage, 0.86)
```

The reply generator only uses resolution templates and retrieved evidence from the local training set. It never invents account-specific facts, refunds, dates, or links.

## Data and labels

The taxonomy is deliberately small:

| Intent | Meaning | Default route |
| --- | --- | --- |
| `billing_payment` | payment, charge, balance, or bill question | auto if confident |
| `plan_change` | upgrade, downgrade, add-on, or plan change | auto if confident |
| `sim_activation` | SIM/eSIM activation or replacement | auto if confident |
| `service_outage` | no signal, data, calls, or broad outage | human |
| `account_access` | login, verification, or personal data access | human |
| `cancellation` | cancellation, leaving, or formal complaint | human |
| `delivery_tracking` | handset/SIM delivery status | auto if confident |
| `unknown` | outside taxonomy or ambiguous | human |

`data/golden_set.jsonl` is the bundled illustrative evaluation fixture. For a real submission, replace or extend it with 150–250 genuinely hand-labelled examples sampled from a held-out brand slice, record annotator decisions, and report inter-annotator agreement. The raw-data adapter's labels are deterministic bootstrap labels and must not be presented as independent human labels.

## Evaluation design

`atlas_agent.evaluate` compares three systems:

* **Majority baseline:** always predicts the most common intent.
* **Keyword baseline:** weighted keyword counts, without retrieval.
* **AtlasCare:** keyword classifier plus confidence-aware nearest-example retrieval and policy routing.

Reported metrics include macro-F1, accuracy, top-1 evidence hit rate, escalation precision/recall, and a deterministic rubric proxy for grounded replies. The optional LLM judge contract is documented in `docs/judge_rubric.md`; judge agreement must be measured on a human-scored subset before using it as a headline number.

## Replacing the fixture with Kaggle data

```powershell
py scripts\prepare_kaggle.py --input twcs.csv --output data\brand_conversations.jsonl --brand AppleSupport --limit 500
py -m atlas_agent.cli --message "My iPhone cannot connect to Wi-Fi" --data data\brand_conversations.jsonl
py -m atlas_agent.evaluate --data data\golden_set.jsonl --train data\brand_conversations.jsonl
```

The preparation script is intentionally conservative: it keeps inbound customer messages, joins the referenced outbound response from the selected brand, drops empty/deleted tweets, and applies transparent bootstrap intent labels. These bootstrap labels are not a replacement for the required human-labelled golden set.

## Report

The submission narrative is in [`docs/report.md`](docs/report.md). It includes framing, baselines, failure analysis, the mandatory misleading-headline-number section, next-week plan, citations, and a decision log. Before submitting, replace the illustrative numbers with output from your actual held-out sample.

## Originality and citations

All application code and fixture text in this repository are original. The project borrows the problem framing from the Hiver take-home prompt and uses the public dataset named above only as an optional input format. No generated result should be represented as a result on the Kaggle corpus without running the pipeline on that corpus.