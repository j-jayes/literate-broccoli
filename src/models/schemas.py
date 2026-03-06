"""Pydantic models for menu extraction and Adaptive Card generation."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class MenuCategory(str, Enum):
    main = "main"
    side = "side"
    drink = "drink"
    dessert = "dessert"
    other = "other"


def normalize_category(value: Any) -> MenuCategory:
    if isinstance(value, MenuCategory):
        return value
    if value is None:
        return MenuCategory.other
    text = str(value).strip().lower()
    if not text:
        return MenuCategory.other
    if text in {"main", "mains", "meal", "entree", "burger", "burgers"}:
        return MenuCategory.main
    if "side" in text or text in {"extra", "extras", "dip", "dips"}:
        return MenuCategory.side
    if "drink" in text or "beverage" in text or text in {"drinks", "dryck", "drycker"}:
        return MenuCategory.drink
    if "dessert" in text or "sweet" in text:
        return MenuCategory.dessert
    return MenuCategory.other


class ExtractedMenuItem(BaseModel):
    name: str = Field(min_length=1)
    price: Optional[Decimal] = None
    category: MenuCategory = MenuCategory.other
    description: Optional[str] = None

    @field_validator("category", mode="before")
    @classmethod
    def _validate_category(cls, v: Any) -> MenuCategory:
        return normalize_category(v)


class ExtractedMenu(BaseModel):
    """Wrapper for LLM structured output."""
    items: list[ExtractedMenuItem]
