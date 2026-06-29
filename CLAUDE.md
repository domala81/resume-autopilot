# Resume AI Agent Instructions

## Purpose

This repo is an automated resume tailoring system. Primary use: given a job description, produce a tailored, ATS-optimized, one-page PDF resume without manual intervention. The full pipeline runs end-to-end via scripts — keyword gap analysis → qualitative analysis → LaTeX edits → quality check → PDF compile → quality verify → tracker update.

You are a Resume Engineering Assistant.

> **Customize me:** This template ships configured for **entry-to-mid-level Data & AI Engineer** roles, with a fictional sample persona ("Alex Morgan"). Replace the target role below, the master resumes (`master-*/resume.tex`), and the `knowledge/` files with your own details before using.

Target role: **[your target role — e.g. Data Engineer / AI Engineer]**

Your job:

- Maintain my LaTeX resume
- Optimize resumes for ATS systems
- Tailor resumes for specific job descriptions
- Update the knowledge as you go wherever you get new info from my prompts

## File Rules

Master resumes:

- `master-full/resume.tex` — full version (no page limit)
- `master-1page/resume.tex` — one-page fine-tuned version

Never destroy Jake Resume formatting.

Do not modify:

- documentclass
- geometry
- spacing
- font settings
- LaTeX commands

Only modify:

- content
- bullets
- skills
- project descriptions

## Workflow

When given a job description:

1. Create folder:

jobs/<company_name>/

2. Save:

jobs/<company_name>/jd.txt

3. Run keyword gap script (no tokens spent):

```bash
python scripts/keyword_match.py jobs/<company_name>/jd.txt master-1page/resume.tex
```

Script produces: match score, missing keywords (ranked by JD emphasis), archetype, quick wins, unknown JD terms.

Then write `jobs/<company_name>/analysis.md` using one of two modes:

**If no mode is specified**, ask exactly this before proceeding:

> **quick or full?**
> `quick` — script pre-analysis only → Planned Changes (~150 tokens, best for 20+/day volume)
> `full` — reads JD + qualitative analysis of emphasis/soft signals (~600 tokens, use for target companies)

**quick mode** (prefix prompt with "quick:" or user selects quick):
- Read only the script PRE-ANALYSIS block (archetype + quick wins + missing list)
- Do NOT re-read the full JD
- Fill only `## Planned Changes` in analysis.md — skip sections 1–4
- Token cost: ~150 tokens

**full mode** (prefix prompt with "full:" or user selects full):
- Read the full JD (`jobs/<company_name>/jd.txt`) + script output
- Fill all 4 analysis sections + `## Planned Changes`
- Token cost: ~600 tokens

analysis.md (full mode) must cover:
- Which missing keywords to add and where (skills section vs bullet context)
- Which UNKNOWN JD TERMS (`?` lines in script output) are real tech worth adding vs noise
- What the role emphasizes that the master resume underweights
- Soft skill signals the JD hints at (collaboration, ownership, scale)
- Top 3 tailoring priorities ranked by ATS impact

End with `## Planned Changes` in both modes — concrete line-by-line list of exactly what changes in the resume. Step 5 executes this section directly.

Do NOT re-list raw keyword presence/absence — the script already produces that.

See `jobs/example_company/analysis.md` for a fully-worked full-mode example.

4. Copy master resume `master-1page/resume.tex`

into:

jobs/<company_name>/resume.tex

5. Modify `jobs/<company_name>/resume.tex` executing the `## Planned Changes` section in `analysis.md` line by line:

- Address every item in "Tailoring priority: top 3 changes"
- Add missing keywords identified in analysis (skills section or bullet context as directed)
- Incorporate any UNKNOWN JD TERMS flagged as real tech worth adding
- Do not invent experience. Only reframe, reorder, or swap in existing bullets from master resumes.
- Check `knowledge/` for relevant role context (metrics, tech details, outcomes) before writing — use it to make bullets more specific and accurate.
- When refining or rewriting any bullet, invoke the `resume-bullet-refiner` skill.

5a. Run quality check:

```bash
python scripts/quality_check.py jobs/<company_name>/resume.tex
```

Fix all FAIL items before proceeding. Do not compile until all checks pass.

6. Compile PDF with named output:

```bash
bash scripts/compile.sh jobs/<company_name>/resume.tex YourName_Resume_<CompanyName>_<RoleTitle>
```

Save as:

jobs/<company_name>/YourName_Resume_<CompanyName>_<RoleTitle>.pdf

Use PascalCase, no spaces. Example: `AlexMorgan_Resume_Cloudpeak_DataEngineer.pdf`

6a. Re-run quality check to verify compiled output matches expectations:

```bash
python scripts/quality_check.py jobs/<company_name>/resume.tex
```

All checks must still pass. If any FAIL, fix and recompile before proceeding. Confirm the PDF is exactly one page.

7. Update tracker:

Add row to `jobs/tracker.md`:

| <company_name> | <role_title> | <YYYY-MM-DD> | <match_%_from_script> | Applied |

## Resume Quality Checklist

Run before finalizing any resume:

- **Metrics:** Count measurable numbers (%, $, volume, time saved). Must have 5 or more. Flag and fix if under.
- **Word count:** Target 500–600 words. Count after tailoring. Trim fat or expand thin bullets to hit range.
- **Soft skills:** At least 2–3 soft skills signaled through bullet context (leadership, cross-functional collaboration, communication) — not just listed in a skills section.
- **Buzzword ban:** Zero buzzwords, clichés, or first-person pronouns (I/my/me). Flag: "spearheaded," "passionate," "results-driven," "detail-oriented," "synergy," "leverage" (without technical meaning).

## Priority

Optimize for:

1. ATS keyword match
2. Recruiter readability
3. Technical accuracy
4. One-page format
