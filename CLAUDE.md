# Resume Autopilot — Agent Instructions

Automated resume tailoring: JD in → tailored, ATS-optimized, one-page PDF out. You are a Resume Engineering Assistant. Full workflow detail lives in README.md; this file is the operating contract.

> **Customize me:** This template ships configured for **entry-to-mid-level Data & AI Engineer** roles, with a fictional sample persona ("Alex Morgan"). Replace the target role below, `config.json`, the master resumes, and the `knowledge/` files with your own details before using.

Target role: **[your target role — e.g. Data Engineer / AI Engineer]**

## File Rules

- Masters: `master-1page/resume.tex` (default source), `master-full/resume.tex` (no page limit).
- Never touch LaTeX formatting: documentclass, geometry, spacing, fonts, command definitions. Only edit content: bullets, skills, project descriptions.
- When editing any resume.tex, read from `\begin{document}` onward (~line 84) using the `%---SECTION---` markers. Never read the preamble.

## Workflow

1. Folder name: `jobs/<company>/`; if it exists, disambiguate with job ID (`_<job_id>`) or role slug (`_de`). Check `ls jobs/` first.
2. Save JD to `jobs/<folder>/jd.txt`, then run:
   `bash scripts/new_job.sh <folder>` — copies master into the folder and prints keyword gap analysis (match %, missing ranked by emphasis, archetype, quick wins, unknown terms).
3. Write `jobs/<folder>/analysis.md`. If no mode given, ask exactly:
   > **quick or full?**
   > `quick` — script pre-analysis only → Planned Changes (~150 tokens, 20+/day volume)
   > `full` — reads JD + qualitative analysis (~600 tokens, target companies)
   - **quick**: use script output only (do NOT read jd.txt); write only `## Planned Changes`.
   - **full**: read jd.txt too; cover missing-keyword placement, which `?` unknown terms are real tech vs noise, underweighted role emphasis, soft-skill signals, top-3 priorities by ATS impact; then `## Planned Changes`.
   - `## Planned Changes` = terse directives ("Experience bullet 3: add 'Airflow', reframe around orchestration"). No before/after bullet pairs, no re-listing keyword presence.
4. Edit `jobs/<folder>/resume.tex` executing `## Planned Changes` line by line:
   - Never invent experience — only reframe, reorder, or swap in existing bullets from masters.
   - Check `knowledge/` for role context (metrics, tech, outcomes) before writing.
   - Invoke `resume-bullet-refiner` skill when rewriting any bullet.
   - Then surface the strongest evidence: `python3 scripts/reorder_bullets.py jobs/<folder>/resume.tex jobs/<folder>/jd.txt` (dry-run, 0 tokens). Read the proposed order; if it doesn't break a role's narrative, re-run with `--apply`. Bullets marked `% pin` never move.
5. Finalize:
   `bash scripts/finish_job.sh <folder> <file_prefix>_<Company>_<RoleTitle> "<Role Title>"` (file_prefix from `config.json`, PascalCase, no spaces) — gates in order: quality check, truth check (aborts on metrics not traceable to masters/knowledge — never work around this by editing knowledge files; fix the resume), compile, 1-page check, contact-info-in-PDF check, match score on extracted PDF text with regression abort if below master, tracker row (folder name kept for disambiguation when ≠ company).
   Truth-check WARN terms: verify each is real experience before finalizing.
6. Full mode only (target companies): after finish_job passes, optionally run the `resume-diagnoser` skill on the tailored resume for a final recruiter-eye pass.
7. Cover letter (full mode, opt-in): after finish_job passes, ask exactly:
   > **Want a cover letter for this role? (y/n)**
   Generate only on yes — never auto-generate per application. On yes, invoke the `resume-cover-letter` skill: it fills `assets/cover_letter_template.tex` from `analysis.md` priorities + the resume's strongest bullets + `knowledge/`, then runs `bash scripts/cover_letter.sh <folder> <file_prefix>_CoverLetter_<Company>` (tone/length gate → truth gate → compiled PDF).

## Quality Checklist (enforced by scripts/quality_check.py)

- Metrics: 5+ measurable numbers (%, $, volume, time).
- Word count: 475–600.
- Soft skills: 2+ signaled in bullet context, not just skills section.
- Buzzwords: zero ("spearheaded," "passionate," "results-driven," "detail-oriented," "synergy," non-technical "leverage"); no I/my/me.

## Priority

1. ATS keyword match 2. Recruiter readability 3. Technical accuracy 4. One-page format
