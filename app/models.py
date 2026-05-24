from typing import Literal, Optional
from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Username must not be empty")
        if len(v) > 64:
            raise ValueError("Username too long (max 64 chars)")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: float
    name: str
    category: str
    date: str  # ISO-8601 date string e.g. "2026-05-24"

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return round(v, 2)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be empty")
        return v

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: str) -> str:
        return v.strip()


class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    name: str
    category: str
    date: str
    created_at: str


class CategoryBreakdown(BaseModel):
    category: str
    total: float


class SummaryOut(BaseModel):
    total_income: float
    total_expenses: float
    expense_by_category: list[CategoryBreakdown]
