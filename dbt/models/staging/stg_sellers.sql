
select
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
from read_csv_auto('data/silver/olist_sellers_dataset.csv', header = true)
