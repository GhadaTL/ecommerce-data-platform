# E-Commerce Data Engineering Platform

## Overview

An end-to-end data engineering portfolio project built using the Brazilian E-Commerce Public Dataset by Olist. The platform transforms raw e-commerce data into structured, quality-checked datasets and lays the foundation for business analytics and late-delivery prediction.

The project follows a layered data architecture (Bronze, Silver, and planned Gold) and combines Python-based ETL processing with SQL transformations using dbt and DuckDB.

## Objectives

- Build reliable ETL and ELT data pipelines.
- Organize data into Bronze, Silver, and Gold layers.
- Implement reusable data quality and relationship validation checks.
- Generate data quality reports to identify potential issues.
- Build modular SQL transformation models with dbt.
- Prepare analytical datasets for business intelligence and late-delivery prediction.
- Orchestrate workflows with Apache Airflow.
- Track machine learning experiments with MLflow.
- Automate testing and integration workflows with CI/CD.
- Containerize applications using Docker.
- Explore local deployment with Kubernetes.
- Monitor pipeline execution and data quality.

## Technology Stack

**Currently implemented:**
- Python
- pandas
- pytest
- SQL
- dbt
- DuckDB
- Git and GitHub
- GitHub Actions

**Planned or to be extended:**
- Apache Airflow
- PostgreSQL
- MinIO
- MLflow
- Apache Kafka
- Docker-based application containerization
- Kubernetes
- Prometheus and Grafana

Docker Desktop is installed in the development environment. Additional orchestration, deployment, streaming, and monitoring components will be implemented in later stages.

## Dataset

**Brazilian E-Commerce Public Dataset by Olist**

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
- Latest confirmed test result: 22 tests passed.

### 4. dbt Staging Models

- Configure a dbt project using DuckDB as the local analytical database.
- Connect dbt to the local DuckDB warehouse.
- Create nine staging SQL models based on the Silver CSV datasets.
- Build views for customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translations.
- Execute all nine staging models successfully.

The staging models provide a consistent starting point for subsequent transformations. Intermediate models and analytical Gold marts are planned next.

## Data Quality Findings

Initial profiling and validation of the Olist dataset identified:

- 261,831 exact duplicate geolocation records removed during Bronze-to-Silver processing.
- 9 non-positive payment values requiring review.
- 6 products with zero or missing weights.
- 814 rows with duplicated `review_id` values when checking that column alone.
- 2 product categories without a matching English translation.

These findings describe observed dataset issues and do not necessarily mean that every affected record is unusable. Their treatment depends on the relevant business rules.

## Project Structure

```text
ecommerce-data-platform/
├── .github/
│   └── workflows/
├── dags/
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   ├── processed/
│   ├── reports/
│   └── warehouse/
├── dbt/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_category_translation.sql
│       │   ├── stg_customers.sql
│       │   ├── stg_geolocation.sql
│       │   ├── stg_order_items.sql
│       │   ├── stg_order_payments.sql
│       │   ├── stg_order_reviews.sql
│       │   ├── stg_orders.sql
│       │   ├── stg_products.sql
│       │   └── stg_sellers.sql
│       ├── intermediate/
│       └── marts/
├── docker/
├── docs/
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

Some directories are reserved for future components and may not contain implemented functionality yet. Local datasets, generated reports, the DuckDB database, and dbt-generated artifacts are excluded from version control.

## Setup and Execution

### Prerequisites

- Python 3.11
- Git
- The Olist dataset downloaded from Kaggle
- dbt Core and the dbt-duckdb adapter for dbt transformations

### 1. Clone the repository

```powershell
git clone https://github.com/GhadaTL/ecommerce-data-platform.git
cd ecommerce-data-platform
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

If dbt dependencies are not included in `requirements.txt`, install them separately:

```powershell
python -m pip install dbt-core dbt-duckdb
```

### 4. Prepare the dataset

Download the Olist dataset from Kaggle and place the original CSV files in `data/raw/`.

Run the Python ETL pipeline to generate the Bronze and Silver datasets before executing the dbt models.

### 5. Run automated tests

```powershell
python -m pytest -v
```

### 6. Run data quality validation

```powershell
python -m src.quality.validate_data_quality
```

### 7. Validate table relationships

```powershell
python -m src.quality.validate_relationships
```

### 8. Generate the data quality report

```powershell
python -m src.quality.generate_quality_report
```

The generated report is written to:

`data/reports/data_quality_report.json`

### 9. Run dbt staging models

From the repository root:

```powershell
dbt debug --project-dir dbt
dbt run --project-dir dbt --select staging
```

The dbt project uses a DuckDB profile configured locally in `~/.dbt/profiles.yml`. The default warehouse location is `data/warehouse/ecommerce.duckdb`.

The warehouse database and generated dbt files are local artifacts and are not committed to GitHub.

## Project Roadmap

- [x] Repository and development environment setup
- [x] Bronze-to-Silver ETL pipeline
- [x] Reusable data quality validation
- [x] Relationship validation
- [x] JSON data quality reporting
- [x] Automated tests and GitHub Actions CI
- [x] dbt project setup and DuckDB connection
- [x] Nine dbt staging models
- [ ] Intermediate transformations with dbt
- [ ] Analytical Gold marts
- [ ] Analytical database integration beyond the current DuckDB setup
- [ ] Workflow orchestration with Apache Airflow
- [ ] Late-delivery prediction and ML experiment tracking
- [ ] Containerization and local deployment
- [ ] Streaming pipeline implementation
- [ ] Pipeline monitoring and observability

## License and Data

Dataset usage is subject to the original dataset terms. Raw data, generated datasets, local reports, database files, credentials, and secrets should not be committed to the repository.
