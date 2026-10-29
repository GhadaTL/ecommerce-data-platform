
with order_items as (

    select *
    from {{ ref('int_order_items_enriched') }}

),

orders as (

    select
        order_id,
        order_status,
        order_purchase_timestamp,
        customer_state,
        is_late_delivery,
        delivery_delay_days
    from {{ ref('int_orders_enriched') }}

)

select
    -- Order identifiers
    oi.order_id,
    oi.order_item_id,

    -- Order dates and status
    o.order_purchase_timestamp,
    o.order_status,

    -- Product and seller information
    oi.product_id,
    oi.product_category_name,
    oi.seller_id,
    oi.seller_state,

    -- Sales amounts
    oi.price,
    oi.freight_value,
    oi.price + oi.freight_value as total_item_amount,

    -- Customer and delivery information
    o.customer_state,
    o.is_late_delivery,
    o.delivery_delay_days

from order_items as oi

left join orders as o
    on oi.order_id = o.order_id