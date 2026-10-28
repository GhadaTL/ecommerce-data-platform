
select
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,
    payment_value_is_positive
from read_csv_auto('data/silver/olist_order_payments_dataset.csv', header = true)
