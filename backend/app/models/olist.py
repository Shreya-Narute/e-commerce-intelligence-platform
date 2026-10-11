from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Float,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    customer_unique_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    customer_zip_code_prefix: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    customer_city: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    order_status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    order_purchase_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    order_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_delivered_carrier_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_delivered_customer_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    order_estimated_delivery_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    payments: Mapped[List["OrderPayment"]] = relationship(
        "OrderPayment",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[List["OrderReview"]] = relationship(
        "OrderReview",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_orders_status_purchase", "order_status", "order_purchase_timestamp"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        primary_key=True,
    )
    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("products.product_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    seller_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("sellers.seller_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    shipping_limit_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    freight_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    seller: Mapped["Seller"] = relationship("Seller", back_populates="order_items")

    __table_args__ = (
        Index("idx_order_items_product_seller", "product_id", "seller_id"),
    )


class OrderPayment(Base):
    __tablename__ = "order_payments"

    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        primary_key=True,
    )
    payment_sequential: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_type: Mapped[str] = mapped_column(String(25), nullable=False, index=True)
    payment_installments: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payment_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="payments")


class OrderReview(Base):
    __tablename__ = "order_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    review_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    review_comment_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    review_comment_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_creation_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    review_answer_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="reviews")

    __table_args__ = (
        Index("idx_reviews_order_score", "order_id", "review_score"),
    )


class ProductCategoryTranslation(Base):
    __tablename__ = "product_category_translation"

    product_category_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    product_category_name_english: Mapped[str] = mapped_column(String(100), nullable=False)

    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category_translation",
    )


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    product_category_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("product_category_translation.product_category_name", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_name_lenght: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    product_description_lenght: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    product_photos_qty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    product_weight_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_length_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_width_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product")
    category_translation: Mapped[Optional["ProductCategoryTranslation"]] = relationship(
        "ProductCategoryTranslation",
        back_populates="products",
    )


class Seller(Base):
    __tablename__ = "sellers"

    seller_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    seller_zip_code_prefix: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    seller_city: Mapped[str] = mapped_column(String(100), nullable=False)
    seller_state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="seller")


class Geolocation(Base):
    __tablename__ = "geolocation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    geolocation_zip_code_prefix: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    geolocation_lat: Mapped[float] = mapped_column(Float, nullable=False)
    geolocation_lng: Mapped[float] = mapped_column(Float, nullable=False)
    geolocation_city: Mapped[str] = mapped_column(String(100), nullable=False)
    geolocation_state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)

    __table_args__ = (
        Index("idx_geo_zip_coords", "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"),
    )
