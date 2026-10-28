
select
    product_id,
    product_category_name,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm,
    product_weight_is_positive
from read_csv_auto('data/silver/olist_products_dataset.csv', header = true)
