
select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
from read_csv_auto('data/silver/olist_order_reviews_dataset.csv', header = true)
