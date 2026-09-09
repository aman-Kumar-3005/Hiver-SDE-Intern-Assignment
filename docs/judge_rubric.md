# Reply judge rubric

Score each reply from 0 to 2 on four independent dimensions:

* **Relevance:** addresses the customer intent.
* **Grounding:** supported by the retrieved historical example or approved policy; no invented account facts.
* **Actionability:** gives a safe next step.
* **Tone:** concise, respectful, and appropriate for a public support channel.

Total score is 0–8. A human judge labels 30 stratified examples (all intents plus both routing decisions). The automated judge may be used only after agreement is reported as weighted Cohen's kappa or exact agreement against those human labels. The deterministic proxy in this repository is not an LLM judge and must not be described as one.