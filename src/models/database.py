"""
Database models for the lunch ordering system
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Boolean, 
    ForeignKey, Numeric, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"

    user_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    ms_teams_id = Column(String(100))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="user")
    defaults = relationship("UserDefault", back_populates="user")
    managed_orders = relationship("Order", back_populates="manager")


class Restaurant(Base):
    """Restaurant model for storing restaurant information"""
    __tablename__ = "restaurants"

    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    menu_url = Column(String(500))
    scraper_type = Column(String(50))
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    user_defaults = relationship("UserDefault", back_populates="restaurant")


class MenuItem(Base):
    """Menu item model for storing menu items"""
    __tablename__ = "menu_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    category = Column(String(100))
    scraped_at = Column(DateTime, default=func.now())

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    user_defaults = relationship("UserDefault", back_populates="menu_item")


class Order(Base):
    """Order model for storing orders"""
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(Date, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    manager_id = Column(String(100), ForeignKey("users.user_id"))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())
    finalized_at = Column(DateTime)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    manager = relationship("User", back_populates="managed_orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """Order item model for storing individual order items"""
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    user_id = Column(String(100), ForeignKey("users.user_id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.item_id"))
    quantity = Column(Integer, default=1)
    is_default = Column(Boolean, default=False)
    special_instructions = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    user = relationship("User", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class UserDefault(Base):
    """User default model for storing user default orders per restaurant"""
    __tablename__ = "user_defaults"

    default_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.user_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.restaurant_id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.item_id"))
    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("User", back_populates="defaults")
    restaurant = relationship("Restaurant", back_populates="user_defaults")
    menu_item = relationship("MenuItem", back_populates="user_defaults")


# Database initialization function
def init_db(database_url: str):
    """Initialize the database with all tables"""
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine) -> Session:
    """Get a database session"""
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
