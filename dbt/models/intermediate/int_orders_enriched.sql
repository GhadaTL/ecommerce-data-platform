
select
    -- Order identifiers and status
    o.order_id,
    o.customer_id,
    o.order_status,

    -- Order dates
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,

    -- Customer information
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,

    -- Delivery performance
    case
        when o.order_delivered_customer_date is null
          or o.order_estimated_delivery_date is null
            then null
        when o.order_delivered_customer_date
             > o.order_estimated_delivery_date
            then true
        else false
    end as is_late_delivery,

    date_diff(
        'day',
        cast(o.order_estimated_delivery_date as date),
        cast(o.order_delivered_customer_date as date)
    ) as delivery_delay_days

from {{ ref('stg_orders') }} as o

left join {{ ref('stg_customers') }} as c
    on o.customer_id = c.customer_id