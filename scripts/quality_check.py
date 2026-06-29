#!/usr/bin/env python3
"""
quality_check.py — Resume quality checklist enforcement

Usage:
  python quality_check.py <resume.tex>

Checks (matching CLAUDE.md checklist):
  1. Metrics count — need 5+ measurable numbers
  2. Word count — target 500-600 words (bullet content only)
  3. Soft skill signals — need 2+ behavioral signals
  4. Buzzword ban — zero hits allowed
"""

import re
import sys


BUZZWORDS = [
    "spearheaded", "passionate", "results-driven", "detail-oriented",
    "synergy", "leverage",
]
FIRST_PERSON = [r"\bI\b", r"\bmy\b", r"\bme\b"]

SOFT_SIGNALS = [
    "led", "collaborated", "mentored", "partnered", "coordinated",
    "drove", "communicated", "cross-functional", "stakeholder",
    "ownership", "initiative",
]

METRIC_PATTERNS = [
    r"\d+\.?\d*\s*%",           # percentages: 80%, 4.2%
    r"\$\s*\d[\d,\.]*[MKB]?",  # dollar amounts: $1.2M, $500K
    r"\d+\.?\d*\s*[MKB]\b",    # scale: 4.2B, 10M, 500K
    r"\d+\.?\d*x\b",           # multipliers: 5x, 2.5x
    r"\d+\+?\s*(hours?|days?|weeks?|months?|years?)",  # time: 6 months
    r"(?<![,\d])\b\d{2,}\b(?![,\d])",  # standalone integers 10+ (not inside comma-separated numbers)
]


def extract_bullets(tex):
    """Extract plain text from \\resumeItem{...} blocks."""
    bullets = []
    for match in re.finditer(r'\\resumeItem\{((?:[^{}]|\{[^{}]*\})*)\}', tex, re.DOTALL):
        text = strip_latex(match.group(1))
        if text.strip():
            bullets.append(text.strip())
    return bullets


def strip_latex(text):
    """Remove LaTeX markup, return plain text."""
    # Strip inline math $...$ (e.g. $\sim$, $\approx$) before dollar-amount detection
    text = re.sub(r'\$[^$]{0,20}\$', ' ', text)
    # Remove \command[opt]{arg} and \command{arg}
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}', r'\1', text)
    # Remove remaining \commands
    text = re.sub(r'\\[a-zA-Z]+\*?', ' ', text)
    # Remove leftover braces and special chars
    text = re.sub(r'[{}\\]', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def check_metrics(bullets):
    found = []
    for i, bullet in enumerate(bullets, 1):
        bullet_metrics = set()
        for pattern in METRIC_PATTERNS:
            for m in re.finditer(pattern, bullet, re.IGNORECASE):
                val = m.group().strip()
                # Skip bare 2-digit numbers that look like years or dates
                if re.fullmatch(r'\d{4}', val):
                    continue
                bullet_metrics.add(val)
        for val in bullet_metrics:
            found.append((val, i, bullet[:60]))
    return found


def check_wordcount(tex):
    """Count words in all resume content (bullets + section text, not preamble)."""
    body = tex.split(r'\begin{document}', 1)[-1]
    # Unwrap \command{content} → content (preserve text inside braces)
    for _ in range(5):  # iterate to handle nested braces
        body = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}', r'\1', body)
    # Remove bare commands and structural chars
    body = re.sub(r'\\[a-zA-Z]+\*?', ' ', body)
    body = re.sub(r'[{}\\]', ' ', body)
    words = [w for w in body.split() if re.search(r'[a-zA-Z]', w)]
    return len(words)


def check_soft_skills(bullets):
    found = {}
    all_text = " ".join(bullets).lower()
    for signal in SOFT_SIGNALS:
        if re.search(r'\b' + re.escape(signal) + r'\b', all_text):
            # Find which bullet
            for i, b in enumerate(bullets, 1):
                if re.search(r'\b' + re.escape(signal) + r'\b', b.lower()):
                    found[signal] = i
                    break
    return found


def check_buzzwords(tex_lines):
    hits = []
    for lineno, line in enumerate(tex_lines, 1):
        plain = strip_latex(line).lower()
        for word in BUZZWORDS:
            if re.search(r'\b' + re.escape(word) + r'\b', plain):
                # Allow "leverage" when used technically (preceded by tool/infra context)
                if word == "leverage":
                    context = plain
                    if any(t in context for t in ["technical", "infrastructure", "aws", "cloud", "api"]):
                        continue
                hits.append((lineno, word, line.strip()[:70]))
        for pattern in FIRST_PERSON:
            if re.search(pattern, strip_latex(line)):
                hits.append((lineno, pattern.replace(r'\b', ''), line.strip()[:70]))
    return hits


def fmt_pass(label):
    return f"[PASS] {label}"


def fmt_fail(label):
    return f"[FAIL] {label}"


def fmt_warn(label):
    return f"[WARN] {label}"


def main():
    if len(sys.argv) != 2:
        print("Usage: python quality_check.py <resume.tex>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        tex = open(path).read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    tex_lines = tex.splitlines()
    bullets = extract_bullets(tex)

    if not bullets:
        print("WARNING: No \\resumeItem bullets found. Check file is a Jake-format resume.")
        sys.exit(1)

    sep = "=" * 52
    print(f"\nQUALITY CHECK — {path}")
    print(sep)

    passes = 0
    total = 4

    # Check 1: Metrics
    metrics = check_metrics(bullets)
    unique_metrics = list({m[0]: m for m in metrics}.values())
    if len(unique_metrics) >= 5:
        print(fmt_pass(f"Metrics: {len(unique_metrics)} found (need 5+)"))
        passes += 1
    else:
        print(fmt_fail(f"Metrics: {len(unique_metrics)} found (need 5+) — ADD MORE"))
    for val, bullet_num, snippet in unique_metrics[:10]:
        print(f"       → {val!r} (bullet {bullet_num}): {snippet}...")

    # Check 2: Word count
    wc = check_wordcount(tex)
    if 500 <= wc <= 600:
        print(fmt_pass(f"Word count: {wc} words (target 500–600)"))
        passes += 1
    elif wc < 500:
        print(fmt_warn(f"Word count: {wc} words — ADD ~{500 - wc} words"))
    else:
        print(fmt_warn(f"Word count: {wc} words — TRIM ~{wc - 600} words"))
    # Word count is warn-only, doesn't count as fail/pass in overall score
    total = 3

    # Check 3: Soft skills
    signals = check_soft_skills(bullets)
    if len(signals) >= 2:
        print(fmt_pass(f"Soft skills: {len(signals)} signals found ({', '.join(signals.keys())})"))
        passes += 1
    else:
        print(fmt_fail(f"Soft skills: {len(signals)} signals found (need 2+)"))
        if signals:
            print(f"       → Found: {', '.join(signals.keys())}")

    # Check 4: Buzzwords
    bw_hits = check_buzzwords(tex_lines)
    if not bw_hits:
        print(fmt_pass("Buzzwords: 0 hits"))
        passes += 1
    else:
        print(fmt_fail(f"Buzzwords: {len(bw_hits)} hit(s)"))
        for lineno, word, snippet in bw_hits:
            print(f"       → line {lineno}: '{word}' — {snippet}")

    print(sep)
    if passes == total:
        print(f"Overall: {passes}/{total} checks passed. READY TO COMPILE.")
    else:
        print(f"Overall: {passes}/{total} checks passed. Fix FAIL items before compiling.")
    print()


if __name__ == "__main__":
    main()
