# Changelog

All notable changes to Resume Autopilot are documented here.

## [3.0.0] — 2026-07-26

The headline of v3 is **cover letter generation** — the plugin now bundles **six skills**.

### Added
- **New skill `resume-cover-letter`** — generates a tailored, one-page cover letter from the
  finalized resume's analysis + strongest bullets, following a four-beat pattern
  (hook → one story → differentiator → company close). Opt-in per role; it reuses the resume's
  analysis instead of re-deriving it.
- **Designed LaTeX template** `assets/cover_letter_template.tex` — a three-column header
  (contact / name + role / links), blue section accents, and a page footer, rendered in the
  same default font as the resume. Compiles to PDF with the existing `compile.sh`
  (**pdflatex — no extra fonts or xelatex**).
- **Tone gate** `scripts/cover_letter_check.py` — blocks banned buzzwords and canned AI-tell
  openers, and enforces word count (target 300–330, hard cap 370). First-person is allowed
  here (unlike the resume gate).
- **One-call finalizer** `scripts/cover_letter.sh` — tone gate → truth gate (`truth_check.py`,
  reused) → compiled PDF.
- **Opt-in workflow** — `CLAUDE.md` step 7 asks *"Want a cover letter for this role?"* after the
  resume passes; it never auto-generates per application.
- `config.json` gains a `linkedin` field for the letter header.

### Changed
- Plugin now advertises **six skills** (was five) — `plugin.json`, `marketplace.json`, `README.md`,
  and `SKILLS.md` updated accordingly.

## [2.0.0]

- Five resume skills (diagnoser, recruiter, rewriter, hiring-manager, bullet-refiner) and the
  script-first, LLM-second tailoring pipeline with hard quality/truth gates.
