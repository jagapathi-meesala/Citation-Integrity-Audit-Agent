from __future__ import annotations

import re
from collections import Counter
from typing import Any

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
REQUIRED_FIELDS = ("title", "authors", "year")


def parse_document(document: Any) -> dict:
    if not isinstance(document, dict):
        raise ValueError("Input must be a JSON object.")
    claims = document.get("claims", [])
    references = document.get("references", [])
    if not isinstance(claims, list) or not isinstance(references, list):
        raise ValueError("'claims' and 'references' must be arrays.")
    if any(not isinstance(x, dict) for x in claims):
        raise ValueError("Every claim must be an object.")
    if any(not isinstance(x, dict) for x in references):
        raise ValueError("Every reference must be an object.")
    return {"claims": claims, "references": references}


def _finding(severity: str, rule: str, item: str, message: str, action: str) -> dict:
    return {"severity": severity, "rule": rule, "item": item, "message": message, "recommended_action": action}


def audit_document(document: Any) -> dict:
    data = parse_document(document)
    claims, references = data["claims"], data["references"]
    findings = []

    keys = []
    dois = []
    for index, ref in enumerate(references):
        key = str(ref.get("key", "")).strip()
        label = key or f"reference[{index}]"
        if not key:
            findings.append(_finding("error", "missing_reference_key", label,
                                     "Reference has no non-empty key.",
                                     "Assign a stable key and update matching in-text citations."))
        keys.append(key)
        for field in REQUIRED_FIELDS:
            value = ref.get(field)
            if value is None or value == "" or value == []:
                findings.append(_finding("warning", f"missing_{field}", label,
                                         f"Required bibliographic field '{field}' is missing or empty.",
                                         f"Verify the original source and supply '{field}' if confirmed."))
        doi = str(ref.get("doi", "")).strip()
        if doi:
            dois.append(doi.lower())
            if not DOI_RE.match(doi.removeprefix("https://doi.org/").removeprefix("http://doi.org/")):
                findings.append(_finding("warning", "doi_format", label,
                                         "DOI does not match the conservative local syntax check.",
                                         "Check the DOI against the publisher or a trusted registry."))
    key_counts = Counter(k for k in keys if k)
    for key, count in key_counts.items():
        if count > 1:
            findings.append(_finding("error", "duplicate_reference_key", key,
                                     f"Reference key occurs {count} times.",
                                     "Give each bibliography entry a unique key and recheck citations."))
    doi_counts = Counter(dois)
    for doi, count in doi_counts.items():
        if count > 1:
            findings.append(_finding("warning", "duplicate_doi", doi,
                                     f"DOI occurs in {count} reference entries.",
                                     "Check whether these entries refer to the same work or have copied metadata."))

    known_keys = set(k for k in keys if k)
    cited_keys = set()
    for index, claim in enumerate(claims):
        claim_label = str(claim.get("id") or f"claim[{index}]")
        citation_keys = claim.get("citation_keys", [])
        if not isinstance(citation_keys, list):
            findings.append(_finding("warning", "malformed_citation_keys", claim_label,
                                     "'citation_keys' must be an array.",
                                     "Represent each in-text citation as a reference key in an array."))
            continue
        for raw_key in citation_keys:
            key = str(raw_key).strip()
            if not key:
                findings.append(_finding("warning", "empty_citation_key", claim_label,
                                         "Claim contains an empty citation key.",
                                         "Identify the intended source or remove the empty citation."))
                continue
            cited_keys.add(key)
            if key not in known_keys:
                findings.append(_finding("error", "unmatched_citation", f"{claim_label}:{key}",
                                         f"Citation key '{key}' has no matching bibliography entry.",
                                         "Add the verified reference entry or correct the citation key."))

    for key in sorted(known_keys - cited_keys):
        findings.append(_finding("info", "uncited_reference", key,
                                 "Reference entry is not linked from any claim.",
                                 "Confirm whether the reference should be cited or removed."))

    severity_order = {"error": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda f: (severity_order[f["severity"]], f["rule"], f["item"]))
    counts = Counter(f["severity"] for f in findings)
    return {
        "status": "needs_review" if findings else "no_structural_issues_detected",
        "summary": {"claims": len(claims), "references": len(references), "findings": len(findings),
                    "errors": counts["error"], "warnings": counts["warning"], "info": counts["info"]},
        "findings": findings,
        "limitations": [
            "This audit checks structure and syntax, not source authenticity.",
            "It does not determine whether a source semantically supports a claim.",
            "Human verification against original sources is required."
        ]
    }
