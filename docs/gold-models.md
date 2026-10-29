# Gold Models — E-Commerce Data Platform

## 1. Overview

The Gold layer contains analytical models designed to support business intelligence, reporting, and data analysis.

It builds on the Intermediate layer, which enriches staging data and centralizes reusable business logic.

The first Gold model developed in this project is `fct_sales`.

## 2. Model: `fct_sales`

### Objective

`fct_sales` provides an analytical dataset combining order-item information with order status, purchase dates, customer location, and delivery-performance indicators.

It can serve as a source for sales analysis and business intelligence dashboards.

### Source models

- `int_order_items_enriched`: order items, product attributes, seller information, prices, and freight values.
- `int_orders_enriched`: order status, purchase timestamps, customer location, and delivery-performance indicators.

### Transformations performed

The model joins the two Intermediate models using `order_id`.

Since `int_orders_enriched` contains one row per order, this join is intended to preserve the order-item grain.

The model includes:

- Order identifiers: `order_id`, `order_item_id`
- Purchase information: `order_purchase_timestamp`, `order_status`
- Product information: `product_id`, `product_category_name`
- Seller information: `seller_id`, `seller_state`
- Sales amounts: `price`, `freight_value`
- Derived amount: `total_item_amount`
- Customer location: `customer_state`
- Delivery indicators: `is_late_delivery`, `delivery_delay_days`

### Business calculation

The field `total_item_amount` is calculated as:

`price + freight_value`

It represents the item price plus its associated freight charge. It should not be interpreted as the total payment amount for an entire order.

### Data grain

The model is designed at the order-item grain: one row represents an item within an order.

The composite key is:

`(order_id, order_item_id)`

### Validation

The model was executed successfully using dbt.

- Expected row count: **112,650**
- Observed row count: **112,650**

The row count matches the source Intermediate model `int_order_items_enriched`.

The following quality checks were also executed:

- Required identifiers and purchase timestamps are not null.
- Item prices are strictly positive.
- Freight values are non-negative.
- The composite order-item key is unique.

All nine tests selected for `fct_sales` passed in the recorded execution.

## 3. Materialization

The project configures models in `dbt/models/marts/` as tables in DuckDB.

This means `fct_sales` is materialized as a table rather than a view, making it suitable for repeated analytical queries.

## 4. Current limitations

The current model focuses on order-item sales information and delivery attributes.

It does not directly join payment records. This avoids multiplying item rows when an order contains multiple items and multiple payment records.

Further analytical models may be added to support revenue trends, category performance, seller analysis, and delivery KPIs.

## 5. Next steps

Potential extensions include:

- Aggregated sales metrics by month and product category.
- Delivery-performance analysis.
- Additional dbt tests and relationship checks.
- Integration with a BI tool for dashboards.