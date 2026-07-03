#!/usr/bin/env python3
"""
keyword_match.py — JD-to-resume keyword gap analysis + pre-analysis for Claude

Usage:
  python keyword_match.py <jd_file> <resume_file> [--verbose]

Output (default, brief — what Claude reads):
  1. Match score + missing keywords ranked by JD emphasis
  2. Unknown JD tech terms missing from resume
  3. JD archetype (streaming-DE / batch-DE / ml-adjacent / cloud-infra-DE / analytics-DE)
  4. Quick wins — top 3 keyword placement suggestions for Claude

--verbose adds: full present-in-resume list + unknown terms already in resume.
"""

import json
import sys
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
_config = json.loads((REPO_ROOT / "config.json").read_text())
_kw_data = json.loads((REPO_ROOT / _config["keywords_file"]).read_text())

KNOWN_KEYWORDS = _kw_data["known_keywords"]
ALIASES = _kw_data["aliases"]
SKILLS_CLUSTERS = _kw_data["skills_clusters"]
ARCHETYPES = _kw_data["archetypes"]
COMMON_WORDS = set(_kw_data["common_words"])


def normalize(text):
    return text.lower()


def count_keyword_frequency(jd_text, keywords):
    """Count how many times each keyword appears in the JD."""
    jd = normalize(jd_text)
    freq = {}
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        freq[kw] = len(re.findall(pattern, jd))
    return freq


def detect_archetype(jd_text, freq):
    """Score JD against archetype keyword sets, return top archetype with score."""
    jd = normalize(jd_text)
    scores = {}
    for archetype, signals in ARCHETYPES.items():
        score = 0
        for signal in signals:
            pattern = r'\b' + re.escape(signal) + r'\b'
            count = len(re.findall(pattern, jd))
            score += count
        scores[archetype] = score

    top = max(scores, key=scores.get)
    top_score = scores[top]

    # Build signal evidence string
    signals_found = []
    for signal in ARCHETYPES[top]:
        pattern = r'\b' + re.escape(signal) + r'\b'
        count = len(re.findall(pattern, jd))
        if count > 0:
            signals_found.append(f"{signal}×{count}")

    return top, top_score, signals_found[:5]


def keyword_to_cluster(kw):
    """Return which skills cluster a keyword belongs to."""
    for cluster, members in SKILLS_CLUSTERS.items():
        if kw in members:
            return cluster
    return "Skills (new cluster needed)"


def generate_quick_wins(missing, freq):
    """Top 3 highest-frequency missing keywords with placement suggestion."""
    if not missing:
        return []
    ranked = sorted(missing, key=lambda k: freq.get(k, 0), reverse=True)[:3]
    wins = []
    for kw in ranked:
        cluster = keyword_to_cluster(kw)
        f = freq.get(kw, 0)
        wins.append((kw, cluster, f))
    return wins


def extract_jd_keywords(jd_text):
    """Return set of curated keywords found in the JD."""
    jd = normalize(jd_text)
    found = set()
    for kw in KNOWN_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, jd):
            found.add(kw)
    return found


def check_resume(resume_text, keywords):
    """For each keyword, check if it (or an alias) appears in the resume."""
    resume = normalize(resume_text)
    present = set()
    missing = set()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, resume):
            present.add(kw)
            continue
        aliases = ALIASES.get(kw, [])
        if any(re.search(r'\b' + re.escape(a) + r'\b', resume) for a in aliases):
            present.add(kw)
            continue
        missing.add(kw)
    return present, missing


def extract_unknown_jd_terms(jd_text, resume_text):
    """Extract tech-looking terms from JD not in KNOWN_KEYWORDS, check against resume."""
    known_set = set(KNOWN_KEYWORDS)
    resume_lower = resume_text.lower()

    all_tokens = re.findall(r'[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*', jd_text)
    token_counts = Counter(t.lower() for t in all_tokens)

    candidates = set()
    for token in all_tokens:
        tl = token.lower()
        if tl in known_set or tl in COMMON_WORDS or len(tl) < 3:
            continue
        strong_signal = (
            token.isupper()
            or '-' in token
            or any(c.isdigit() for c in token)
        )
        # First-letter caps alone is weak (sentence starts) — require 2+ occurrences
        if not strong_signal:
            if token[0].isupper():
                if token_counts[tl] < 2:
                    continue
            elif len(tl) < 4 or token_counts[tl] < 3:
                continue
        candidates.add(tl)

    present = set()
    missing = set()
    for term in candidates:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, resume_lower):
            present.add(term)
        else:
            missing.add(term)
    return present, missing


def main():
    args = [a for a in sys.argv[1:] if a != "--verbose"]
    verbose = "--verbose" in sys.argv[1:]
    if len(args) != 2:
        print("Usage: python keyword_match.py <jd_file> <resume_file> [--verbose]")
        sys.exit(1)

    jd_path, resume_path = args[0], args[1]

    try:
        jd_text = open(jd_path).read()
    except FileNotFoundError:
        print(f"ERROR: JD file not found: {jd_path}")
        sys.exit(1)

    try:
        resume_text = open(resume_path).read()
    except FileNotFoundError:
        print(f"ERROR: Resume file not found: {resume_path}")
        sys.exit(1)

    jd_keywords = extract_jd_keywords(jd_text)

    if not jd_keywords:
        print("No known keywords found in JD. Check the JD content or expand KNOWN_KEYWORDS.")
        sys.exit(0)

    present, missing = check_resume(resume_text, jd_keywords)
    match_pct = round(len(present) / len(jd_keywords) * 100)
    freq = count_keyword_frequency(jd_text, jd_keywords)
    archetype, arch_score, arch_signals = detect_archetype(jd_text, freq)
    quick_wins = generate_quick_wins(missing, freq)
    unknown_present, unknown_missing = extract_unknown_jd_terms(jd_text, resume_text)

    sep = "=" * 54

    # ── Section 1: Match score ──────────────────────────────
    print(f"\n{sep}")
    print(f"KEYWORD MATCH REPORT")
    print(f"JD: {jd_path}  |  Resume: {resume_path}")
    print(f"{sep}")
    print(f"\nMatch score: {match_pct}%  ({len(present)}/{len(jd_keywords)} known JD keywords)\n")

    if missing:
        # Sort missing by frequency (most emphasized first)
        missing_ranked = sorted(missing, key=lambda k: freq.get(k, 0), reverse=True)
        print(f"MISSING from resume ({len(missing)}) — sorted by JD emphasis:")
        for kw in missing_ranked:
            f = freq.get(kw, 0)
            marker = f" ×{f}" if f > 1 else ""
            print(f"  - {kw}{marker}")
    else:
        print("No missing known keywords — full coverage.")

    if verbose:
        print(f"\nPresent in resume ({len(present)}):")
        for kw in sorted(present):
            f = freq.get(kw, 0)
            marker = f" ×{f}" if f > 1 else ""
            print(f"  + {kw}{marker}")

    # ── Section 2: Unknown JD terms ────────────────────────
    if unknown_missing:
        print(f"\nUNKNOWN JD TERMS — not in known list, missing from resume ({len(unknown_missing)}):")
        print("  (Claude: assess each — real tech worth adding vs noise)")
        for kw in sorted(unknown_missing):
            print(f"  ? {kw}")

    if verbose and unknown_present:
        print(f"\nUnknown JD terms already in resume ({len(unknown_present)}):")
        for kw in sorted(unknown_present):
            print(f"  ~ {kw}")

    # ── Section 3: Pre-analysis for Claude ─────────────────
    print(f"\n{sep}")
    print(f"PRE-ANALYSIS (read this instead of the full JD)")
    print(f"{sep}")

    signals_str = ", ".join(arch_signals) if arch_signals else "—"
    print(f"\nARCHETYPE: {archetype}  [{signals_str}]")

    if quick_wins:
        print(f"\nQUICK WINS — top {len(quick_wins)} missing keywords by JD emphasis:")
        for kw, cluster, f in quick_wins:
            freq_str = f" (appears ×{f} in JD)" if f > 0 else ""
            print(f"  → Add \"{kw}\" to Skills > {cluster}{freq_str}")

    print(f"\n{sep}")
    print("Claude: write analysis.md from the above — do not re-read the full JD in quick mode.")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
