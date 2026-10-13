# Explainability

## Inputs
The agent reads a JSON document containing claims and reference records. Claims provide text and citation keys; references provide a key and bibliographic metadata fields.

## Decision
The agent applies deterministic checks for missing required metadata, duplicate keys/DOIs, DOI syntax, unmatched citation keys, and uncited references. Each finding records the rule, affected item, explanation, severity, and a suggested next step.

## Limits
Structural checks do not establish source authenticity, factual correctness, or whether a cited source entails a claim. Source-level verification and final editorial decisions require human review.

## Tool: citation-parser

### Inputs and Data Sources
A local JSON document with `claims` and `references` arrays.

### Decision and Reasoning
Validates the top-level shape and normalizes absent arrays to empty lists without changing individual records.

### Outputs and Evidence
Returns parsed claim and reference records; parse or shape errors are surfaced as exceptions.

### Limits and Constraints
Does not parse arbitrary PDF files or infer citation style.

### Failure Handling
Reports JSON decoding and input-shape errors to the caller.

### Human Review
Confirm that the supplied JSON faithfully represents the manuscript and bibliography.

## Tool: source-metadata-checker

### Inputs and Data Sources
Reference records supplied in the input JSON.

### Decision and Reasoning
Checks required fields, duplicate keys, duplicate DOI strings, and DOI syntax with conservative local rules.

### Outputs and Evidence
Produces findings tied to a reference key and the exact rule that was triggered.

### Limits and Constraints
Does not query Crossref, publishers, libraries, or the web; a syntactically valid DOI may still be incorrect.

### Failure Handling
Malformed or missing fields produce findings instead of guessed replacements.

### Human Review
Verify metadata against the publisher or trusted scholarly index before changing a record.

## Tool: claim-evidence-auditor

### Inputs and Data Sources
Claim records and their citation keys, compared with the reference keys.

### Decision and Reasoning
Reports citation keys that lack reference entries and references that are not cited by any claim.

### Outputs and Evidence
Produces unmatched-citation and uncited-reference findings with record-level evidence.

### Limits and Constraints
Does not establish semantic support between a claim and source content.

### Failure Handling
Missing or malformed citation key lists are flagged conservatively.

### Human Review
Open each cited source and verify that it supports the associated claim in context.
