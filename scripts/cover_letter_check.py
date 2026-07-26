#!/usr/bin/env python3
"""
cover_letter_check.py <cover_letter.tex> — tone + length gate for a generated cover letter.

Mirrors the resume quality-gate philosophy but tuned for a first-person letter:
  1. Banned buzzwords / corporate filler — zero hits allowed (FAIL)
  2. AI-tell patterns — canned openers + vague future-gesturing — zero hits allowed (FAIL)
  3. Word-count of the letter body (salutation -> sign-off): target 300-330, hard cap 370

First-person ("I", "my", "me") is EXPECTED in a cover letter, so — unlike quality_check.py —
it is NOT flagged here. Prints [PASS]/[WARN]/[FAIL]; exits 1 on any FAIL so cover_letter.sh
aborts before compile.

Standard library only.
"""
import re
import sys

# Faithful to the cover-letter pattern template's "BANNED — buzzwords/corporate filler" list.
BANNED_BUZZWORDS = [
    "leverage synergies", "passionate about", "results-driven", "thrilled",
    "dynamic environment", "cutting-edge", "fast-paced", "go-getter", "team player",
    "wheelhouse", "proven track record", "hit the ground running", "wear many hats",
]

# The template's "BANNED — AI tells" that can be matched deterministically. Poetic openers,
# self-restating taglines, em-dash rhythm and tricolon padding are left to human/skill review.
AI_TELLS = [
    (r"\bI am excited to apply\b", "canned opener: 'I am excited to apply'"),
    (r"\bI[' ]?a?m excited to apply for\b", "canned opener: 'excited to apply for'"),
    (r"\bI am writing to express\b", "canned opener: 'I am writing to express'"),
    (r"\bwhere engineering is headed\b", "vague future-gesturing"),
    (r"\bin today'?s (landscape|world|market|climate)\b", "vague future-gesturing"),
    (r"\bI'?d love nothing more than\b", "over-eager filler"),
]

TARGET_LOW, TARGET_HIGH, HARD_CAP = 300, 330, 370


def strip_latex(text):
    """Remove LaTeX markup, return plain text (mirrors quality_check.py:strip_latex)."""
    text = re.sub(r'\$[^$]{0,20}\$', ' ', text)                # inline math $\sim$ etc.
    text = re.sub(r'\\href\{[^{}]*\}\{([^{}]*)\}', r'\1', text)  # \href{url}{text} -> text
    for _ in range(5):                                          # unwrap nested \cmd{arg} -> arg
        text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\*?', ' ', text)                 # bare \commands
    text = re.sub(r'[{}\\]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def letter_body(tex):
    """Plain-text letter body from the salutation to just before the sign-off."""
    part = re.split(r'(?m)^\\begin\{document\}', tex, maxsplit=1)[-1]
    plain = strip_latex(part)
    m = re.search(r'(Dear\b.*?)\b(Sincerely|Best regards|Kind regards|Regards|Warm regards)\b',
                  plain, re.IGNORECASE | re.DOTALL)
    return m.group(1) if m else plain


def word_count(text):
    return len([w for w in text.split() if re.search(r'[a-zA-Z]', w)])


def fmt(tag, msg):
    return f"[{tag}] {msg}"


def main():
    if len(sys.argv) < 2:
        print("Usage: cover_letter_check.py <cover_letter.tex>")
        sys.exit(2)
    path = sys.argv[1]
    with open(path) as f:
        tex = f.read()

    body = letter_body(tex)
    low = body.lower()
    fails = 0
    print(f"Cover letter check: {path}\n")

    # 1. Buzzwords
    hits = [b for b in BANNED_BUZZWORDS if re.search(r'\b' + re.escape(b) + r'\b', low)]
    if hits:
        print(fmt("FAIL", f"Buzzwords: {len(hits)} hit(s) -> {', '.join(hits)}"))
        fails += 1
    else:
        print(fmt("PASS", "Buzzwords: 0 hits"))

    # 2. AI-tells
    tell_hits = [desc for pat, desc in AI_TELLS if re.search(pat, body, re.IGNORECASE)]
    if tell_hits:
        print(fmt("FAIL", f"AI-tells: {len(tell_hits)} -> {'; '.join(tell_hits)}"))
        fails += 1
    else:
        print(fmt("PASS", "AI-tells: 0 hits"))

    # 3. Word count
    wc = word_count(body)
    if wc > HARD_CAP:
        print(fmt("FAIL", f"Word count: {wc} (hard cap {HARD_CAP})"))
        fails += 1
    elif wc < TARGET_LOW:
        print(fmt("WARN", f"Word count: {wc} (below target {TARGET_LOW}-{TARGET_HIGH})"))
    elif wc > TARGET_HIGH:
        print(fmt("WARN", f"Word count: {wc} (above target {TARGET_LOW}-{TARGET_HIGH}, under cap {HARD_CAP})"))
    else:
        print(fmt("PASS", f"Word count: {wc} (target {TARGET_LOW}-{TARGET_HIGH})"))

    print()
    if fails:
        print(f"RESULT: FAIL ({fails} blocking issue(s)) — fix before compiling.")
        sys.exit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
