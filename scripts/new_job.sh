#!/bin/bash
# new_job.sh <folder_name> — one-call job setup.
# Expects jobs/<folder_name>/jd.txt to already exist (save the JD there first).
# Creates the folder if needed, copies the 1-page master, runs keyword gap analysis.

set -e
cd "$(dirname "$0")/.."

FOLDER=$1
if [ -z "$FOLDER" ]; then
  echo "Usage: ./new_job.sh <folder_name>   (jd.txt must exist in jobs/<folder_name>/)"
  exit 1
fi

JOB_DIR="jobs/$FOLDER"
mkdir -p "$JOB_DIR"

if [ ! -f "$JOB_DIR/jd.txt" ]; then
  echo "ERROR: $JOB_DIR/jd.txt not found. Save the job description there first."
  exit 1
fi

cp master-1page/resume.tex "$JOB_DIR/resume.tex"
echo "Copied master-1page/resume.tex -> $JOB_DIR/resume.tex"

python3 scripts/keyword_match.py "$JOB_DIR/jd.txt" master-1page/resume.tex
