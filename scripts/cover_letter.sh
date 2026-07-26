#!/bin/bash
# cover_letter.sh <folder> [OutputName] — one-call cover-letter finalization.
# Gates in order: tone/length check, truth check (fabrication), compile -> PDF.
# Expects jobs/<folder>/cover_letter.tex to already exist (written by the
# resume-cover-letter skill from assets/cover_letter_template.tex).

set -e
cd "$(dirname "$0")/.."

FOLDER=$1
OUTPUT_NAME=$2   # optional: e.g. YourName_CoverLetter_Company (no .pdf). Defaults to cover_letter.
if [ -z "$FOLDER" ]; then
  echo "Usage: ./cover_letter.sh <folder> [OutputName]"
  echo "Example: ./cover_letter.sh acme YourName_CoverLetter_Acme"
  exit 1
fi

JOB_DIR="jobs/$FOLDER"
TEX="$JOB_DIR/cover_letter.tex"
PDF="$JOB_DIR/${OUTPUT_NAME:-cover_letter}.pdf"

if [ ! -f "$TEX" ]; then
  echo "ERROR: $TEX not found. Generate the cover letter first (resume-cover-letter skill)."
  exit 1
fi

# 1. Tone + length gate — abort on FAIL
if ! python3 scripts/cover_letter_check.py "$TEX"; then
  echo "ABORT: fix cover-letter tone/length FAILs before compiling."
  exit 1
fi

# 2. Truth check — every number must trace to masters/knowledge (same gate as the resume)
if ! python3 scripts/truth_check.py "$TEX"; then
  echo "ABORT: resolve fabricated metrics before compiling."
  exit 1
fi

# 3. Compile -> named PDF (rename only when an OutputName is given)
if [ -n "$OUTPUT_NAME" ]; then
  bash scripts/compile.sh "$TEX" "$OUTPUT_NAME" >/dev/null 2>&1
else
  bash scripts/compile.sh "$TEX" >/dev/null 2>&1
fi
if [ ! -f "$PDF" ]; then
  echo "ABORT: compile failed — see $JOB_DIR/cover_letter.log"
  exit 1
fi
echo "Cover letter PDF generated: $PDF"
