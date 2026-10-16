# AtlasCare support classification baseline

## Overview

A deterministic, offline baseline for classifying support messages and deciding whether to escalate them. It combines token-based intent scoring with nearest-example retrieval and fixed reply templates. It does not call an LLM or require an API key.

## System architecture and modules

| Path | Responsibility |
| --- | --- |
| `atlas_agent/engine.py` | SupportAgent scoring, Jaccard retrieval, confidence thresholds, and routing. |
| `atlas_agent/data.py` | Example model and JSONL loading. |
| `atlas_agent/cli.py` | Single-message command-line interface. |
| `atlas_agent/evaluate.py / atlas_agent/metrics.py` | Baseline comparisons and evaluation metrics. |
| `data/` | Bundled training and illustrative evaluation fixtures. |
| `scripts/prepare_kaggle.py` | Converts a supplied Twitter customer-support CSV into brand conversations. |
| `tests/test_agent.py` | Unit tests for classification and escalation. |
| `docs/report.md / docs/judge_rubric.md` | Assignment report and optional judging rubric. |

## Tech stack

Python >=3.10 and the Python standard library. `pyproject.toml` uses setuptools and registers the `atlas-agent` command. There is no database, web service, or external model dependency.

## Local setup

```bash
git clone https://github.com/shreyasingh3005/Hiver-SDE-Intern-Assignment.git
cd Hiver-SDE-Intern-Assignment
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m atlas_agent.cli --message "My iPhone cannot connect to Wi-Fi"
python -m unittest discover -s tests -v
python -m atlas_agent.evaluate
```

On Windows use `py -m venv .venv` and `.\.venv\Scripts\Activate.ps1`. Evaluation writes `artifacts/evaluation.json`.

For a separately supplied dataset:

```bash
python scripts/prepare_kaggle.py --input twcs.csv --output data/brand_conversations.jsonl --brand AppleSupport --limit 500
python -m atlas_agent.evaluate --data data/golden_set.jsonl --train data/brand_conversations.jsonl
```

## Implementation notes and limits

- `engine.py` scores intent terms, retrieves an example within the predicted intent, and escalates risky intents or weak confidence/similarity. Retrieval evidence is returned separately; reply text comes from fixed templates rather than being generated from the retrieved response.
- Bundled fixtures are illustrative. Results on them must not be described as independently labelled, held-out production accuracy or a Kaggle benchmark.
- The CSV adapter uses bootstrap labels. A credible model evaluation still needs independent labels, a clean train/test split, leakage checks, and error analysis.
- Earlier narrative and artifact numbers are retained for traceability; rerun evaluation before citing them. The CLI does not send replies to customers.
