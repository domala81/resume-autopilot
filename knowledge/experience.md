# Northwind Analytics

Role: Data Engineer
Location: Austin, USA
Dates: Jan 2024 – Present

Technologies: AWS (Glue, Lambda, DynamoDB, SQS, Step Functions, S3), PySpark, Databricks, SQL, GitHub Actions

## Project: Enterprise AWS Medallion Data Pipeline

### Architecture Overview
- Fully AWS-based data engineering pipeline
- Ingests data from multiple upstream source tables
- Transforms and loads into canonical Big Tables stored in Delta Lake format
- Follows Bronze/Silver/Gold Medallion Architecture
- Processes 3.5 billion+ records total across all layers
- Role: building new pipeline components and improving features on existing architecture

### Data Domain Onboarding Process
When new fields need to be added to the Big Tables (per business/product requirements):
1. Identify source tables containing the required data
2. Write and test SQL transformation logic in Databricks notebooks
3. Define transformation configs for deployment
4. Test and validate (statistical + schema validation)
5. Deploy — the Big Table expands horizontally with the new dataset
- "Onboarding 10+ data domains" = completed this end-to-end process for 10+ new field groups
- Cycle time: 6–8 working days per domain (domains are independent, can run in parallel)
- Pipeline runs: daily

### Other Contributions
- Built serverless ingestion monitoring: Lambda, DynamoDB, Step Functions (8-state workflow) — automates delta file event triggering
- Developed internal Lambda API tooling reducing engineering effort ~70%
- Resolved 15+ high-severity production incidents via root cause analysis
- Automated test data provisioning across internal APIs and DynamoDB, cutting setup time ~75%

Raw Bullets (original):
- Built AWS data pipelines (PySpark in Glue) processing billions of records across Bronze/Silver/Gold Medallion layers; onboarded 10+ data domains with SQL transformation logic and schema validation in Databricks
- Engineered serverless ingestion monitoring via Lambda, DynamoDB, and Step Functions (8-state workflow), automating delta file event triggering and improving pipeline observability
- Developed internal Lambda API tooling reducing engineering effort by ~70%; resolved 15+ high-severity incidents via root cause analysis to restore service reliability

---

# BlueOrbit Labs

Role: Data Engineering Intern
Location: Remote, USA
Dates: May 2023 – Aug 2023

Technologies: Airflow, dbt, Kafka, Snowflake, Python, SQL

Bullets:
- Designed an Airflow + dbt ETL pipeline loading 50M+ daily events from Kafka into Snowflake
- Reduced data-availability latency from 6 hours to under 30 minutes for 5 analytics teams
- Added dbt tests and schema checks to catch upstream data quality regressions before they hit dashboards

---

# Acme AI

Role: Machine Learning Engineer Intern
Location: Remote, USA
Dates: May 2022 – Aug 2022

Technologies: Python, LSTM, GloVe, BERT, TensorFlow, scikit-learn, NLP

Bullets:
- Led a team of 3 to build text preprocessing pipelines (TF-IDF, GloVe, BERT tokenization) for 40,000+ imbalanced support tickets across 5 intent classes
- Benchmarked Naive Bayes, LSTM (GloVe 300-dim), and BERT (110M params) on 5-class intent classification, achieving 95.4% validation accuracy
