# Citation Integrity Audit Agent

A local, deterministic starter agent for auditing citation structure and evidence traceability in research drafts. It checks bibliography identifiers/fields, detects duplicate reference entries, finds in-text citation keys that do not map to references, and flags references that are never cited. It does **not** prove that a source supports a claim or certify that a paper is genuine; those checks require source access and human review.

## Features
- Parse a simple JSON research draft.
- Detect missing reference fields and duplicate reference keys.
- Compare in-text citation keys with bibliography keys.
- Flag uncited bibliography entries.
- Produce machine-readable findings with severity and evidence.

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
python3 -m core.cli examples/research_draft.json
```

## Input format
See `examples/research_draft.json`. The tool expects `claims` as records with `text` and `citation_keys`, and `references` as records with `key`, `title`, `authors`, `year`, and `doi` (fields may be omitted so they can be flagged).

## Interpretation
Findings are warnings for a researcher or editor to review. DOI format checks are syntactic only; metadata correctness, source authenticity, and claim-source entailment are not verified automatically. Never silently invent or repair bibliographic facts.

## Validation
```bash
python3 -m pytest -q
python3 verification/readiness_audit.py
opengap validate
```
