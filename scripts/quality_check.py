#!/usr/bin/env python3
"""
quality_check.py — Resume quality checklist enforcement

Usage:
  python quality_check.py <resume.tex>

Checks (matching CLAUDE.md checklist):
  1. Metrics count — need 5+ measurable numbers
  2. Word count — target 475-600 words (bullet content only) [WARN only]
  3. Soft skill signals — need 2+ behavioral signals
  4. Buzzword ban — zero hits allowed
  5. Preamble integrity — LaTeX preamble must match master exactly
  6. Duplicate bullets — no two identical bullets
  7. Keyword stuffing — any term used 3+ times flagged [WARN only]
  8. Bullet style — action-verb start, <=32 words per bullet [WARN only]
"""

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((REPO_ROOT / "config.json").read_text())


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


def split_doc(tex):
    """Split at the real \\begin{document} (start of line — ignores mentions in comments)."""
    parts = re.split(r'(?m)^\\begin\{document\}', tex, maxsplit=1)
    return parts[0], parts[-1]


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
    body = split_doc(tex)[1]
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


def preamble_hash(tex):
    """Hash of everything before \\begin{document}, ignoring comment lines and blank lines."""
    pre = split_doc(tex)[0]
    lines = [ln.strip() for ln in pre.splitlines()
             if ln.strip() and not ln.strip().startswith('%')]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def check_preamble(tex, path):
    """Compare preamble against master. Returns None if this file IS a master."""
    master_path = REPO_ROOT / CONFIG["master"]
    if Path(path).resolve() in (master_path.resolve(),
                                (REPO_ROOT / CONFIG["master_full"]).resolve()):
        return None
    master_tex = master_path.read_text()
    return preamble_hash(tex) == preamble_hash(master_tex)


def check_duplicates(bullets):
    seen = {}
    dupes = []
    for i, b in enumerate(bullets, 1):
        key = b.lower().strip()
        if key in seen:
            dupes.append((seen[key], i, b[:60]))
        else:
            seen[key] = i
    return dupes


def check_stuffing(bullets, tex):
    """Flag tech-looking terms appearing 3+ times across bullets + skills."""
    body = split_doc(tex)[1]
    body = re.sub(r'\\(begin|end)\{[^}]*\}', ' ', body)
    text = strip_latex(body).lower()
    words = re.findall(r'[a-z][a-z0-9+#./-]{2,}', text)
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    stopset = {"and", "the", "for", "with", "data", "using", "across", "from",
               "into", "that", "per", "via", "over", "through", "engineer",
               "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep",
               "oct", "nov", "dec", "january", "february", "march", "april",
               "june", "july", "august", "september", "october", "november",
               "december", "present"}
    return sorted((w, c) for w, c in counts.items()
                  if c >= 3 and w not in stopset and not w.isdigit())


def check_bullet_style(bullets):
    """WARN: bullets not starting with a verb-like word, or over 32 words."""
    issues = []
    non_verb_starters = {"the", "a", "an", "responsible", "worked", "helped",
                         "various", "also", "successfully"}
    for i, b in enumerate(bullets, 1):
        wc = len(b.split())
        first = b.split()[0].lower().rstrip(',.') if b.split() else ""
        if wc > 32:
            issues.append((i, f"{wc} words (cap 32)", b[:50]))
        if first in non_verb_starters or first.endswith("ing"):
            issues.append((i, f"weak opener '{first}'", b[:50]))
    return issues


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
        for val, bullet_num, snippet in unique_metrics[:5]:
            print(f"       → {val!r} (bullet {bullet_num}): {snippet}...")

    # Check 2: Word count (warn-only — not counted in pass/fail score)
    wc = check_wordcount(tex)
    if 475 <= wc <= 600:
        print(fmt_pass(f"Word count: {wc} words (target 475–600)"))
    elif wc < 475:
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

    # Check 5: Preamble integrity (skipped for masters)
    preamble_ok = check_preamble(tex, path)
    if preamble_ok is not None:
        total += 1
        if preamble_ok:
            print(fmt_pass("Preamble: matches master (formatting intact)"))
            passes += 1
        else:
            print(fmt_fail("Preamble: DIFFERS from master — formatting was modified"))

    # Check 6: Duplicate bullets
    dupes = check_duplicates(bullets)
    total += 1
    if not dupes:
        print(fmt_pass("Duplicates: none"))
        passes += 1
    else:
        print(fmt_fail(f"Duplicates: {len(dupes)} bullet(s) repeated"))
        for a, b, snippet in dupes:
            print(f"       → bullets {a} and {b}: {snippet}...")

    # Check 7: Keyword stuffing (warn-only)
    stuffed = check_stuffing(bullets, tex)
    if stuffed:
        top = ", ".join(f"{w}×{c}" for w, c in sorted(stuffed, key=lambda x: -x[1])[:8])
        print(fmt_warn(f"Stuffing: {len(stuffed)} term(s) used 3+ times — {top}"))

    # Check 8: Bullet style (warn-only)
    style = check_bullet_style(bullets)
    for i, issue, snippet in style[:5]:
        print(fmt_warn(f"Bullet {i}: {issue} — {snippet}..."))

    print(sep)
    if passes == total:
        print(f"Overall: {passes}/{total} checks passed. READY TO COMPILE.")
    else:
        print(f"Overall: {passes}/{total} checks passed. Fix FAIL items before compiling.")
    print()


if __name__ == "__main__":
    main()
