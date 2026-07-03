#!/usr/bin/env python3
"""
truth_check.py — fabrication guard

Usage:
  python truth_check.py <resume.tex>

Compares a tailored resume against the trusted sources (both masters +
knowledge/ files). Numbers and metrics that appear nowhere in the trusted
sources are FAIL (likely fabricated). Tech-looking terms not in trusted
sources are WARN (review — may be a legitimately reframed JD keyword).
Exit code 1 on FAIL.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((REPO_ROOT / "config.json").read_text())

METRIC_PATTERN = re.compile(
    r"\d+\.?\d*\s*%|\$\s*\d[\d,\.]*[MKB]?|\d+\.?\d*\s*[MKB]\b|\d+\.?\d*x\b|\d[\d,]*\+?"
)


def load_trusted_text():
    parts = []
    for key in ("master", "master_full"):
        p = REPO_ROOT / CONFIG[key]
        if p.exists():
            parts.append(p.read_text())
    kdir = REPO_ROOT / CONFIG.get("knowledge_dir", "knowledge")
    if kdir.is_dir():
        for f in sorted(kdir.glob("*.md")):
            parts.append(f.read_text())
    return "\n".join(parts)


def body_of(tex):
    return re.split(r"(?m)^\\begin\{document\}", tex, maxsplit=1)[-1]


def extract_metrics(text):
    found = set()
    for m in METRIC_PATTERN.finditer(text):
        val = m.group().strip()
        norm = re.sub(r"[\s,]", "", val).lower()
        if re.fullmatch(r"\d{4}", norm):  # years
            continue
        if len(norm) < 2 and norm.isdigit():  # single digits are noise
            continue
        found.add(norm)
    return found


def extract_terms(text):
    """Lowercased tech-looking tokens (capitalized words, hyphenated, acronyms)."""
    terms = set()
    for token in re.findall(r"[A-Za-z][A-Za-z0-9+#.]*(?:-[A-Za-z0-9]+)*", text):
        if len(token) < 3:
            continue
        if token[0].isupper() or token.isupper() or "-" in token:
            terms.add(token.lower())
    return terms


def main():
    if len(sys.argv) != 2:
        print("Usage: python truth_check.py <resume.tex>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        tex = open(path).read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    trusted = load_trusted_text().lower()
    trusted_norm = re.sub(r"[\s,]", "", trusted)
    body = body_of(tex)

    # Metrics: every number in the tailored resume must exist in trusted sources
    resume_metrics = extract_metrics(body)
    fabricated = sorted(m for m in resume_metrics
                        if m not in trusted_norm)

    # Terms: new tech terms not present anywhere in trusted sources
    resume_terms = extract_terms(body)
    trusted_terms = extract_terms(trusted)
    new_terms = sorted(t for t in resume_terms
                       if t not in trusted_terms and t not in trusted)

    print(f"\nTRUTH CHECK — {path}")
    print("=" * 52)
    if fabricated:
        print(f"[FAIL] Metrics not found in masters/knowledge ({len(fabricated)}):")
        for m in fabricated:
            print(f"       → {m}")
        print("       Fabricated numbers are interview-fatal. Remove or source them.")
    else:
        print(f"[PASS] Metrics: all {len(resume_metrics)} traceable to trusted sources")

    if new_terms:
        print(f"[WARN] Terms not in masters/knowledge ({len(new_terms)}) — verify each is real experience:")
        print("       " + ", ".join(new_terms[:15]))

    print("=" * 52)
    sys.exit(1 if fabricated else 0)


if __name__ == "__main__":
    main()
