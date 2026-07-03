#!/bin/bash
# finish_job.sh <folder_name> <OutputName> <RoleTitle> — one-call job finalization.
# Gates: quality check, truth check (fabrication), compile, 1-page check,
# contact-info-in-PDF check, post-edit match score on extracted PDF text
# (what an ATS actually parses), regression vs master baseline, tracker row.

set -e
cd "$(dirname "$0")/.."

FOLDER=$1
OUTPUT_NAME=$2
ROLE=$3
if [ -z "$FOLDER" ] || [ -z "$OUTPUT_NAME" ] || [ -z "$ROLE" ]; then
  echo "Usage: ./finish_job.sh <folder_name> <OutputName> <RoleTitle>"
  echo "Example: ./finish_job.sh cloudpeak AlexMorgan_Resume_Cloudpeak_DataEngineer 'Data Engineer'"
  exit 1
fi

JOB_DIR="jobs/$FOLDER"
TEX="$JOB_DIR/resume.tex"
PDF="$JOB_DIR/$OUTPUT_NAME.pdf"
cfg() { python3 -c "import json;print(json.load(open('config.json'))['$1'])"; }
MASTER=$(cfg master)
EMAIL=$(cfg email)
PHONE=$(cfg phone)

# 1. Quality check — abort on FAIL
QC_OUT=$(python3 scripts/quality_check.py "$TEX")
echo "$QC_OUT"
if echo "$QC_OUT" | grep -q '\[FAIL\]'; then
  echo "ABORT: fix FAIL items before compiling."
  exit 1
fi

# 2. Truth check — abort on fabricated metrics
if ! python3 scripts/truth_check.py "$TEX"; then
  echo "ABORT: resolve fabricated metrics before compiling."
  exit 1
fi

# 3. Compile (latexmk output suppressed; log kept in job folder)
bash scripts/compile.sh "$TEX" "$OUTPUT_NAME" >/dev/null 2>&1
if [ ! -f "$PDF" ]; then
  echo "ABORT: compile failed — see $JOB_DIR/resume.log"
  exit 1
fi
echo "PDF Generated: $PDF"

# 4. One-page check (from latexmk log — no extra dependencies)
PAGES=$(grep -o 'Output written on .* (\([0-9]*\) page' "$JOB_DIR/resume.log" | grep -o '([0-9]*' | tr -d '(' | tail -1)
if command -v pdfinfo >/dev/null 2>&1; then
  PAGES=$(pdfinfo "$PDF" | awk '/^Pages:/ {print $2}')
fi
if [ "$PAGES" != "1" ]; then
  echo "ABORT: PDF is ${PAGES:-unknown} pages — must be 1. Trim content and recompile."
  exit 1
fi

# 5. Score what an ATS parses: extracted PDF text if pdftotext exists, else .tex
extract_score() { grep -o 'Match score: [0-9]*%' | head -1 | grep -o '[0-9]*'; }
BEFORE=$(python3 scripts/keyword_match.py "$JOB_DIR/jd.txt" "$MASTER" | extract_score)
SCORE_SRC="$TEX"
SCORE_LABEL=".tex source"
if command -v pdftotext >/dev/null 2>&1; then
  PDF_TXT="$JOB_DIR/.pdf_text.txt"
  pdftotext "$PDF" "$PDF_TXT"
  if [ ! -s "$PDF_TXT" ]; then
    echo "ABORT: pdftotext extracted no text — PDF is not ATS-readable."
    exit 1
  fi
  if ! grep -q "$EMAIL" "$PDF_TXT" || ! grep -q "$PHONE" "$PDF_TXT"; then
    echo "ABORT: email or phone missing from extracted PDF text."
    exit 1
  fi
  SCORE_SRC="$PDF_TXT"
  SCORE_LABEL="ATS-parsed PDF"
else
  echo "NOTE: pdftotext not installed (poppler) — scoring .tex; PDF text/contact checks skipped."
fi
AFTER=$(python3 scripts/keyword_match.py "$JOB_DIR/jd.txt" "$SCORE_SRC" | extract_score)
rm -f "$JOB_DIR/.pdf_text.txt"
echo "Match score ($SCORE_LABEL): master ${BEFORE}% -> tailored ${AFTER}%"
if [ -n "$BEFORE" ] && [ -n "$AFTER" ] && [ "$AFTER" -lt "$BEFORE" ]; then
  echo "ABORT: tailored score below master baseline — tailoring made it worse."
  exit 1
fi

# 6. Tracker row — before (master) and after (tailored) match scores
DATE=$(date +%Y-%m-%d)
echo "| $FOLDER | $ROLE | $DATE | ${BEFORE}% -> ${AFTER}% |  |  | Applied |" >> jobs/tracker.md
echo "Tracker updated: $FOLDER | $ROLE | $DATE | ${BEFORE}% -> ${AFTER}% | Applied"
