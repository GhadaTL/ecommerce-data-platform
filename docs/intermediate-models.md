# Intermediate Models — E-Commerce Data Platform

## 1. Overview

The intermediate layer is the second transformation layer of the dbt project. It builds on the staging models to combine related datasets, enrich records with additional information, and prepare structured data for analytical models in the Gold layer.

The transformations are implemented with dbt and SQL, using DuckDB as the data warehouse.

Two intermediate models have been developed:

- `int_order_items_enriched`
- `int_orders_enriched`

Both models are configured as **views** in DuckDB.

## 2. Model: `int_order_items_enriched`

### Objective

This model enriches order-item records with product and seller information. It provides a consolidated view of the items sold on the platform.

### Source models

- `stg_order_items`: order-item identifiers, product and seller identifiers, prices, freight values, and shipping-limit dates.
- `stg_products`: product categories, physical dimensions, weight, and product-weight quality flags.
- `stg_sellers`: seller locations and geographic information.

### Transformations performed

The model uses `LEFT JOIN` operations to combine the three staging models:

1. Join order items with products using `product_id`.
2. Join order items with sellers using `seller_id`.
3. Retain the original order-item attributes and add the available product and seller information.

The resulting dataset contains:

- Order identifiers: `order_id`, `order_item_id`
- Product and seller identifiers: `product_id`, `seller_id`
- Sales information: `price`, `freight_value`
- Shipping information: `shipping_limit_date`
- Product attributes: category, weight, length, height, and width
- Product quality information: `product_weight_is_positive`
- Seller location: `seller_city`, `seller_state`

### Why use LEFT JOIN?

A `LEFT JOIN` preserves records from the order-items dataset even when the corresponding product or seller information is unavailable. This prevents those order items from being discarded during enrichment.

### Validation

The model was executed successfully with dbt.

- Expected row count: **112,650**
- Observed row count: **112,650**

The matching row count indicates that the joins did not increase or reduce the total number of order-item records. It does not, by itself, prove that every product and seller matched or that the composite key is unique.

## 3. Model: `int_orders_enriched`

### Objective

This model enriches order records with customer information and derives delivery-performance indicators. It prepares order-level data for delivery analysis.

### Source models

- `stg_orders`: order identifiers, customer identifiers, order statuses, and order-related timestamps.
- `stg_customers`: customer identifiers, unique customer identifiers, cities, and states.

### Transformations performed

The model joins orders with customers using `customer_id`, retaining the order records and adding customer attributes.

It also derives two delivery-related fields.

#### `is_late_delivery`

This Boolean field indicates whether an order was delivered after its estimated delivery date.

- `TRUE`: the actual delivery date is later than the estimated delivery date.
- `FALSE`: the actual delivery date is on or before the estimated delivery date.
- `NULL`: the actual or estimated delivery date is unavailable.

#### `delivery_delay_days`

This field calculates the difference in days between the estimated delivery date and the actual delivery date.

A positive value indicates a delay, zero indicates delivery on the estimated date, and a negative value indicates delivery before the estimated date. The result is `NULL` when a required date is missing.

### Output attributes

The resulting dataset contains:

- Order identifiers: `order_id`, `customer_id`
- Order status: `order_status`
- Order timestamps: purchase, approval, carrier handoff, customer delivery, and estimated delivery dates
- Customer information: `customer_unique_id`, `customer_city`, `customer_state`
- Delivery indicators: `is_late_delivery`, `delivery_delay_days`

### Validation

The model was executed successfully with dbt.

- Expected row count: **99,441**
- Observed row count: **99,441**

The matching row count indicates that the customer join did not increase or reduce the number of order records. Further uniqueness and relationship tests can provide stronger validation.

## 4. Execution and validation

The intermediate models can be built together from the project root with:

```bash
dbt run --project-dir dbt --select intermediate
```

The successful execution returned:

- `PASS=2`
- `ERROR=0`

The row counts were also checked using dbt:

| Model | Expected rows | Observed rows |
|---|---:|---:|
| `int_order_items_enriched` | 112,650 | 112,650 |
| `int_orders_enriched` | 99,441 | 99,441 |

These checks confirm successful model execution and preservation of the expected row counts. Additional dbt tests will be useful for validating key uniqueness and relationships.

## 5. Design considerations

- **Separation of concerns:** staging models select and expose source columns, while intermediate models enrich and derive information.
- **Reusable transformations:** both intermediate models can serve as inputs to multiple analytical models.
- **LEFT JOIN operations:** preserve the records from the main dataset when related information is missing.
- **Delivery metrics:** centralize delivery-performance logic so downstream models can reuse consistent definitions.
- **Avoiding payment duplication:** payment records are not joined directly to order items in these models. Multiple payments and multiple items can belong to the same order, so joining both datasets without prior aggregation could multiply rows and distort totals.

## 6. Next step

The next step is to develop the Gold layer, beginning with `fct_sales`. This analytical model will combine item-level sales information with order-level attributes to support sales analysis by purchase date, product category, seller location, and delivery performance.

The Gold model will be developed and validated separately; it is not yet included in this document's completed transformations.