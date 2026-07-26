---
name: resume-cover-letter
description: Use to generate a tailored, one-page cover letter for a target-company role after the tailored resume is finalized. Full-mode only, and only when the user explicitly asks for one — never auto-run per application. Follows a four-beat pattern with hard tone gates and the same truth constraints as the resume.
---

# Resume Cover Letter

> **Customize me:** the selectors below reference *categories* of achievement (your biggest
> automation win, your largest pipeline, etc.). Map each to real stories in your `knowledge/`
> files before using. The header and sign-off read from `config.json`. Never invent a metric —
> `truth_check.py` blocks any number not traceable to your masters/knowledge.

## When to use

Full-mode target companies only, AFTER `finish_job.sh` passes. Generate **only** when the user
answers yes to "Want a cover letter for this role?" — never for every application. A cover letter
roughly doubles a full-mode job's token cost, so it is opt-in per role.

## Inputs (already in context from tailoring — do not re-analyze the JD from scratch)

- `jobs/<folder>/analysis.md` — top JD priorities + planned changes = the "why me" argument
- `jobs/<folder>/resume.tex` — the tailored resume's 2–3 strongest bullets for those priorities
- `jobs/<folder>/jd.txt` — ROLE_TITLE, COMPANY, named stack keywords, soft emphasis
- `knowledge/` — exact metrics/tech (truth-gated, same as the resume)
- `config.json` — name/email/phone/linkedin for the header + sign-off

## Structure — 4 beats, 300–330 words, hard cap 370

### Beat 1 — The Hook (2–3 sentences)
Name the exact role. Pivot to ONE specific thing about THIS JD/company that made it worth writing
— "why this one caught my attention," not "why I'm applying." End asserting this is already how I
work.
- Stretch role (different type): name the transition honestly + why.
- Obvious fit: disarm it — "rather than tell you I check every box, let me show you the
  scale/discipline I check them at."
- JD emphasizes something specific (AI validation, data quality): make THAT the hook.
- NEVER open with "I am excited to apply for" / "I am writing to express interest."

### Beat 2 — One Story, Well Told (3–4 sentences)
The SINGLE most relevant achievement. Situation (what was broken/needed) → what I built → what
changed (the metric). Deep on one, never a list. Rotate the CENTERPIECE by role type — pull the
matching story from your `knowledge/`:
- Full-stack / automation role → your biggest automation win (the effort/time % you cut)
- Databricks / big-data role → your largest-scale pipeline (records/day, downstream consumers,
  incidents resolved)
- Data engineering role → a pipeline + data-quality / schema-validation story as the spine

### Beat 3 — The Differentiator (3–4 sentences)
The ONE asset that best proves the JD's most-emphasized SOFT requirement (not the core stack —
that's assumed). Frame it as JUDGMENT (the principle applied), not activity. Then one honest
sentence on the JD's named stack keywords; gaps as "comfortable picking up X quickly" — never fake
a skill. Choose the category by what the JD leans on:
- AI validation / responsible AI → your most rigorous AI or quality-gate project, framed as AI
  judgment (deterministic-first, human-in-the-loop, "the validation layer has the final say").
- Reliability / operational stability → your incident-RCA / SLA-ownership work, framed as ownership.
- ML / data science → your ML depth (model benchmarking, publications), framed as rigor.
- Cloud / architecture breadth → your broadest end-to-end or multi-cloud system, framed as
  end-to-end system thinking.
- Automation / efficiency → your friction-removal automation, framed as "automate the friction,
  own the outcome."

The RULE, not the asset: the memorable part is the JUDGMENT behind it, not the metric alone. The
DIFFERENTIATOR must be a DIFFERENT asset from the CENTERPIECE so it's not one story told twice.

### Beat 4 — Company-Specific Close (2–3 sentences)
ONE real, researched fact about the COMPANY tied to why it's the environment I want to build in.
Then a simple, warm one-line call to action + thanks.
- Derive the fact from the JD or known context. If none is genuinely known, use WebSearch for one
  concrete, specific fact — never a generic "industry leader" line. If still none, leave
  `[COMPANY FACT — verify]` for the user to fill. NEVER fabricate.

## Tone gates (also enforced by cover_letter_check.py)

BANNED buzzwords: leverage synergies, passionate about, results-driven, thrilled, dynamic
environment, cutting-edge, fast-paced, go-getter, team player, wheelhouse, "proven track record",
"hit the ground running", "wear many hats".
BANNED AI-tells: poetic/abstract openers; taglines that restate themselves; vague future-gesturing
("where engineering is headed", "in today's landscape"); em-dash rhythm for false gravitas;
tricolon padding (e.g. "secure, stable, and scalable" echoed back from the JD).
REQUIRED: short plain sentences; concrete nouns + real numbers; honest confidence (real skills
flat, gaps as "comfortable picking up X quickly"); never volunteer a JD gap unless immediately
closed with proof; enthusiasm through specificity, not exclamation marks; one story beats five
stats; 300–330 words, never over 370.

## Fill-in skeleton

```
Dear Hiring Manager,

I'm applying for the {{ROLE_TITLE}} role {{TEAM_OR_ORG_CONTEXT}}. {{HOOK: the one specific thing
about this JD/company that made it worth writing}}. {{One line: this is already how I work.}}

{{CENTERPIECE — situation → what I built → what changed, single most JD-relevant metric.}}

{{DIFFERENTIATOR — the ONE asset proving the JD's most-emphasized SOFT requirement (see Beat 3
selector), framed as the judgment behind it; then one honest sentence on the JD's named stack
keywords; gaps as "comfortable picking up X quickly".}}

{{COMPANY CLOSE — one real researched fact about {{COMPANY}} tied to why it's the environment I
want to build in.}} I'd welcome the chance to talk it through. Thank you for your consideration.

Sincerely,
<name / phone / email / linkedin from config.json>
```

## Per-job distinctness (multiple roles at one company)

Before writing, check sibling `jobs/<same-company*>/cover_letter.tex`. Vary the SPINE (transition /
responsible-AI / scale / data-quality) and rotate the centerpiece story + company fact so a
recruiter seeing several letters doesn't feel déjà vu.

## Steps

1. Copy `assets/cover_letter_template.tex` → `jobs/<folder>/cover_letter.tex`.
2. Fill the `{{ROLE TITLE}}` slot in the header and the four `{{BEAT ...}}` body markers per the
   beats above (the rest of the header is your config.json identity). LaTeX-escape any `& % $ # _`
   in prose. Keep the salutation and "Sincerely" sign-off intact.
3. Run: `bash scripts/cover_letter.sh <folder> <file_prefix>_CoverLetter_<Company>` — gates tone and
   length (cover_letter_check.py), truth (truth_check.py), then compiles the named PDF.
4. Fix any FAIL and re-run. Every number must trace to knowledge/masters — same rule as the resume.
