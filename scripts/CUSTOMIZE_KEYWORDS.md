# Customizing the keyword bank for your role

`scripts/keyword_match.py` ships with a keyword bank tuned for **Data / AI / Cloud Engineering**
roles (matching the Alex Morgan demo persona). If you're targeting a different field — frontend,
product management, marketing, data science, DevOps, security, etc. — retune the bank so the match
score and placement hints actually mean something for your JDs.

You don't have to write the lists by hand. Paste the prompt below into any AI chat, fill in your
target role, and drop the generated Python back into the script.

---

## What you're editing

All of it lives near the top of `scripts/keyword_match.py` as plain Python data — no logic to touch:

| Structure | Where (approx.) | What it does |
|-----------|-----------------|--------------|
| `KNOWN_KEYWORDS` | lines ~20–64 | The master list of tech/terms the script looks for in a JD. **The main thing to change.** |
| `ALIASES` | ~67–77 | Treats variants as the same keyword (e.g. `postgres` = `postgresql`). |
| `SKILLS_CLUSTERS` | ~80–113 | Maps each keyword to a resume Skills section, so the script can say "add X to Skills > Y". |
| `ARCHETYPES` | ~116–130 | Sub-types of your role; drives the one-line archetype guess. Optional but nice. |
| `COMMON_WORDS` | ~133–156 | Stop words ignored in the unknown-term scan. Usually leave as-is. |

**Two rules that matter:**
1. Every keyword is a **lowercase string**. The match is case-insensitive and whole-word.
2. The **keys in `SKILLS_CLUSTERS` must exactly match the bold section labels in your resume's
   `\section{Skills}`** (the `\textbf{...}` labels). The default labels are
   `Programming & Tools`, `Databases`, `Big Data & Visualization`, `ML & AI`, `AWS Services`. If you
   rename your resume's skill categories, rename the cluster keys to match, or the placement hints
   point at sections that don't exist.

---

## The prompt

Copy this into any AI chat. Replace the two bracketed lines, then run it.

```text
You are helping me configure a resume keyword-matching script. I am targeting:

  TARGET ROLE: [e.g. Senior Frontend Engineer]
  MY RESUME SKILLS SECTION LABELS: [e.g. Languages, Frameworks, Tools, Testing]

Generate three Python data structures I can paste directly into the script. Output ONLY a single
```python code block, nothing else. Rules:

1. KNOWN_KEYWORDS: a Python list of 120–180 lowercase strings — the tools, languages, frameworks,
   platforms, concepts, and standard terms that show up in real job postings for the TARGET ROLE.
   Group them with `# Category` comments (e.g. # Languages, # Frameworks, # Testing). Lowercase only.
   Use the exact spelling that appears in JDs (e.g. "ci/cd", "rest", "next.js").

2. SKILLS_CLUSTERS: a Python dict. The KEYS must be exactly the labels I gave in
   "MY RESUME SKILLS SECTION LABELS". The VALUE for each key is a list of the KNOWN_KEYWORDS that
   belong in that resume section. Every keyword should appear in exactly one cluster.

3. ARCHETYPES: a Python dict mapping 3–5 sub-specialties of the TARGET ROLE (short kebab-case names)
   to a list of 8–12 signal keywords drawn from KNOWN_KEYWORDS that most distinguish that sub-type.

Match this shape exactly:

KNOWN_KEYWORDS = [
    # Category A
    "term-a", "term-b",
    # Category B
    "term-c",
]
SKILLS_CLUSTERS = {
    "Label One": ["term-a", "term-b"],
    "Label Two": ["term-c"],
}
ARCHETYPES = {
    "sub-type-one": ["term-a", "term-c"],
    "sub-type-two": ["term-b"],
}
```

---

## Dropping it in

1. Open `scripts/keyword_match.py`.
2. Replace the existing `KNOWN_KEYWORDS = [ ... ]` block with the generated one. (Replace
   `SKILLS_CLUSTERS` and `ARCHETYPES` too if you regenerated them — recommended for a clean retarget.)
3. Make sure each `SKILLS_CLUSTERS` key matches a bold label in your resume's `\section{Skills}`.
4. Sanity-check it runs:

   ```bash
   python3 scripts/keyword_match.py jobs/<some_company>/jd.txt master-1page/resume.tex
   ```

   You should get a match score, a missing/present breakdown, and an archetype line. If it prints
   *"No known keywords found in JD"*, your bank is too narrow for that JD — add the obvious terms and
   re-run.

> Tip: `ALIASES` and `COMMON_WORDS` rarely need changes. Add to `ALIASES` only when one tool has two
> common spellings you want scored as one (e.g. `"node.js": ["nodejs", "node"]`). Add to
> `COMMON_WORDS` if a generic word in your field keeps showing up as a false "unknown tech term".
