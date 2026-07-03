# Knowledge Base — Your Source of Truth

This folder holds the facts the AI is allowed to use about you. The truth check
(`scripts/truth_check.py`) blocks any metric in a tailored resume that can't be
traced back to these files or your masters — so **if it's not written here, it
can't go on your resume.** That's the feature, not a limitation: it's what keeps
the AI from inventing experience you'd have to defend in an interview.

## First-time setup (30–45 minutes, once)

Fill these five files with your real history. Be generous — more detail here
means sharper, more specific bullets later.

| File                  | What goes in it                                                        |
| --------------------- | ---------------------------------------------------------------------- |
| `skills.md`           | Every tool/language/platform you've genuinely used, grouped by category |
| `experience.md`       | Each role: company, dates, what you did, raw numbers and outcomes       |
| `projects.md`         | Side/school projects: stack, what it does, measurable results           |
| `certifications.md`   | Education, certifications, awards                                       |
| `achievement_bank.md` | Pre-written, quantified bullets ready to swap into any resume           |

## Tips that pay off

- **Numbers first.** Dig up the metrics now: records processed, % improved,
  hours saved, users served, dollars. A bullet without a number is a claim;
  with a number it's evidence. Estimates are fine — just be able to explain them.
- **Write ugly, write everything.** These files are never seen by recruiters.
  Raw bullet-point dumps beat polished paragraphs.
- **Update on the spot.** Shipped something? Got a metric in a sprint review?
  Add it the same day. Future-you tailoring at midnight will be grateful.
- **One easy way to start:** open Claude Code and say
  *"Interview me about my work history and write the answers into the knowledge/ files."*
  Answering questions is easier than staring at a blank file.

## How the pipeline uses this

- The AI checks these files (and its session memory) before rewriting any bullet,
  so tailored bullets stay specific and accurate.
- `truth_check.py` builds its whitelist from these files + both masters.
- Adding a new fact here immediately makes it available to every future resume.
