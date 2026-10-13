from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "agent.yaml", "README.md", "SOUL.md", "RULES.md", "DUTIES.md", "AGENTS.md",
    "EXPLAINABILITY.md", "requirements.txt", ".env.example", ".gitignore", "pytest.ini",
    "core/__init__.py", "core/audit.py", "core/cli.py",
    "tools/citation-parser.yaml", "tools/source-metadata-checker.yaml", "tools/claim-evidence-auditor.yaml",
    "skills/citation-source-verification/SKILL.md", "skills/claim-evidence-mapping/SKILL.md",
    "skills/bibliography-consistency/SKILL.md", "tests/test_audit.py", "verification/readiness_audit.py",
    "examples/research_draft.json", "adapters/.gitkeep", "config/.gitkeep", "contracts/.gitkeep"
]
missing = [item for item in REQUIRED if not (ROOT / item).exists()]
if missing:
    print("FAIL: missing required files:")
    print("\n".join(missing))
    sys.exit(1)
print(f"PASS: all {len(REQUIRED)}/{len(REQUIRED)} required files present")
