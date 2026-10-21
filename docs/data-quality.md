# Data Quality and Validation

## 1. Overview

Data quality is an essential component of the E-Commerce Data Engineering Platform. The objective is to detect inconsistencies, validate relationships between datasets, and improve the reliability of downstream analytics.

The project uses the Brazilian E-Commerce Public Dataset by Olist.

Data quality validation is implemented in Python using pandas. Automated tests are written with pytest, and validation results are collected in a JSON report.

## 2. Data Quality Architecture

The current validation workflow includes:

1. Load the Olist CSV files.
2. Profile and validate individual datasets.
3. Check primary and candidate keys.
4. Validate relationships between related tables.
5. Identify invalid values and missing category translations.
6. Generate a JSON report containing validation results and statuses.

The main scripts are:

- `src/quality/validate_data_quality.py`: validates values and data quality rules.
- `src/quality/validate_relationships.py`: validates keys, foreign key relationships, and category translation coverage.
- `src/quality/generate_quality_report.py`: aggregates validation results into a JSON report.

## 3. Data Quality Rules

### 3.1 Payment Values

**Rule:** Payment values should be positive.

**Purpose:** Identify zero or negative payment amounts that may require investigation.

**Implementation:** `count_non_positive_payments()`.

**Observed result:** 9 non-positive payment values were detected in the Olist dataset.

**Status:** `REVIEW` when non-positive values are found.

### 3.2 Review Scores

**Rule:** Review scores must be within the expected range of 1 to 5.

**Purpose:** Detect invalid review scores before using them in reporting or analysis.

**Implementation:** `count_invalid_review_scores()`.

**Status:** `PASS` if no invalid scores are found; otherwise, `REVIEW`.

### 3.3 Item Prices and Freight Values

**Rules:**
- Item prices must not be negative.
- Freight values must not be negative.

**Purpose:** Detect invalid monetary values that could affect sales and delivery cost analysis.

**Implementations:**
- `count_negative_item_prices()`
- `count_negative_freight_values()`

**Status:** `PASS` if no negative values are found; otherwise, `REVIEW`.

### 3.4 Product Dimensions

**Rule:** Product dimensions and weight must be positive and present.

The following fields are checked:

- `product_weight_g`
- `product_length_cm`
- `product_height_cm`
- `product_width_cm`

**Purpose:** Identify missing, zero, or negative measurements that may affect logistics and shipping analysis.

**Implementation:** `count_invalid_product_dimensions()`.

**Observed result:** 6 products were identified with zero or missing weights.

**Status:** `REVIEW` when zero, negative, or missing values are detected.

### 3.5 Geographic Coordinates

**Rules:**
- Latitude must be between -90 and 90.
- Longitude must be between -180 and 180.

**Purpose:** Detect invalid geographic coordinates that could affect location-based analysis.

**Implementation:** `count_invalid_coordinates()`.

**Status:** `PASS` if all checked coordinates are valid; otherwise, `REVIEW`.

### 3.6 Key Uniqueness

**Rule:** Primary and candidate keys should not contain null values or duplicate key combinations.

The project checks keys such as:

- `orders.order_id`
- `customers.customer_id`
- `products.product_id`
- `sellers.seller_id`
- `order_items (order_id, order_item_id)`
- `order_payments (order_id, payment_sequential)`

The `order_reviews.review_id` field is also checked independently.

**Purpose:** Detect potential duplicate records and validate the identifiers used to connect datasets.

**Implementation:** `check_unique()`.

**Observed result:** The `review_id` field has 814 duplicate-key rows. However, the composite key `(review_id, order_id)` is unique in the profiled dataset.

**Status:** `PASS` if the checked key has no duplicates or nulls; otherwise, `REVIEW`.

### 3.7 Foreign Key Relationships

**Rule:** Foreign key values must reference existing records in the corresponding parent dataset.

The project checks relationships including:

- `orders.customer_id` → `customers.customer_id`
- `order_items.order_id` → `orders.order_id`
- `order_items.product_id` → `products.product_id`
- `order_items.seller_id` → `sellers.seller_id`
- `order_payments.order_id` → `orders.order_id`
- `order_reviews.order_id` → `orders.order_id`

**Purpose:** Detect orphan records and maintain consistency between related datasets.

**Implementation:** `check_foreign_key()`.

**Observed result:** No missing parent values were detected in the relationships checked against the raw Olist datasets.

**Status:**
- `PASS`: no missing parent values.
- `FAIL`: one or more child values have no matching parent.

### 3.8 Product Category Translation

**Rule:** Product categories should have a corresponding entry in the English category translation dataset when a translation is required.

**Purpose:** Improve consistency in product category reporting and dashboard labels.

**Implementation:** `check_category_translation()`.

**Observed result:** Two categories have no matching translation:

- `pc_gamer`
- `portateis_cozinha_e_preparadores_de_alimentos`

**Status:** `PASS` if all checked categories have translations; otherwise, `REVIEW`.

## 4. Automated Testing Strategy

Automated tests are implemented using pytest.

The current test suite contains three test modules:

| Test module | Number of tests | Main purpose |
|---|---:|---|
| `tests/test_bronze_to_silver.py` | 5 | Validate ETL transformations and error handling |
| `tests/test_data_quality.py` | 12 | Validate data quality functions |
| `tests/test_relationships.py` | 5 | Validate key and relationship checks |
| **Total** | **22** | |

These counts reflect the last reported test run and should be rechecked if the test suite changes.

### Artificial Test Data

Most unit tests use small artificial DataFrames or temporary files.

For example, a payment validation test can use values such as `[100, 50, 0, -10]` to verify that two non-positive values are detected.

Artificial test data makes it possible to control the expected results and test normal cases, invalid values, duplicates, missing values, and missing parent records.

### Real Dataset Validation

The validation scripts and report generator load the actual Olist CSV files from `data/raw/`.

These scripts measure real dataset characteristics and identify actual data quality issues.

Unit tests and real dataset validation serve different purposes: unit tests validate the code, while real-data checks evaluate the dataset.

## 5. Validation Statuses

The JSON quality report uses three statuses:

| Status | Meaning |
|---|---|
| `PASS` | The validation rule passed. |
| `REVIEW` | An anomaly was detected and requires examination. |
| `FAIL` | A critical validation condition failed, such as a missing foreign key parent. |

A `REVIEW` result does not automatically mean that a record must be deleted. The appropriate action depends on the business context.

## 6. Quality Report

The report generator writes its results to:

`data/reports/data_quality_report.json`

The report includes:

- Dataset name
- Generation timestamp
- Number of checks
- Individual check names and categories
- Detected anomaly counts
- Validation statuses

The report is generated from the actual Olist CSV files, not from the artificial DataFrames used in unit tests.

The generated report is a local artifact and is excluded from version control under the project's current `.gitignore` rules.

## 7. How to Run the Validations

Run the automated test suite:

```powershell
python -m pytest -v
```

Run data quality checks:

```powershell
python -m src.quality.validate_data_quality
```

Run relationship validation:

```powershell
python -m src.quality.validate_relationships
```

Generate the JSON quality report:

```powershell
python -m src.quality.generate_quality_report
```

The raw Olist CSV files must be available in `data/raw/` before executing the validation scripts.

## 8. Current Limitations and Future Improvements

Potential improvements include:

- Adding tests for the JSON report structure and status assignment.
- Defining explicit business rules for handling invalid payments and product measurements.
- Using the composite review key where appropriate instead of assuming `review_id` is unique.
- Integrating data quality checks into the CI pipeline.
- Adding schema and transformation tests to the future dbt models.
- Introducing data freshness, volume anomaly, and schema drift checks.
- Tracking data quality metrics over successive pipeline executions.

## 9. Conclusion

The current data quality layer combines reusable Python validation functions, automated unit tests, relationship checks, and a JSON reporting mechanism.

This foundation helps identify data inconsistencies before the datasets are used to build analytical models and business reports.
