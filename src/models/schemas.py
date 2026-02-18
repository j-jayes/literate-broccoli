"""
Pydantic models for API request/response validation
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class MenuItemBase(BaseModel):
    """Base model for menu items"""
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str


class MenuItem(MenuItemBase):
    """Menu item model with ID"""
    item_id: int
    restaurant_id: int
    scraped_at: datetime

    class Config:
        from_attributes = True


class MenuItemCreate(MenuItemBase):
    """Model for creating menu items"""
    restaurant_id: int


class UserBase(BaseModel):
    """Base model for users"""
    user_id: str
    name: str
    email: EmailStr


class User(UserBase):
    """User model with additional fields"""
    ms_teams_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Model for creating users"""
    ms_teams_id: Optional[str] = None


class RestaurantBase(BaseModel):
    """Base model for restaurants"""
    name: str
    menu_url: Optional[str] = None
    scraper_type: Optional[str] = None


class Restaurant(RestaurantBase):
    """Restaurant model with ID"""
    restaurant_id: int
    last_scraped: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RestaurantCreate(RestaurantBase):
    """Model for creating restaurants"""
    pass


class OrderItemBase(BaseModel):
    """Base model for order items"""
    menu_item_id: int
    quantity: int = 1
    special_instructions: Optional[str] = None


class OrderItem(OrderItemBase):
    """Order item with user information"""
    order_item_id: int
    user_id: str
    user_name: str
    menu_item_name: str
    is_default: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemCreate(OrderItemBase):
    """Model for creating order items"""
    user_id: str
    is_default: bool = False


class OrderBase(BaseModel):
    """Base model for orders"""
    order_date: date
    restaurant_id: int
    manager_id: str


class Order(OrderBase):
    """Order model with items"""
    order_id: int
    restaurant_name: str
    manager_name: str
    status: str
    items: List[OrderItem] = []
    created_at: datetime
    finalized_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    """Model for creating orders"""
    pass


class OrderUpdate(BaseModel):
    """Model for updating order status"""
    status: Optional[str] = None
    finalized_at: Optional[datetime] = None


class UserDefaultBase(BaseModel):
    """Base model for user defaults"""
    restaurant_id: int
    menu_item_id: int


class UserDefault(UserDefaultBase):
    """User default with ID"""
    default_id: int
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserDefaultCreate(UserDefaultBase):
    """Model for creating user defaults"""
    user_id: str


class MenuResponse(BaseModel):
    """Response model for menu data"""
    restaurant: Restaurant
    items: List[MenuItem]


class OrderSummary(BaseModel):
    """Summary model for orders"""
    order: Order
    item_totals: dict[str, int]
    total_items: int
    pending_users: List[str]


class NotificationRequest(BaseModel):
    """Request model for sending notifications"""
    order_id: int
    notification_type: str = Field(..., pattern="^(order_created|order_updated|order_finalized)$")
    recipients: List[str]
