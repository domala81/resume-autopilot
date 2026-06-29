# Analysis — Cloudpeak (Data Engineer, Data Platform)

> **Mode:** full | **Match:** 81% (26/32 known keywords) | **Archetype:** batch-DE
>
> Script already produced match score, missing keywords, archetype, and quick wins.
> This file adds qualitative judgment on top. Raw keyword presence is NOT re-listed here.

## 1. Keyword Placement

| Keyword | Add Where | How |
|---------|-----------|-----|
| CI/CD | Skills > Programming & Tools | Append after GitHub Actions; also weave into Lambda tooling bullet |
| Kubernetes | Skills > Programming & Tools | Append after Docker |
| ELT | Bullet context | Reframe the BlueOrbit "ETL" bullet to "ELT" (dbt-in-warehouse is ELT) |
| data warehouse | Bullet context | Name the Snowflake target as a "data warehouse" in the BlueOrbit bullet |
| Great Expectations | Skills > Big Data & Visualization | Real data-quality framework (JD "nice to have"); add and reference in a bullet |
| Fivetran | Skills > Big Data & Visualization | Real managed-ingestion tool (JD "nice to have"); safe to add |

Skipped: `dagster` (Airflow already covers orchestration — adding an unused tool would be padding).

## 2. Role Emphasis vs Master Resume

- **Overweighted in JD:** real-time streaming (Kafka + Spark Structured Streaming), data quality/observability, end-to-end ownership of data products. Master already covers all three — surface them harder.
- **Underweighted in master:** containerized/Kubernetes deployment and explicit CI/CD ownership. Both are listed-skill gaps, not experience gaps.
- **Neutral / already covered:** Python, SQL, PySpark/Spark, Airflow, dbt, Snowflake, AWS (Glue/Lambda/S3/EMR/Step Functions), Terraform.

## 3. Soft Skill Signals

- **Collaboration:** JD repeats "partner closely with analytics, ML, and product teams." Master already signals this ("coordinating requirements with downstream teams") — keep and surface.
- **Ownership:** JD says "own data products end to end," "ownership of reliability, SLAs, incident response." Master's incident-resolution + SLA bullet maps directly — leave prominent.
- **Scale/reliability:** JD wants "at scale" + reliability. Master's 3.5B records + 15+ incidents + SLA framing covers it.

## 4. Top 3 Tailoring Priorities

1. **[Highest impact]** — Add `CI/CD` and `Kubernetes` to Skills (JD emphasis ×2 each; pure listed-skill gaps that drop ATS match the most).
2. **[Second]** — Reframe the BlueOrbit bullet to `ELT` + name the `data warehouse` + add a `Great Expectations` data-quality check — lands 3 missing/nice-to-have keywords in one honest edit.
3. **[Third]** — Add `Great Expectations` + `Fivetran` to the Skills section (JD nice-to-haves; real tools that round out the data-quality + ingestion story).

## Planned Changes

- [ ] Skills > Programming & Tools: append `Kubernetes, CI/CD` after `GitHub Actions`
- [ ] Skills > Big Data & Visualization: append `Great Expectations, Fivetran`
- [ ] Northwind bullet 2 (Lambda API tooling): add `via CI/CD` to the deployment-workflows phrasing
- [ ] BlueOrbit bullet: `ETL` → `ELT`, name Snowflake as the `data warehouse`, add `Great Expectations data quality checks`
