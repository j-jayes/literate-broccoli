"""
Sample tests for the lunch ordering system
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from src.models.schemas import (
    MenuItem, MenuItemCreate, 
    Order, OrderCreate,
    OrderItem, OrderItemCreate,
    User, UserCreate
)


def test_menu_item_creation():
    """Test creating a menu item"""
    item = MenuItem(
        item_id=1,
        restaurant_id=1,
        name="Caesar Salad",
        description="Fresh romaine lettuce with parmesan",
        price=Decimal("8.99"),
        category="Appetizers",
        scraped_at=datetime.now()
    )
    assert item.name == "Caesar Salad"
    assert item.price == Decimal("8.99")


def test_order_creation():
    """Test creating an order"""
    order = OrderCreate(
        order_date=date.today(),
        restaurant_id=1,
        manager_id="manager@example.com"
    )
    assert order.order_date == date.today()
    assert order.restaurant_id == 1


def test_user_creation():
    """Test creating a user"""
    user = UserCreate(
        user_id="user123",
        name="John Doe",
        email="john.doe@example.com"
    )
    assert user.name == "John Doe"
    assert user.email == "john.doe@example.com"


def test_order_item_creation():
    """Test creating an order item"""
    item = OrderItemCreate(
        user_id="user123",
        menu_item_id=1,
        quantity=2,
        special_instructions="No onions"
    )
    assert item.quantity == 2
    assert item.special_instructions == "No onions"


# Add more tests as services are implemented
@pytest.mark.skip(reason="API not implemented yet")
def test_api_create_order():
    """Test creating an order via API"""
    pass


@pytest.mark.skip(reason="Menu scraper not implemented yet")
def test_menu_scraper():
    """Test menu scraping functionality"""
    pass


@pytest.mark.skip(reason="Notification service not implemented yet")
def test_send_notification():
    """Test sending notifications"""
    pass
