# Brazilian E-Commerce (Olist) Schema Data Dictionary

| Table Name | Primary Key | Foreign Keys | Key Attributes & Description |
|---|---|---|---|
| `customers` | `customer_id` | - | `customer_unique_id` (identifies individual person), `customer_zip_code_prefix`, `customer_city`, `customer_state`. |
| `orders` | `order_id` | `customer_id` -> `customers` | `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`. |
| `order_items` | `(order_id, order_item_id)` | `order_id` -> `orders`, `product_id` -> `products`, `seller_id` -> `sellers` | `shipping_limit_date`, `price`, `freight_value`. |
| `order_payments` | `(order_id, payment_sequential)` | `order_id` -> `orders` | `payment_type` (credit_card, boleto, voucher, debit_card), `payment_installments`, `payment_value`. |
| `order_reviews` | `id` (surrogate PK), indexed `(review_id, order_id)` | `order_id` -> `orders` | `review_score` (1-5), `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp`. |
| `products` | `product_id` | `product_category_name` -> `product_category_translation` | `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`. |
| `sellers` | `seller_id` | - | `seller_zip_code_prefix`, `seller_city`, `seller_state`. |
| `geolocation` | `id` (surrogate PK) | - | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state`. |
| `product_category_translation` | `product_category_name` | - | `product_category_name_english`. Translation bridge from Portuguese categories to English. |
| `users` | `id` | - | Platform user accounts with bcrypt hashed passwords, JWT token authentication, roles (`is_superuser`). |
