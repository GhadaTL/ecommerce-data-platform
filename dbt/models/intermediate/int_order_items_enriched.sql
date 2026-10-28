
select
    -- Order item information
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.shipping_limit_date,

    -- Sales amounts
    oi.price,
    oi.freight_value,

    -- Product information
    p.product_category_name,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    p.product_weight_is_positive,

    -- Seller information
    s.seller_city,
    s.seller_state

from {{ ref('stg_order_items') }} as oi

left join {{ ref('stg_products') }} as p
    on oi.product_id = p.product_id

left join {{ ref('stg_sellers') }} as s
    on oi.seller_id = s.seller_id