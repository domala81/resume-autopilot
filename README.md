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

> **Why this exists:** sharing is caring. Job hunting is exhausting enough without spending an hour
> tweaking your resume for every posting. If tech can make that easier, everyone should have it —
> so here it is. Use it, fork it, pass it on.

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
        │quality_check │  hard gate: 5+ metrics, 0 buzzwords, 0 first-person, 2+ soft-skill
        │     .py      │  signals, no duplicate bullets, LaTeX preamble untouched → must PASS
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │ truth_check  │  fabrication gate: every number must be traceable to your
        │     .py      │  masters/knowledge base — a made-up metric blocks the build
        └──────┬───────┘
               ▼
        ┌──────────────┐
        │finish_job.sh │  latexmk → named PDF → 1-page gate → re-score the EXTRACTED
        │              │  PDF text (what an ATS parses) → abort if worse than master
        └──────┬───────┘
               ▼
          tracker.md     append: company, role, date, match % (master -> tailored),
                         response, interview, status
```

Three engineering ideas make this work better than "ask an LLM to rewrite my resume":

1. **A deterministic script runs *before* the LLM.** `keyword_match.py` does the keyword gap analysis
   with zero tokens — ranking missing keywords by JD emphasis, detecting the role archetype, and
   suggesting placements. Claude never wastes tokens computing what a regex can.

2. **Token-budgeted analysis modes.** `quick` mode (~150 tokens) reads only the script's pre-analysis
   block and writes the change list — ideal for 20+ applications/day. `full` mode (~600 tokens) reads
   the JD for soft-signal extraction on target companies. You choose the spend per application.

3. **Quality gates that block bad output.** `quality_check.py` fails the build if the resume has fewer
   than 5 metrics, any banned buzzword or first-person pronoun, too few soft-skill signals, duplicate
   bullets, or a modified LaTeX preamble (hash-checked against the master). The agent must fix FAILs
   before it is allowed to compile — so "looks done" can't ship broken.

4. **It can't lie for you.** `truth_check.py` compares every number in the tailored resume against
   your masters and `knowledge/` files. A fabricated metric is an interview you'll fail — so it's a
   hard block, not a warning.

5. **It scores what recruiters' software actually sees.** The final match score runs against text
   extracted from the compiled PDF (the thing an ATS parses), not your source file — and the build
   aborts if tailoring somehow made the score worse than the master.

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

See [`SKILLS.md`](SKILLS.md) for the full when-to-use-what guide.

---

## Install

### Option A — as a Claude Code plugin (recommended)

From inside Claude Code, add this repo as a plugin marketplace and install the toolkit:

```text
/plugin marketplace add domala81/resume-autopilot
/plugin install resume-autopilot@resume-autopilot-marketplace
```

(You can also point at a local clone: `/plugin marketplace add ./resume-autopilot`.)

The five skills are then available in any Claude Code session.

### Option B — manual copy

Skills are just `SKILL.md` files. Copy them into your personal skills directory:

```bash
cp -r skills/* ~/.claude/skills/
```

### Then clone the pipeline

```bash
git clone https://github.com/domala81/resume-autopilot.git
cd resume-autopilot
```

Open the folder in Claude Code and paste a job description to start tailoring.

---

## Quickstart — tailor a resume for a job

> **First, strengthen your master.** Your master resume is the ceiling: tailoring can only
> polish it, never fix it. Run the master loop in [SKILLS.md](SKILLS.md)
> (diagnoser → recruiter → rewriter → bullet-refiner) before tailoring anything, and again
> every 2–3 months.

1. Open this repo in Claude Code.
2. Paste a job description and say e.g. *"full: tailor my resume for this Cloudpeak Data Engineer role."*
3. Claude runs the pipeline: saves the JD → runs `keyword_match.py` → writes `analysis.md` →
   copies the master → executes the planned changes → runs `quality_check.py` → compiles the PDF →
   updates `tracker.md`.
4. Find your tailored, one-page PDF in `jobs/<company>/`.

Prefer to drive the scripts yourself? Two calls run the whole pipeline:

```bash
# save the JD to jobs/<company>/jd.txt first, then:
bash scripts/new_job.sh    <company>                                          # setup + gap analysis
# ...edit jobs/<company>/resume.tex (or let Claude do it)...
bash scripts/finish_job.sh <company> YourName_Resume_<Company>_<Role> "<Role>" # all gates + PDF + tracker
```

Each underlying script also stands alone (`keyword_match.py`, `quality_check.py`, `truth_check.py`,
`compile.sh`) — see the table in each script's header.

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
├── skills/                  # the 5 resume skills (auto-loaded by the plugin)
│   └── resume-*/SKILL.md
├── config.json              # your identity + paths — edit this first
├── keywords/                # keyword data per role type (JSON, swappable) + guide
├── scripts/
│   ├── new_job.sh              # one call: job folder + master copy + gap analysis
│   ├── finish_job.sh           # one call: every gate → named PDF → tracker row
│   ├── keyword_match.py        # zero-token JD↔resume gap analysis
│   ├── quality_check.py        # metrics / buzzword / soft-skill / preamble / duplicate gate
│   ├── truth_check.py          # fabrication gate — blocks untraceable metrics
│   └── compile.sh              # latexmk → named PDF
├── master-1page/            # one-page master + first-time setup guide (README)
├── master-full/resume.tex   # full master — no page limit
├── knowledge/               # source-of-truth content the agent pulls from (+ setup README)
│   ├── skills.md  experience.md  projects.md  achievement_bank.md  certifications.md
├── jobs/                    # one folder per application (+ how-it-flows README)
│   ├── tracker.md           # application log: match delta, response, interview
│   ├── template_company/    # blank starting point
│   └── example_company/     # ← fully-worked demo (JD → analysis → tailored resume → PDF)
└── assets/jakes_resume.tex  # the upstream Jake's Resume template, for reference
```

New here? Follow the setup guides in order: [`master-1page/README.md`](master-1page/README.md) →
[`knowledge/README.md`](knowledge/README.md) → [`jobs/README.md`](jobs/README.md). Different career?
[`keywords/README.md`](keywords/README.md).

**Why this shape:** the `knowledge/` base is the single source of truth so the agent never
fabricates — it reframes real content. The `master-*` files are the canonical resumes; each job gets
its own folder under `jobs/` so applications never collide and every tailored version is reproducible
from its `.tex`. The scripts are dependency-light and standalone so you can run the pipeline with or
without the agent.

---

## Make it yours

Replace the fictional **Alex Morgan** persona with your own:

1. **`config.json`** — your name, email, phone, and output filename prefix. The truth check,
   PDF contact check, and finish script all read from here.
2. **`master-1page/resume.tex`** and **`master-full/resume.tex`** — edit only the content between
   `\begin{document}` and `\end{document}`. Leave the preamble alone — it's hash-checked, and a
   drifted preamble fails the build. Full guide: [`master-1page/README.md`](master-1page/README.md).
3. **`knowledge/`** — put your real roles, projects, achievements, and metrics here. The truth check
   only allows numbers it can trace to these files, so **if it's not written here, it can't go on
   your resume.** Guide: [`knowledge/README.md`](knowledge/README.md).
4. **`CLAUDE.md`** — set the *Target role* line to the role you're applying for.
5. **The 5 skills** — open each `skills/resume-*/SKILL.md` and replace the
   `Default context — REPLACE with your own` block with your name, seniority, and stack.
6. **The keyword bank** — `keywords/data-eng.json` is tuned for Data / AI / Cloud roles. Different
   field? Copy it, edit five JSON keys, point `config.json` at your file — no code changes.
   Guide: [`keywords/README.md`](keywords/README.md).
7. Delete `jobs/example_company/` (or keep it as a reference) and clear the demo row from
   `jobs/tracker.md`.

---

## Prerequisites

- **Claude Code** — the agent runtime ([install guide](https://docs.claude.com/en/docs/claude-code))
- **A LaTeX toolchain** with `latexmk` — for PDF compilation. Quick install:
  - macOS: `brew install --cask mactex-no-gui` (or the smaller `basictex`)
  - Debian/Ubuntu: `sudo apt-get install texlive-latex-extra latexmk`
  - Windows: install [MiKTeX](https://miktex.org) (bundles `latexmk`)
- **Python 3.8+** — for the keyword and quality scripts (standard library only, no pip installs)
- **poppler** *(optional but recommended)* — enables the PDF-text ATS checks
  (`brew install poppler` / `apt-get install poppler-utils`). Without it the pipeline still runs,
  scoring the `.tex` source instead of the extracted PDF text.

---

## Credits & License

- Resume layout: [Jake's Resume](https://github.com/jakegut/resume) (template, MIT).
- Everything else in this repo: MIT — see [`LICENSE`](LICENSE). Use it, fork it, make it yours.
