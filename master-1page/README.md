# Master Resumes — One-Time Setup

Two masters live in this repo:

- `master-1page/resume.tex` — the one-page version. **Every tailored resume starts as a copy of this file.**
- `master-full/resume.tex` — the extended version, no page limit. Extra bullets live here so tailoring can swap them in.

Both use [Jake's Resume template](https://github.com/jakegut/resume) — a clean,
ATS-friendly LaTeX layout recruiters already know.

## Setting up your master for the first time

1. **Put your content into the template.** Keep the LaTeX preamble (everything
   before `\begin{document}`) untouched — the pipeline hash-checks it and will
   refuse to compile a resume whose formatting drifted. Edit only what's between
   the `%----------SECTION----------` markers: heading, experience, skills,
   projects, education.

2. **Let the AI polish it.** These skills are available in Claude Code — use them
   in roughly this order:

   | Skill                    | What it does                                                        |
   | ------------------------ | ------------------------------------------------------------------- |
   | `resume-rewriter`        | Rewrites every bullet with Google's XYZ formula + metrics            |
   | `resume-bullet-refiner`  | Sharpens individual weak bullets (also used automatically in tailoring) |
   | `resume-diagnoser`       | Scans like an ATS would; ranks your top 5 fixes                      |
   | `resume-recruiter`       | Recruiter's-eye keyword research for your target role                |
   | `resume-hiring-manager`  | Mock interview against your own resume — great final stress test     |

   Full guide on when to use which: [../SKILLS.md](../SKILLS.md). Re-run the
   master loop every 2–3 months or when you switch target role type.

3. **Prompts that work well:**
   - *"Read knowledge/ and master-1page/resume.tex. Rewrite every bullet using resume-rewriter. Don't invent anything not in knowledge/."*
   - *"Run resume-diagnoser on master-1page/resume.tex and fix the top 5 issues."*
   - *"Which bullets in master-full are stronger than their master-1page versions? Recommend swaps."*

4. **Verify before you rely on it:**

   ```bash
   python3 scripts/quality_check.py master-1page/resume.tex
   bash scripts/compile.sh master-1page/resume.tex
   ```

   All checks should pass and the PDF should be exactly one page. Fix the master
   once and every tailored resume inherits the fix.

## Keeping masters healthy

- New skill, project, or metric → add it to `knowledge/` first, then work it into
  the masters when it's earned a permanent spot.
- The one-page master should stay at 475–600 words with 5+ metrics — the same
  bar every tailored copy is held to.
- Never hand-edit tailored copies back into the master; masters are the single
  source, copies are disposable.

## Optional: live PDF preview in VS Code

Install the **LaTeX Workshop** extension (`ext install James-Yu.latex-workshop`)
and add to `.vscode/settings.json`:

```json
{
  "latex-workshop.latex.autoBuild.run": "onSave",
  "latex-workshop.view.pdf.viewer": "tab",
  "latex-workshop.latex.outDir": "%DIR%"
}
```

Open a `.tex` file, press `Cmd+Alt+V` (mac) / `Ctrl+Alt+V`, and the PDF refreshes
on every save — including saves made by the AI. (This repo's Claude Code hook
also auto-compiles on every `.tex` edit, so the PDF is always fresh either way.)
