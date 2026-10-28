
select
    product_category_name,
    product_category_name_english
from read_csv_auto('data/silver/product_category_name_translation.csv', header = true)
