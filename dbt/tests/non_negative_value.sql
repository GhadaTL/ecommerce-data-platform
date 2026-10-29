select *
from {{ ref('fct_sales') }}
where freight_value < 0