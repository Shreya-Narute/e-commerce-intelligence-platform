"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-07 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. product_category_translation
    op.create_table(
        'product_category_translation',
        sa.Column('product_category_name', sa.String(length=100), nullable=False),
        sa.Column('product_category_name_english', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('product_category_name')
    )

    # 3. customers
    op.create_table(
        'customers',
        sa.Column('customer_id', sa.String(length=32), nullable=False),
        sa.Column('customer_unique_id', sa.String(length=32), nullable=False),
        sa.Column('customer_zip_code_prefix', sa.Integer(), nullable=False),
        sa.Column('customer_city', sa.String(length=100), nullable=False),
        sa.Column('customer_state', sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint('customer_id')
    )
    op.create_index('ix_customers_customer_unique_id', 'customers', ['customer_unique_id'], unique=False)
    op.create_index('ix_customers_zip_code', 'customers', ['customer_zip_code_prefix'], unique=False)
    op.create_index('ix_customers_state', 'customers', ['customer_state'], unique=False)

    # 4. sellers
    op.create_table(
        'sellers',
        sa.Column('seller_id', sa.String(length=32), nullable=False),
        sa.Column('seller_zip_code_prefix', sa.Integer(), nullable=False),
        sa.Column('seller_city', sa.String(length=100), nullable=False),
        sa.Column('seller_state', sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint('seller_id')
    )
    op.create_index('ix_sellers_zip_code', 'sellers', ['seller_zip_code_prefix'], unique=False)
    op.create_index('ix_sellers_state', 'sellers', ['seller_state'], unique=False)

    # 5. products
    op.create_table(
        'products',
        sa.Column('product_id', sa.String(length=32), nullable=False),
        sa.Column('product_category_name', sa.String(length=100), nullable=True),
        sa.Column('product_name_lenght', sa.Integer(), nullable=True),
        sa.Column('product_description_lenght', sa.Integer(), nullable=True),
        sa.Column('product_photos_qty', sa.Integer(), nullable=True),
        sa.Column('product_weight_g', sa.Float(), nullable=True),
        sa.Column('product_length_cm', sa.Float(), nullable=True),
        sa.Column('product_height_cm', sa.Float(), nullable=True),
        sa.Column('product_width_cm', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['product_category_name'], ['product_category_translation.product_category_name'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index('ix_products_category', 'products', ['product_category_name'], unique=False)

    # 6. orders
    op.create_table(
        'orders',
        sa.Column('order_id', sa.String(length=32), nullable=False),
        sa.Column('customer_id', sa.String(length=32), nullable=False),
        sa.Column('order_status', sa.String(length=20), nullable=False),
        sa.Column('order_purchase_timestamp', sa.DateTime(), nullable=False),
        sa.Column('order_approved_at', sa.DateTime(), nullable=True),
        sa.Column('order_delivered_carrier_date', sa.DateTime(), nullable=True),
        sa.Column('order_delivered_customer_date', sa.DateTime(), nullable=True),
        sa.Column('order_estimated_delivery_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('order_id')
    )
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'], unique=False)
    op.create_index('ix_orders_status', 'orders', ['order_status'], unique=False)
    op.create_index('ix_orders_purchase', 'orders', ['order_purchase_timestamp'], unique=False)
    op.create_index('idx_orders_status_purchase', 'orders', ['order_status', 'order_purchase_timestamp'], unique=False)

    # 7. order_items
    op.create_table(
        'order_items',
        sa.Column('order_id', sa.String(length=32), nullable=False),
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.String(length=32), nullable=False),
        sa.Column('seller_id', sa.String(length=32), nullable=False),
        sa.Column('shipping_limit_date', sa.DateTime(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('freight_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.seller_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('order_id', 'order_item_id')
    )
    op.create_index('ix_order_items_product_id', 'order_items', ['product_id'], unique=False)
    op.create_index('ix_order_items_seller_id', 'order_items', ['seller_id'], unique=False)
    op.create_index('idx_order_items_product_seller', 'order_items', ['product_id', 'seller_id'], unique=False)

    # 8. order_payments
    op.create_table(
        'order_payments',
        sa.Column('order_id', sa.String(length=32), nullable=False),
        sa.Column('payment_sequential', sa.Integer(), nullable=False),
        sa.Column('payment_type', sa.String(length=25), nullable=False),
        sa.Column('payment_installments', sa.Integer(), nullable=False),
        sa.Column('payment_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('order_id', 'payment_sequential')
    )
    op.create_index('ix_order_payments_type', 'order_payments', ['payment_type'], unique=False)

    # 9. order_reviews
    op.create_table(
        'order_reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('review_id', sa.String(length=32), nullable=False),
        sa.Column('order_id', sa.String(length=32), nullable=False),
        sa.Column('review_score', sa.Integer(), nullable=False),
        sa.Column('review_comment_title', sa.String(length=255), nullable=True),
        sa.Column('review_comment_message', sa.Text(), nullable=True),
        sa.Column('review_creation_date', sa.DateTime(), nullable=False),
        sa.Column('review_answer_timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_review_id', 'order_reviews', ['review_id'], unique=False)
    op.create_index('ix_reviews_order_id', 'order_reviews', ['order_id'], unique=False)
    op.create_index('ix_reviews_score', 'order_reviews', ['review_score'], unique=False)
    op.create_index('idx_reviews_order_score', 'order_reviews', ['order_id', 'review_score'], unique=False)

    # 10. geolocation
    op.create_table(
        'geolocation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('geolocation_zip_code_prefix', sa.Integer(), nullable=False),
        sa.Column('geolocation_lat', sa.Float(), nullable=False),
        sa.Column('geolocation_lng', sa.Float(), nullable=False),
        sa.Column('geolocation_city', sa.String(length=100), nullable=False),
        sa.Column('geolocation_state', sa.String(length=2), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_geolocation_zip', 'geolocation', ['geolocation_zip_code_prefix'], unique=False)
    op.create_index('ix_geolocation_state', 'geolocation', ['geolocation_state'], unique=False)
    op.create_index('idx_geo_zip_coords', 'geolocation', ['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng'], unique=False)


def downgrade() -> None:
    op.drop_table('geolocation')
    op.drop_table('order_reviews')
    op.drop_table('order_payments')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('products')
    op.drop_table('sellers')
    op.drop_table('customers')
    op.drop_table('product_category_translation')
    op.drop_table('users')
