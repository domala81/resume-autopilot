#!/usr/bin/env python3
"""
reorder_bullets.py — surface the strongest JD-matching bullets to the top of each role

Usage:
  python reorder_bullets.py <resume.tex> <jd_file>          # dry-run: print proposed order
  python reorder_bullets.py <resume.tex> <jd_file> --apply  # write the new order

How it works (zero AI tokens):
  - Scores every \\resumeItem against the JD: sum of JD frequencies of matched
    keywords (aliases counted), +1 bonus if the bullet carries a metric.
  - Reorders bullets WITHIN each role only (stable sort — ties keep master order).
    Role order and bullet text are never changed.
  - A bullet containing a "% pin" comment keeps its exact position.
  - Safety: asserts the result is a pure permutation of the original bullets —
    nothing added, dropped, or reworded.
"""

import re
import sys

from keyword_match import (ALIASES, extract_jd_keywords,
                           count_keyword_frequency, normalize)

ITEM_RE = re.compile(r'\\resumeItem\{(?:[^{}]|\{[^{}]*\})*\}(?:[ \t]*%[ \t]*pin)?')
SPAN_RE = re.compile(r'\\resumeItemListStart(.*?)\\resumeItemListEnd', re.DOTALL)
METRIC_RE = re.compile(r'\d+\.?\d*\s*(%|[MKBx]\b)|\$\s*\d|\b\d{2,}\b')


def bullet_score(text, jd_keywords, freq):
    plain = normalize(text)
    score = 0.0
    matched = []
    for kw in jd_keywords:
        terms = [kw] + ALIASES.get(kw, [])
        if any(re.search(r'\b' + re.escape(t) + r'\b', plain) for t in terms):
            f = max(1, freq.get(kw, 0))
            score += f
            matched.append(f"{kw}×{f}" if f > 1 else kw)
    if METRIC_RE.search(text):
        score += 1
    return score, matched


def role_label(tex, span_start):
    """Nearest \\resumeSubheading or \\resumeProjectHeading name above the span."""
    head = tex[:span_start]
    m = None
    for m in re.finditer(r'\\resume(?:Sub|Project)heading\s*\{([^{}]*(?:\{[^{}]*\})?[^{}]*)\}', head, re.IGNORECASE):
        pass
    if not m:
        return "?"
    label = re.sub(r'\\[a-zA-Z]+\*?|\{|\}', '', m.group(1)).strip()
    return label[:40] or "?"


def main():
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply_mode = "--apply" in sys.argv[1:]
    if len(args) != 2:
        print("Usage: python reorder_bullets.py <resume.tex> <jd_file> [--apply]")
        sys.exit(1)

    tex_path, jd_path = args
    tex = open(tex_path).read()
    jd_text = open(jd_path).read()
    # Only operate on the body — the preamble defines the resumeItem commands
    body_start = re.search(r'(?m)^\\begin\{document\}', tex)
    body_start = body_start.end() if body_start else 0

    jd_keywords = extract_jd_keywords(jd_text)
    if not jd_keywords:
        print("No known keywords found in JD — nothing to rank by.")
        sys.exit(0)
    freq = count_keyword_frequency(jd_text, jd_keywords)

    new_tex = tex
    changed_blocks = 0
    offset = 0
    for span in SPAN_RE.finditer(tex, body_start):
        inner = span.group(1)
        items = ITEM_RE.findall(inner)
        if len(items) < 2:
            continue

        scored = []
        for i, raw in enumerate(items):
            pinned = bool(re.search(r'%[ \t]*pin', raw))
            s, matched = bullet_score(raw, jd_keywords, freq)
            scored.append({"i": i, "raw": raw, "pin": pinned, "score": s, "matched": matched})

        movable = [b for b in scored if not b["pin"]]
        movable.sort(key=lambda b: -b["score"])  # stable: ties keep original order
        slots = iter(movable)
        new_order = [b if b["pin"] else next(slots) for b in scored]

        if [b["i"] for b in new_order] == list(range(len(items))):
            continue

        label = role_label(tex, span.start())
        changed_blocks += 1
        print(f"\n{label}:")
        for pos, b in enumerate(new_order, 1):
            flag = " [pinned]" if b["pin"] else ""
            hits = ", ".join(b["matched"]) if b["matched"] else "no JD keywords"
            marker = "" if b["i"] == pos - 1 else f"  (was {b['i'] + 1})"
            print(f"  {pos}. score {b['score']:g}{flag} — {hits}{marker}")

        new_inner = inner
        # Replace items in reverse original order to keep indices valid
        matches = list(ITEM_RE.finditer(inner))
        rebuilt = []
        last = 0
        for m, b in zip(matches, new_order):
            rebuilt.append(inner[last:m.start()])
            rebuilt.append(b["raw"])
            last = m.end()
        rebuilt.append(inner[last:])
        new_inner = "".join(rebuilt)

        s_abs, e_abs = span.start(1) + offset, span.end(1) + offset
        new_tex = new_tex[:s_abs] + new_inner + new_tex[e_abs:]
        offset += len(new_inner) - len(inner)

    if changed_blocks == 0:
        print("No reordering needed — top bullets already best match the JD.")
        return

    # Safety: pure permutation — identical bullet multiset before and after
    assert sorted(ITEM_RE.findall(tex)) == sorted(ITEM_RE.findall(new_tex)), \
        "ABORT: bullet content changed — refusing to write."
    # Preamble untouched
    assert tex.split(r'\begin{document}')[0] == new_tex.split(r'\begin{document}')[0]

    if apply_mode:
        open(tex_path, "w").write(new_tex)
        print(f"\nApplied: {changed_blocks} block(s) reordered in {tex_path}")
    else:
        print(f"\nDry-run: {changed_blocks} block(s) would change. Re-run with --apply to write.")


if __name__ == "__main__":
    main()
