# Resume Skills — Quick Reference

---

## When to Use What

```
MASTER RESUME LOOP (run every 2-3 months or when switching target role type)
  1. /resume-diagnoser    → ATS audit, top 5 fixes
  2. /resume-recruiter    → market-wide keywords for role type (not per-company)
  3. /resume-rewriter     → full bullet overhaul with keyword layering
  4. /resume-bullet-refiner → surgical fixes on remaining weak bullets

PER-APPLICATION LOOP (CLAUDE.md workflow)
  1. keyword_match.py     → fast JD-to-resume gap (no Claude tokens)
  2. Claude: analysis.md  → qualitative tailoring strategy only
  3. Tailor resume.tex    → add missing keywords, adjust framing
  4. /resume-bullet-refiner → optional: sharpen any new bullets added
  5. compile.sh           → PDF

INTERVIEW PREP (standalone, night before)
  /resume-hiring-manager  → 30-min mock interview, hireability score, study plan

BULLET QUALITY (anytime, no JD needed)
  /resume-bullet-refiner  → single bullets, surgical, asks for metrics
```

---

## 1. Diagnoser

**Trigger phrases:** `diagnose my resume` · `audit my resume` · `why isn't my resume getting interviews`

**What it does:** Simulates a real ATS scan. Flags auto-rejection risks (tables, columns, graphics, bad formatting), weak bullets, missing signals per section. Returns top 5 fixes ranked by impact with before/after.

**Use when:**
- Starting fresh with a new master resume
- Interview rate drops and you don't know why
- Haven't run it in 2+ months

**Do NOT use when:**
- You already know what's wrong (use bullet-refiner or rewriter directly)
- Per-application tailoring (overkill — use CLAUDE.md workflow)

**Token cost:** Medium — single structured pass.

**What to paste:**
```
diagnose my resume for [Data Engineer / Cloud Engineer / AI Engineer]

[paste resume as plain text — not PDF, not .tex]
```

**Caveats:**
- Entry-level (<2 yrs exp): it won't flag missing summary section — that's intentional, summaries waste space at your level
- Output is diagnosis only — it won't rewrite bullets. Run rewriter or bullet-refiner after

---

## 2. Recruiter

**Trigger phrases:** `find missing keywords in my resume` · `what keywords should I have for [role]` · `act as a recruiter`

**What it does:** Simulates market-wide keyword intelligence across live JDs for a role type. Returns top 15 keywords ranked by frequency, what's missing from your resume, trending 2026 skills others aren't including, buzzwords to cut, and a ranked action list.

**Use when:**
- Updating master resume to target a new role type (e.g., pivoting from data engineering to ML engineering)
- Haven't refreshed keyword alignment in 3+ months
- Want to know what the market cares about, not just one JD

**Do NOT use when:**
- Per-application (this is market-wide, not JD-specific — use `keyword_match.py` for that)
- You already have the keywords from a prior run and just need to rewrite bullets (go straight to rewriter)

**Token cost:** Medium-high — full structured market analysis.

**Important limitation:** Uses Claude's training knowledge of the market, not live job postings. Can lag 3-6 months on very new tooling (e.g., a framework that emerged this quarter). For cutting-edge stack trends, verify manually.

**What to paste:**
```
find missing keywords in my resume for [role] at [company type: FAANG / fintech / startup / consulting]

[paste resume as plain text]
```

**Save the output** — paste the missing keywords list into the Rewriter in step 3.

---

## 3. Rewriter

**Trigger phrases:** `rewrite my resume bullets` · `XYZ my resume` · `make my resume bullets stronger`

**What it does:** Rewrites EVERY bullet in the experience section using Google's XYZ formula:
> "Accomplished [X] as measured by [Y], by doing [Z]."

Layers in missing keywords from Recruiter output. Returns before/after for top 5 highest-impact bullets.

**Use when:**
- Master resume needs a full overhaul (e.g., updating from intern/student bullets to FTE bullets)
- Running the full master resume loop (after Diagnoser + Recruiter)
- Bullet quality is broadly weak across the whole experience section

**Do NOT use when:**
- Per-application tailoring (too aggressive — rewrites everything, not just what needs to change)
- Only a few bullets are weak (use bullet-refiner instead — cheaper, surgical)

**Token cost:** High — full experience section in + full rewrite out.

**What to paste:**
```
rewrite my resume bullets for [role]

Missing keywords to layer in: [paste from Recruiter output]

Experience section:
[paste all experience bullets]
```

**Caveats:**
- It WILL ask for metrics on unquantified bullets — be ready to supply them
- Anything it can't verify gets flagged `[estimate, verify before sending]` — don't let those slip through
- Run bullet-refiner after to clean up any bullets you're still not happy with

---

## 4. Hiring Manager

**Trigger phrases:** `interview me for [role]` · `mock interview for [role]` · `practice interview`

**What it does:** Runs a realistic 30-min mock interview — 5 technical/role-specific questions + 3 STAR behavioral questions, one at a time. Scores each answer out of 10 with exact feedback. Ends with hireability score out of 100, 3 weakest answers, 3 questions to rehearse, and a gap study plan.

**Use when:**
- Night before a real interview
- Want to test how well your resume experience translates to verbal answers
- Haven't interviewed in a while and need calibration

**Do NOT use when:**
- You want resume edits — this is interview prep only, zero overlap with resume pipeline
- Early in the application process — save it for when you have an actual interview scheduled

**Token cost:** High — full back-and-forth conversation, but you get what you pay for.

**What to paste:**
```
interview me for [Cloud Engineer / Data Engineer / AI Engineer] at [Fortune 500 fintech / startup / FAANG / etc]

[paste resume as plain text]
```

**Rules:**
- Answer as you would in a real interview — don't over-explain
- It pushes back on vague answers like a real interviewer would
- Feedback is harsh by design — take it seriously

---

## 5. Bullet Refiner

**Trigger phrases:** `refine my bullets` · `strengthen this bullet` · `improve this resume point`

**What it does:** Rewrites individual bullets (one or several) using Google's XYZ formula. No JD or keywords needed. If a bullet has no metric, asks for specific data points (runtime, record count, error rate, scale) before rewriting. Falls back to scale/scope/comparative language when no metrics exist.

**Use when:**
- Any time a bullet feels weak, vague, or generic — master or tailored resume
- After per-application tailoring to check any new bullets you added
- After Rewriter, for surgical cleanup on bullets that still aren't tight
- Improving master resume quality without doing a full overhaul

**Do NOT use when:**
- You need keyword layering (use Rewriter — bullet-refiner ignores JD keywords)
- The whole experience section needs a rewrite (use Rewriter — more efficient)

**Token cost:** Low — tiny context per bullet.

**What to paste:**
```
refine my resume bullets

[paste one bullet or several, one per line]
```

**Caveats:**
- It won't write to any file until you explicitly confirm — shows refined bullet first, then stops
- "yes" / "apply" / "looks good" = triggers file write
- Difference from Rewriter: no keyword layering, no JD required, interactive metric prompts, one bullet at a time

---

## Per-Application Workflow (CLAUDE.md)

For each job application, paste the JD directly. Claude runs:

```
jobs/<company_name>/
  jd.txt          ← job description saved
  keyword_match   ← script: python scripts/keyword_match.py jd.txt master-1page/resume.tex
  analysis.md     ← qualitative tailoring strategy (not raw keyword list — script handles that)
  resume.tex      ← tailored from master-1page/
  resume.pdf      ← compiled output
```

Skills are for **master resume improvement** and **interview prep** — not per-application tailoring.

---

## Files

| File | Purpose |
|------|---------|
| `master-1page/resume.tex` | One-page source of truth — tailor from here for most applications |
| `master-full/resume.tex` | Full version — no page limit |
| `scripts/keyword_match.py` | JD-to-resume gap script — run before analysis.md, no tokens |
| `scripts/compile.sh` | Compile .tex to PDF via pdflatex |
| `knowledge/experience.md` | Raw experience bullets |
| `knowledge/skills.md` | Full tech stack |
| `knowledge/projects.md` | Project details |
| `knowledge/achievement_bank.md` | Metrics and wins |
| `assets/jakes_resume.tex` | Jake's template reference — do not modify |
