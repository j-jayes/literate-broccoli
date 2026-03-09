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
    description: Optional[str] = None


class ScrapeRequest(BaseModel):
    restaurant_name: str
    menu_url: Optional[str] = None


class ScrapeResponse(BaseModel):
    items: list[MenuItem]


class CreateSessionRequest(BaseModel):
    restaurant_name: str
    description: Optional[str] = None
    items: list[MenuItem]


class SubmitOrderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    selected_items: list[str] = Field(min_length=1)


class Order(BaseModel):
    name: str
    items: list[str]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class LunchSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    restaurant_name: str
    description: Optional[str] = None
    items: list[MenuItem]
    orders: dict[str, Order] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionResponse(BaseModel):
    id: UUID
    restaurant_name: str
    description: Optional[str] = None
    items: list[MenuItem]
    orders: dict[str, Order]
    created_at: datetime


class AuthRequest(BaseModel):
    password: str
