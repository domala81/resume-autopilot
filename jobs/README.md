# Jobs — One Folder Per Application

Every application gets its own folder. Nothing is overwritten; you can always
look back at exactly what you sent where.

## Anatomy of a job folder

```
jobs/acme/
├── jd.txt          the job description you pasted (raw)
├── analysis.md     keyword gaps + planned changes (the AI's work order)
├── resume.tex      tailored copy of the master
└── AlexMorgan_Resume_Acme_DataEngineer.pdf   what you actually submit
```

Folder naming: company name, lowercase (`jobs/acme/`). Applying twice to the
same company? Disambiguate with the job ID or role: `jobs/acme_123456/`,
`jobs/acme_swe/`.

## The flow (mostly automatic)

1. Save the JD to `jobs/<folder>/jd.txt`, then:
   ```bash
   bash scripts/new_job.sh <folder>
   ```
2. The AI writes `analysis.md` (you pick `quick` or `full`), edits `resume.tex`.
3. Finalize:
   ```bash
   bash scripts/finish_job.sh <folder> <OutputName> "<Role Title>"
   ```
   This runs every gate (quality, truth, compile, one page, PDF text, score
   regression) and appends a row to the tracker. If it aborts, it tells you
   exactly why — fix and rerun.

## tracker.md — where the learning happens

| Column | Fill it in when |
| ------ | --------------- |
| Match % (master -> tailored) | automatic |
| Response | you hear back (or mark `—` after ~3 weeks of silence) |
| Interview | you get one |
| Status | Applied → Screening → Interview → Offer / Rejected |

Keep Response and Interview honest and current. After 30–50 applications the
tracker answers the only question that matters: **which match scores and role
types actually get callbacks** — and that tells you where to aim next.
