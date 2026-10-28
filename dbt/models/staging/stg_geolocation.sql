
select
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    geolocation_city,
    geolocation_state
from read_csv_auto('data/silver/olist_geolocation_dataset.csv', header = true)
