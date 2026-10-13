import pytest
from core.audit import audit_document, parse_document


def test_clean_document_has_no_findings():
    data = {"claims": [{"id": "c1", "text": "claim", "citation_keys": ["r1"]}],
            "references": [{"key": "r1", "title": "Title", "authors": ["A"], "year": 2024, "doi": "10.1234/abc"}]}
    result = audit_document(data)
    assert result["summary"]["findings"] == 0
    assert result["status"] == "no_structural_issues_detected"


def test_unmatched_citation_and_uncited_reference():
    data = {"claims": [{"text": "claim", "citation_keys": ["absent"]}],
            "references": [{"key": "r1", "title": "Title", "authors": ["A"], "year": 2024}]}
    rules = {f["rule"] for f in audit_document(data)["findings"]}
    assert "unmatched_citation" in rules
    assert "uncited_reference" in rules


def test_missing_required_metadata():
    result = audit_document({"references": [{"key": "r1"}]})
    rules = {f["rule"] for f in result["findings"]}
    assert {"missing_title", "missing_authors", "missing_year"} <= rules


def test_duplicate_keys_and_dois():
    ref = {"key": "r1", "title": "T", "authors": ["A"], "year": 2024, "doi": "10.1234/x"}
    result = audit_document({"references": [ref, dict(ref)]})
    rules = {f["rule"] for f in result["findings"]}
    assert "duplicate_reference_key" in rules
    assert "duplicate_doi" in rules


def test_doi_url_prefix_is_accepted():
    data = {"references": [{"key": "r1", "title": "T", "authors": ["A"], "year": 2024,
                            "doi": "https://doi.org/10.1234/abc"}]}
    assert "doi_format" not in {f["rule"] for f in audit_document(data)["findings"]}


def test_bad_input_shapes():
    with pytest.raises(ValueError):
        parse_document([])
    with pytest.raises(ValueError):
        parse_document({"claims": {}, "references": []})


def test_non_list_citation_keys_flagged():
    result = audit_document({"claims": [{"id": "c1", "citation_keys": "r1"}]})
    assert "malformed_citation_keys" in {f["rule"] for f in result["findings"]}


def test_input_is_not_mutated():
    data = {"claims": [{"citation_keys": ["r1"]}], "references": [{"key": "r1", "title": "T", "authors": ["A"], "year": 2024}]}
    before = json_copy = __import__("copy").deepcopy(data)
    audit_document(data)
    assert data == before
