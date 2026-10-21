# E-Commerce Data Engineering Platform

## Overview

An end-to-end data engineering portfolio project built with the Brazilian E-Commerce Public Dataset by Olist. The platform aims to transform raw e-commerce data into reliable analytical datasets and support business analytics and late-delivery prediction.

## Objectives

- Build reliable ETL and ELT data pipelines.
- Organize data into Bronze, Silver, and Gold layers.
- Implement reusable data quality and relationship validation checks.
- Generate data quality reports to identify potential issues.
- Orchestrate workflows with Apache Airflow.
- Build analytical data models using dbt.
- Track machine learning experiments with MLflow.
- Automate testing and build workflows with CI/CD.
- Containerize applications using Docker.
- Explore local deployment with Kubernetes.
- Monitor pipeline execution and services.

## Technology Stack

**Currently used:** Python, pandas, pytest, Git, GitHub, GitHub Actions.

**Planned:** DuckDB, dbt, PostgreSQL, MinIO, Apache Airflow, MLflow, Apache Kafka, Docker, Kubernetes, Prometheus, and Grafana.

The stack will evolve as new pipeline components are implemented.

## Dataset

Brazilian E-Commerce Public Dataset by Olist.

Source: [Olist dataset on Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

The dataset contains information about customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translations.

Raw dataset files are stored locally and are not committed to the repository.

## Current Implementation

### 1. Bronze-to-Silver ETL

- Load and organize the raw Olist CSV files.
- Create Bronze and Silver data layers.
- Remove exact duplicate geolocation records.
- Convert date columns and identify invalid values.
- Flag non-positive payment values and invalid product weights.
- Generate an ETL processing report.

### 2. Data Quality and Relationship Validation

- Check primary and candidate key uniqueness.
- Detect duplicate review IDs.
- Validate foreign key relationships between related tables.
- Check payment values, review scores, item prices, and freight values.
- Validate product dimensions and geographic coordinates.
- Check product category translation coverage.
- Generate a JSON data quality report with `PASS`, `REVIEW`, and `FAIL` statuses.

### 3. Automated Testing and CI

- Automated tests using pytest.
- Tests for ETL transformations, data quality functions, and relationship validation.
- GitHub Actions workflow to run tests on pushes and pull requests targeting `main`.

## Data Quality Findings

Initial profiling and validation of the Olist dataset identified:

- 261,831 exact duplicate geolocation records removed during Bronze-to-Silver processing.
- 9 non-positive payment values requiring review.
- 6 products with zero or missing weights.
- 814 duplicate-key rows when checking `review_id` alone.
- 2 product categories without a matching English translation.

These findings are dataset observations, not necessarily proof that every affected record is unusable. Their treatment depends on the relevant business rules.

## Project Structure

```text
ecommerce-data-platform/
├── .github/
│   └── workflows/
├── docs/
├── dags/
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   └── reports/
├── dbt/
├── docker/
├── k8s/
├── ml/
├── src/
│   ├── etl/
│   └── quality/
├── streaming/
├── tests/
├── requirements.txt
└── README.md
```

Some directories are reserved for future components and may not contain implemented functionality yet.

## Setup and Execution

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Run automated tests

```powershell
python -m pytest -v
```

### 4. Run data quality validation

```powershell
python -m src.quality.validate_data_quality
```

### 5. Validate table relationships

```powershell
python -m src.quality.validate_relationships
```

### 6. Generate the data quality report

```powershell
python -m src.quality.generate_quality_report
```

The generated report is written to:

`data/reports/data_quality_report.json`

The raw dataset must be downloaded separately and placed in `data/raw/` before running the pipeline.

## Project Roadmap

- [x] Repository and development environment setup
- [x] Bronze-to-Silver ETL pipeline
- [x] Reusable data quality validation
- [x] Relationship validation
- [x] JSON data quality reporting
- [x] Automated tests and GitHub Actions CI
- [ ] Analytical Gold layer with dbt
- [ ] Analytical database integration
- [ ] Workflow orchestration with Airflow
- [ ] Late-delivery prediction and ML experiment tracking
- [ ] Containerization and local deployment
- [ ] Pipeline monitoring and observability

## License and Data

Dataset usage is subject to the original dataset terms. Raw data, generated datasets, local reports, credentials, and secrets should not be committed to the repository.
