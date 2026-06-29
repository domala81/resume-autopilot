#!/bin/bash

FILE=$1
OUTPUT_NAME=$2  # optional: YourName_Resume_CompanyName_RoleTitle (no .pdf)

if [ -z "$FILE" ]; then
  echo "Usage: ./compile.sh path/to/resume.tex [OutputName]"
  echo "Example: ./compile.sh jobs/cloudpeak/resume.tex AlexMorgan_Resume_Cloudpeak_DataEngineer"
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
