from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, field_validator


# -------- Auth --------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    organization_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInToken(BaseModel):
    id: int
    email: EmailStr
    organization_id: int


# -------- Product --------

class ProductBase(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    quantity_on_hand: int = 0
    cost_price: float = 0
    selling_price: float = 0
    low_stock_threshold: Optional[int] = None

    @field_validator("quantity_on_hand", "cost_price", "selling_price", "low_stock_threshold")
    @classmethod
    def non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    quantity_on_hand: Optional[int] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    low_stock_threshold: Optional[int] = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_low_stock: bool
    effective_threshold: int

    class Config:
        from_attributes = True


# -------- Dashboard --------

class DashboardStats(BaseModel):
    total_products: int
    total_inventory_units: int
    low_stock_products: List[ProductOut]


# -------- Settings --------

class SettingsOut(BaseModel):
    default_low_stock_threshold: int


class SettingsUpdate(BaseModel):
    default_low_stock_threshold: int

    @field_validator("default_low_stock_threshold")
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("default_low_stock_threshold must be positive")
        return v