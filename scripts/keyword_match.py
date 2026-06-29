#!/usr/bin/env python3
"""
keyword_match.py — JD-to-resume keyword gap analysis + pre-analysis for Claude

Usage:
  python keyword_match.py <jd_file> <resume_file>

Output:
  1. Match score + missing/present known keywords
  2. Unknown JD tech terms not in known list
  3. JD archetype (streaming-DE / batch-DE / ml-adjacent / cloud-infra-DE / analytics-DE)
  4. Quick wins — top 3 keyword placement suggestions for Claude
"""

import sys
import re
from collections import Counter

# Curated Data/AI/Cloud keyword list — 150+ terms
KNOWN_KEYWORDS = [
    # Languages
    "python", "sql", "scala", "java", "r", "bash", "go", "rust", "typescript", "javascript",
    # Big Data / Processing
    "spark", "pyspark", "hadoop", "hive", "flink", "kafka", "kinesis", "beam", "dbt",
    "databricks", "delta lake", "delta", "iceberg", "parquet", "avro", "orc",
    # Cloud — AWS
    "aws", "s3", "glue", "lambda", "redshift", "emr", "athena", "sagemaker", "step functions",
    "dynamodb", "sqs", "sns", "rds", "ec2", "ecs", "eks", "cloudwatch", "cloudformation",
    "cdk", "terraform", "iam",
    # Cloud — GCP
    "gcp", "bigquery", "dataflow", "dataproc", "pub/sub", "pubsub", "cloud run", "gke",
    "vertex ai", "vertex",
    # Cloud — Azure
    "azure", "azure data factory", "adf", "synapse", "azure databricks", "cosmos db",
    "azure functions", "ado",
    # Orchestration / Workflow
    "airflow", "prefect", "dagster", "luigi", "mage", "argo",
    # Databases
    "postgresql", "postgres", "mysql", "snowflake", "mongodb", "cassandra", "redis",
    "elasticsearch", "neo4j", "sqlite", "cockroachdb", "duckdb",
    # ML / AI
    "machine learning", "deep learning", "nlp", "llm", "rag", "langchain", "openai",
    "hugging face", "pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost",
    "lightgbm", "mlflow", "feature store", "vector database", "embeddings",
    "transformer", "bert", "gpt", "fine-tuning", "prompt engineering",
    # Data Engineering patterns
    "etl", "elt", "data pipeline", "data lake", "data lakehouse", "data warehouse",
    "data mesh", "data catalog", "data quality", "data lineage", "data governance",
    "streaming", "batch processing", "real-time", "cdc", "change data capture",
    "schema evolution", "schema registry",
    # DevOps / Infra
    "docker", "kubernetes", "k8s", "ci/cd", "github actions", "jenkins", "gitlab ci",
    "helm", "ansible", "git", "github", "gitlab",
    # APIs / Integration
    "rest", "restful", "graphql", "grpc", "api gateway", "fastapi", "flask", "django",
    # Soft / Process
    "agile", "scrum", "jira", "confluence", "stakeholder", "cross-functional",
    # BI / Visualization
    "tableau", "power bi", "looker", "quicksight", "grafana", "superset",
    # Testing
    "pytest", "unit testing", "integration testing", "data testing", "great expectations",
    # Monitoring
    "datadog", "new relic", "splunk", "prometheus", "alerting", "observability",
]

# Alias map — treat these as the same keyword
ALIASES = {
    "pyspark": ["spark"],
    "postgresql": ["postgres"],
    "scikit-learn": ["sklearn"],
    "pub/sub": ["pubsub"],
    "k8s": ["kubernetes"],
    "aws glue": ["glue"],
    "aws lambda": ["lambda"],
    "step functions": ["step functions", "stepfunctions"],
    "delta lake": ["delta"],
}

# Skills clusters from master resume — maps keywords to which section to add them
SKILLS_CLUSTERS = {
    "Programming & Tools": [
        "python", "sql", "bash", "go", "scala", "java", "rust", "typescript", "javascript",
        "git", "github", "gitlab", "docker", "terraform", "ansible", "helm", "cdk",
        "jenkins", "github actions", "gitlab ci", "ci/cd",
        "kubernetes", "k8s", "eks", "ecs", "ec2",
    ],
    "Databases": [
        "mysql", "snowflake", "mongodb", "postgresql", "postgres", "neo4j", "bigquery",
        "redis", "cassandra", "elasticsearch", "sqlite", "cockroachdb", "duckdb",
        "dynamodb", "rds",
    ],
    "Big Data & Visualization": [
        "spark", "pyspark", "hadoop", "hive", "flink", "kafka", "kinesis", "beam", "dbt",
        "databricks", "delta lake", "delta", "iceberg", "parquet", "avro", "orc",
        "airflow", "prefect", "dagster", "luigi", "mage", "argo",
        "streaming", "batch processing", "real-time", "etl", "elt",
        "data warehouse", "data lake", "data lakehouse", "data pipeline",
        "tableau", "power bi", "looker", "quicksight", "grafana", "superset",
        "datadog", "prometheus", "splunk", "observability",
    ],
    "ML & AI": [
        "machine learning", "deep learning", "nlp", "llm", "rag", "langchain", "openai",
        "hugging face", "pytorch", "tensorflow", "scikit-learn", "sklearn", "xgboost",
        "lightgbm", "mlflow", "feature store", "vector database", "embeddings",
        "transformer", "bert", "gpt", "fine-tuning", "prompt engineering",
        "sagemaker", "vertex ai", "vertex",
    ],
    "AWS Services": [
        "aws", "s3", "glue", "lambda", "redshift", "emr", "athena", "sagemaker",
        "step functions", "sqs", "sns", "ec2", "ecs", "eks", "cloudwatch",
        "cloudformation", "iam", "kinesis",
    ],
}

# Archetype definitions — keyword signals + weights
ARCHETYPES = {
    "streaming-DE": ["kafka", "kinesis", "flink", "real-time", "streaming", "cdc",
                     "change data capture", "pubsub", "pub/sub", "beam", "schema registry"],
    "batch-DE":     ["spark", "pyspark", "glue", "airflow", "etl", "elt", "dbt",
                     "batch processing", "hive", "hadoop", "emr", "dagster", "prefect"],
    "ml-adjacent":  ["sagemaker", "mlflow", "feature store", "machine learning", "pytorch",
                     "tensorflow", "llm", "rag", "vertex ai", "xgboost", "scikit-learn",
                     "embeddings", "fine-tuning"],
    "cloud-infra-DE": ["eks", "k8s", "kubernetes", "terraform", "cdk", "cloudformation",
                       "docker", "helm", "ecs", "ansible", "ci/cd", "github actions",
                       "cloudwatch", "observability"],
    "analytics-DE": ["dbt", "snowflake", "tableau", "power bi", "looker", "bigquery",
                     "duckdb", "quicksight", "superset", "grafana", "data warehouse",
                     "data lakehouse", "redshift"],
}

# Common English words to skip in free-form JD scan
COMMON_WORDS = {
    "the", "and", "with", "for", "that", "this", "are", "from", "have", "will",
    "your", "you", "our", "their", "they", "them", "not", "but", "can", "all",
    "use", "used", "using", "work", "working", "role", "team", "data", "new",
    "build", "built", "help", "strong", "good", "best", "well", "need", "must",
    "also", "able", "make", "into", "such", "both", "more", "most", "some",
    "has", "had", "its", "than", "each", "may", "one", "two", "three", "across",
    "within", "about", "other", "what", "how", "when", "where", "which",
    "key", "high", "large", "scale", "based", "level", "end", "systems",
    "experience", "skills", "knowledge", "understanding", "ability", "including",
    "requirements", "responsibilities", "preferred", "required", "plus", "etc",
    "year", "years", "time", "business", "product", "service", "customer",
    "ensure", "drive", "develop", "design", "implement", "manage", "support",
    "platform", "solution", "solutions", "environment", "process", "processes",
    "apache", "cloud", "engineer", "engineering", "software", "infrastructure",
    "application", "applications", "framework", "frameworks", "tools", "tool",
    "pipeline", "pipelines", "model", "models", "project", "projects",
    # Soft/behavioral words that slip past the tech filter
    "ownership", "familiarity", "mindset", "ability", "stakeholders",
    "collaborate", "collaboration", "cross-functionally", "communication",
    "motivated", "passion", "detail", "oriented", "driven", "focused",
    "responsible", "accountability", "proficiency", "proficient",
    "hands-on", "end-to-end", "fast-paced", "self-starter",
}


def normalize(text):
    return text.lower()


def count_keyword_frequency(jd_text, keywords):
    """Count how many times each keyword appears in the JD."""
    jd = normalize(jd_text)
    freq = {}
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        freq[kw] = len(re.findall(pattern, jd))
    return freq


def detect_archetype(jd_text, freq):
    """Score JD against archetype keyword sets, return top archetype with score."""
    jd = normalize(jd_text)
    scores = {}
    for archetype, signals in ARCHETYPES.items():
        score = 0
        for signal in signals:
            pattern = r'\b' + re.escape(signal) + r'\b'
            count = len(re.findall(pattern, jd))
            score += count
        scores[archetype] = score

    top = max(scores, key=scores.get)
    top_score = scores[top]

    # Build signal evidence string
    signals_found = []
    for signal in ARCHETYPES[top]:
        pattern = r'\b' + re.escape(signal) + r'\b'
        count = len(re.findall(pattern, jd))
        if count > 0:
            signals_found.append(f"{signal}×{count}")

    return top, top_score, signals_found[:5]


def keyword_to_cluster(kw):
    """Return which skills cluster a keyword belongs to."""
    for cluster, members in SKILLS_CLUSTERS.items():
        if kw in members:
            return cluster
    return "Skills (new cluster needed)"


def generate_quick_wins(missing, freq):
    """Top 3 highest-frequency missing keywords with placement suggestion."""
    if not missing:
        return []
    ranked = sorted(missing, key=lambda k: freq.get(k, 0), reverse=True)[:3]
    wins = []
    for kw in ranked:
        cluster = keyword_to_cluster(kw)
        f = freq.get(kw, 0)
        wins.append((kw, cluster, f))
    return wins


def extract_jd_keywords(jd_text):
    """Return set of curated keywords found in the JD."""
    jd = normalize(jd_text)
    found = set()
    for kw in KNOWN_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, jd):
            found.add(kw)
    return found


def check_resume(resume_text, keywords):
    """For each keyword, check if it (or an alias) appears in the resume."""
    resume = normalize(resume_text)
    present = set()
    missing = set()
    for kw in keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, resume):
            present.add(kw)
            continue
        aliases = ALIASES.get(kw, [])
        if any(re.search(r'\b' + re.escape(a) + r'\b', resume) for a in aliases):
            present.add(kw)
            continue
        missing.add(kw)
    return present, missing


def extract_unknown_jd_terms(jd_text, resume_text):
    """Extract tech-looking terms from JD not in KNOWN_KEYWORDS, check against resume."""
    known_set = set(KNOWN_KEYWORDS)
    resume_lower = resume_text.lower()

    all_tokens = re.findall(r'[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)*', jd_text)
    token_counts = Counter(t.lower() for t in all_tokens)

    candidates = set()
    for token in all_tokens:
        tl = token.lower()
        if tl in known_set or tl in COMMON_WORDS or len(tl) < 3:
            continue
        is_tech = (
            token[0].isupper()
            or token.isupper()
            or '-' in token
            or any(c.isdigit() for c in token)
        )
        if not is_tech and (len(tl) < 4 or token_counts[tl] < 3):
            continue
        candidates.add(tl)

    present = set()
    missing = set()
    for term in candidates:
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, resume_lower):
            present.add(term)
        else:
            missing.add(term)
    return present, missing


def main():
    if len(sys.argv) != 3:
        print("Usage: python keyword_match.py <jd_file> <resume_file>")
        sys.exit(1)

    jd_path, resume_path = sys.argv[1], sys.argv[2]

    try:
        jd_text = open(jd_path).read()
    except FileNotFoundError:
        print(f"ERROR: JD file not found: {jd_path}")
        sys.exit(1)

    try:
        resume_text = open(resume_path).read()
    except FileNotFoundError:
        print(f"ERROR: Resume file not found: {resume_path}")
        sys.exit(1)

    jd_keywords = extract_jd_keywords(jd_text)

    if not jd_keywords:
        print("No known keywords found in JD. Check the JD content or expand KNOWN_KEYWORDS.")
        sys.exit(0)

    present, missing = check_resume(resume_text, jd_keywords)
    match_pct = round(len(present) / len(jd_keywords) * 100)
    freq = count_keyword_frequency(jd_text, jd_keywords)
    archetype, arch_score, arch_signals = detect_archetype(jd_text, freq)
    quick_wins = generate_quick_wins(missing, freq)
    unknown_present, unknown_missing = extract_unknown_jd_terms(jd_text, resume_text)

    sep = "=" * 54

    # ── Section 1: Match score ──────────────────────────────
    print(f"\n{sep}")
    print(f"KEYWORD MATCH REPORT")
    print(f"JD: {jd_path}  |  Resume: {resume_path}")
    print(f"{sep}")
    print(f"\nMatch score: {match_pct}%  ({len(present)}/{len(jd_keywords)} known JD keywords)\n")

    if missing:
        # Sort missing by frequency (most emphasized first)
        missing_ranked = sorted(missing, key=lambda k: freq.get(k, 0), reverse=True)
        print(f"MISSING from resume ({len(missing)}) — sorted by JD emphasis:")
        for kw in missing_ranked:
            f = freq.get(kw, 0)
            marker = f" ×{f}" if f > 1 else ""
            print(f"  - {kw}{marker}")
    else:
        print("No missing known keywords — full coverage.")

    print(f"\nPresent in resume ({len(present)}):")
    for kw in sorted(present):
        f = freq.get(kw, 0)
        marker = f" ×{f}" if f > 1 else ""
        print(f"  + {kw}{marker}")

    # ── Section 2: Unknown JD terms ────────────────────────
    if unknown_missing:
        print(f"\nUNKNOWN JD TERMS — not in known list, missing from resume ({len(unknown_missing)}):")
        print("  (Claude: assess each — real tech worth adding vs noise)")
        for kw in sorted(unknown_missing):
            print(f"  ? {kw}")

    if unknown_present:
        print(f"\nUnknown JD terms already in resume ({len(unknown_present)}):")
        for kw in sorted(unknown_present):
            print(f"  ~ {kw}")

    # ── Section 3: Pre-analysis for Claude ─────────────────
    print(f"\n{sep}")
    print(f"PRE-ANALYSIS (read this instead of the full JD)")
    print(f"{sep}")

    signals_str = ", ".join(arch_signals) if arch_signals else "—"
    print(f"\nARCHETYPE: {archetype}  [{signals_str}]")

    if quick_wins:
        print(f"\nQUICK WINS — top {len(quick_wins)} missing keywords by JD emphasis:")
        for kw, cluster, f in quick_wins:
            freq_str = f" (appears ×{f} in JD)" if f > 0 else ""
            print(f"  → Add \"{kw}\" to Skills > {cluster}{freq_str}")

    print(f"\n{sep}")
    print("Claude: use PRE-ANALYSIS above to write analysis.md without re-reading the full JD.")
    print("For 'quick' mode: fill only ## Planned Changes from quick wins + missing list.")
    print("For 'full' mode: also read jd.txt for soft signal extraction.")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
