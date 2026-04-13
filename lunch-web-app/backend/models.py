"""Pydantic models for the web app API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MenuItem(BaseModel):
    name: str
    price: Optional[Decimal] = None
    category: str = "other"
    description: str = ""
    subcategory: Optional[str] = None


class RestaurantMenu(BaseModel):
    restaurant_name: str
    items: list[MenuItem]


class ScrapeRequest(BaseModel):
    restaurant_name: str
    menu_url: Optional[str] = None


class ScrapeResponse(BaseModel):
    items: list[MenuItem]


class CachedRestaurantsResponse(BaseModel):
    restaurants: list[RestaurantMenu]


class CreateSessionRequest(BaseModel):
    restaurants: list[RestaurantMenu]
    description: Optional[str] = None


class SubmitOrderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    selected_items: list[str] = Field(min_length=1)


class Order(BaseModel):
    name: str
    items: list[str]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class LunchSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurants: list[RestaurantMenu]
    description: Optional[str] = None
    orders: dict[str, Order] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def title(self) -> str:
        return " & ".join(r.restaurant_name for r in self.restaurants)

    @property
    def all_items(self) -> list[MenuItem]:
        return [item for r in self.restaurants for item in r.items]


class SessionResponse(BaseModel):
    id: UUID
    title: str
    restaurants: list[RestaurantMenu]
    description: Optional[str] = None
    orders: dict[str, Order]
    created_at: datetime

    @classmethod
    def from_session(cls, session: LunchSession) -> "SessionResponse":
        return cls(
            id=session.id,
            title=session.title,
            restaurants=session.restaurants,
            description=session.description,
            orders=session.orders,
            created_at=session.created_at,
        )


class AuthRequest(BaseModel):
    password: str
