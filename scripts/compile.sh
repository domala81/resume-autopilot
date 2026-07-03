#!/bin/bash
# compile.sh <file.tex> [OutputName] — LaTeX -> PDF via latexmk.
# Compiles in the file's own directory (aux files stay local to it).
# With OutputName, renames the PDF to OutputName.pdf (no extension in arg).
# Used by finish_job.sh for the final named PDF; safe to run standalone.

FILE=$1
OUTPUT_NAME=$2  # optional: AlexMorgan_Resume_CompanyName_RoleTitle (no .pdf)

if [ -z "$FILE" ]; then
  echo "Usage: ./compile.sh path/to/resume.tex [OutputName]"
  echo "Example: ./compile.sh jobs/google/resume.tex AlexMorgan_Resume_Google_DataEngineer"
  exit 1
fi

DIR="$(cd "$(dirname "$FILE")" && pwd)"
BASE="$(basename "$FILE" .tex)"

cd "$DIR"

latexmk -pdf -interaction=nonstopmode "$(basename "$FILE")"

if [ -n "$OUTPUT_NAME" ]; then
  mv "${BASE}.pdf" "${OUTPUT_NAME}.pdf"
  echo "PDF Generated: ${DIR}/${OUTPUT_NAME}.pdf"
else
  echo "PDF Generated: ${DIR}/${BASE}.pdf"
fi
