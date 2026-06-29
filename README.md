# Resume Autopilot — Claude Code Resume Tailoring Agent

> An automated, ATS-optimized resume tailoring system built on **Claude Code**. Paste a job
> description, get a tailored, quality-gated, one-page PDF — without hand-editing LaTeX.

![Claude Code](https://img.shields.io/badge/Claude%20Code-agent-7C3AED)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB)
![LaTeX](https://img.shields.io/badge/LaTeX-Jake's%20Resume-008080)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

This repo ships with a **fictional sample persona** ("Alex Morgan", a Data Engineer) so the whole
pipeline runs end-to-end out of the box and compiles to a real demo PDF. Swap in your own details
to make it yours.

---

## The problem

Tailoring a resume to each job posting is the single highest-leverage thing a job seeker can do for
ATS (applicant tracking system) match rates — and the most tedious. For every application you have to:

1. Read the JD and figure out which keywords it actually weights
2. Decide what to add, where, and what to cut to stay one page
3. Edit LaTeX without breaking the layout
4. Sanity-check metrics, buzzwords, length, and formatting
5. Recompile and track what you sent where

Doing this by hand for 20+ applications a week is unsustainable. Doing it with a naive "rewrite my
resume" LLM prompt burns tokens and produces inconsistent, often-fabricated output.

This repo is the engineered answer: a **deterministic-script-first, LLM-second** pipeline driven by a
Claude Code agent, with hard quality gates and a fixed LaTeX template that the agent is forbidden to
break.

---

## Demo

A fully-worked example ships in [`jobs/example_company/`](jobs/example_company/) — the persona's
resume tailored to a fictional **Cloudpeak — Data Engineer** posting:

| File | What it is |
|------|------------|
| [`jd.txt`](jobs/example_company/jd.txt) | The job description |
| [`analysis.md`](jobs/example_company/analysis.md) | Claude's full-mode tailoring strategy |
| [`resume.tex`](jobs/example_company/resume.tex) | The tailored LaTeX source |
| `AlexMorgan_Resume_Cloudpeak_DataEngineer.pdf` | The compiled one-page output |

The keyword script scored the master resume at **81%** against this JD; after the agent executed the
planned changes, the tailored resume scored **94%** — passing all quality gates and staying on one page.

```text
$ python scripts/keyword_match.py jobs/example_company/jd.txt master-1page/resume.tex

Match score: 81%  (26/32 known JD keywords)
MISSING from resume (6) — sorted by JD emphasis:
  - ci/cd ×2
  - kubernetes ×2
  - great expectations
  ...
ARCHETYPE: batch-DE
QUICK WINS — top 3 missing keywords by JD emphasis:
  → Add "ci/cd" to Skills > Programming & Tools (appears ×2 in JD)
  → Add "kubernetes" to Skills > Programming & Tools (appears ×2 in JD)
```

---

## How it works

```text
        ┌──────────────┐
  JD →  │ keyword_match│  deterministic, ZERO Claude tokens
        │     .py      │  → match %, missing keywords (ranked), archetype, quick wins
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  analysis.md │  Claude reads the script output (not the raw JD in quick mode)
        │ (quick/full) │  → a concrete, line-by-line "Planned Changes" list
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  resume.tex  │  Claude edits ONLY content — never the LaTeX preamble/spacing
        │  (tailored)  │  → reframes existing bullets, layers in missing keywords
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │quality_check │  hard gate: 5+ metrics, 0 buzzwords, 0 first-person,
        │     .py      │  2+ soft-skill signals, 500–600 words → must PASS
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │  compile.sh  │  latexmk → named one-page PDF
        └──────┬───────┘
               ▼
          tracker.md     append: company, role, date, match %, status
```

Three engineering ideas make this work better than "ask an LLM to rewrite my resume":

1. **A deterministic script runs *before* the LLM.** `keyword_match.py` does the keyword gap analysis
   with zero tokens — ranking missing keywords by JD emphasis, detecting the role archetype, and
   suggesting placements. Claude never wastes tokens computing what a regex can.

2. **Token-budgeted analysis modes.** `quick` mode (~150 tokens) reads only the script's pre-analysis
   block and writes the change list — ideal for 20+ applications/day. `full` mode (~600 tokens) reads
   the JD for soft-signal extraction on target companies. You choose the spend per application.

3. **Quality gates that block bad output.** `quality_check.py` fails the build if the resume has fewer
   than 5 metrics, any banned buzzword or first-person pronoun, or too few soft-skill signals. The
   agent must fix FAILs before it is allowed to compile — so "looks done" can't ship broken.

The LaTeX template (Jake's Resume) is treated as **immutable structure**: `CLAUDE.md` forbids the
agent from touching the documentclass, geometry, spacing, fonts, or commands. It may only change
content between `\begin{document}` and `\end{document}`. This is what keeps every output consistently
one page and ATS-parseable.

---

## The 5 skills

This repo doubles as an installable **Claude Code plugin** bundling five resume skills. Four are
research/coaching tools you run periodically on your master resume; one is a surgical bullet editor
used inside the per-application workflow.

| Skill | What it does | When to use |
|-------|--------------|-------------|
| `resume-diagnoser` | Simulates an ATS scan; flags auto-rejection risks and ranks the top 5 fixes | New master resume, or interview rate drops |
| `resume-recruiter` | Market-wide keyword intelligence for a role type; missing keywords + trending skills | Targeting a new role type |
| `resume-rewriter` | Rewrites every experience bullet with Google's XYZ formula, layering in keywords | Full master-resume overhaul |
| `resume-hiring-manager` | 30-min mock interview with scoring + hireability score + study plan | Night before a real interview |
| `resume-bullet-refiner` | Surgical single-bullet rewrites; asks for metrics instead of fabricating | Anytime a bullet feels weak |

See [`SKILLS.md`](SKILLS.md) for the full when-to-use-what guide, and
[`LINKEDIN_PLAYBOOK.md`](LINKEDIN_PLAYBOOK.md) for a bonus LinkedIn headline/About optimization guide.

---

## Install

### Option A — as a Claude Code plugin (recommended)

From inside Claude Code, add this repo as a plugin marketplace and install the toolkit:

```text
/plugin marketplace add your-username/resume-autopilot
/plugin install resume-autopilot@resume-autopilot-marketplace
```

(Replace `your-username/resume-autopilot` with the GitHub repo path once you've pushed it. You can
also point at a local clone: `/plugin marketplace add ./resume-autopilot`.)

The five skills are then available in any Claude Code session.

### Option B — manual copy

Skills are just `SKILL.md` files. Copy them into your personal skills directory:

```bash
cp -r skills/* ~/.claude/skills/
```

### Then clone the pipeline

```bash
git clone https://github.com/your-username/resume-autopilot.git
cd resume-autopilot
```

Open the folder in Claude Code and paste a job description to start tailoring.

---

## Quickstart — tailor a resume for a job

1. Open this repo in Claude Code.
2. Paste a job description and say e.g. *"full: tailor my resume for this Cloudpeak Data Engineer role."*
3. Claude runs the pipeline: saves the JD → runs `keyword_match.py` → writes `analysis.md` →
   copies the master → executes the planned changes → runs `quality_check.py` → compiles the PDF →
   updates `tracker.md`.
4. Find your tailored, one-page PDF in `jobs/<company>/`.

Prefer to drive the scripts yourself? They stand alone:

```bash
python scripts/keyword_match.py jobs/<company>/jd.txt master-1page/resume.tex
python scripts/quality_check.py jobs/<company>/resume.tex
bash   scripts/compile.sh        jobs/<company>/resume.tex YourName_Resume_<Company>_<Role>
```

---

## Repo structure

```text
resume-autopilot/
├── .claude-plugin/          # makes the repo an installable Claude Code plugin + marketplace
│   ├── plugin.json
│   └── marketplace.json
├── CLAUDE.md                # the agent's operating instructions — the per-application workflow
├── README.md                # you are here
├── SKILLS.md                # when-to-use-which-skill reference
├── LINKEDIN_PLAYBOOK.md     # bonus: LinkedIn headline + About optimization guide
├── skills/                  # the 5 resume skills (auto-loaded by the plugin)
│   └── resume-*/SKILL.md
├── scripts/
│   ├── keyword_match.py     # zero-token JD↔resume gap analysis (runs first)
│   ├── quality_check.py     # metrics / buzzword / soft-skill / length gate
│   └── compile.sh           # latexmk → named PDF
├── master-1page/resume.tex  # one-page master — tailor from here for most applications
├── master-full/resume.tex   # full master — no page limit
├── knowledge/               # source-of-truth content the agent pulls from
│   ├── skills.md  experience.md  projects.md  achievement_bank.md  certifications.md
├── jobs/
│   ├── tracker.md           # application log
│   ├── template_company/    # blank starting point — copy this per application
│   └── example_company/     # ← fully-worked demo (JD → analysis → tailored resume → PDF)
└── assets/jakes_resume.tex  # the upstream Jake's Resume template, for reference
```

**Why this shape:** the `knowledge/` base is the single source of truth so the agent never
fabricates — it reframes real content. The `master-*` files are the canonical resumes; each job gets
its own folder under `jobs/` so applications never collide and every tailored version is reproducible
from its `.tex`. The scripts are dependency-light and standalone so you can run the pipeline with or
without the agent.

---

## Make it yours

Replace the fictional **Alex Morgan** persona with your own:

1. **`master-1page/resume.tex`** and **`master-full/resume.tex`** — edit only the content between
   `\begin{document}` and `\end{document}` (heading, experience, skills, projects, education). Leave
   the preamble alone.
2. **`knowledge/`** — put your real roles, projects, achievements, and tech stack here. The agent
   reads these to make bullets specific and accurate.
3. **`CLAUDE.md`** — set the *Target role* line to the role you're applying for.
4. **The 5 skills** — open each `skills/resume-*/SKILL.md` and replace the
   `Default context — REPLACE with your own` block with your name, seniority, and stack.
5. **`.claude-plugin/plugin.json` + `marketplace.json`** — update the `author`/`owner` name and
   `homepage` to your GitHub repo.
6. Delete `jobs/example_company/` (or keep it as a reference) and clear the demo row from
   `jobs/tracker.md`.

---

## Prerequisites

- **Claude Code** — the agent runtime ([install guide](https://docs.claude.com/en/docs/claude-code))
- **A LaTeX toolchain** with `latexmk` (e.g. TeX Live or MacTeX) — for PDF compilation
- **Python 3.8+** — for the keyword and quality scripts (standard library only, no pip installs)

---

## Credits & License

- Resume layout: [Jake's Resume](https://github.com/jakegut/resume) (template, MIT).
- Everything else in this repo: MIT — see [`LICENSE`](LICENSE). Use it, fork it, make it yours.
