select *
from {{ ref('fct_sales') }}
where price <= 0