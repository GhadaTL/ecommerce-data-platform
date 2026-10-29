select
    order_id,
    order_item_id
from {{ ref('fct_sales') }}
group by
    order_id,
    order_item_id
having count(*) > 1