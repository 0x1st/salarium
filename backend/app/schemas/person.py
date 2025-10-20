from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PersonCreate(BaseModel):
    name: str
    note: Optional[str] = None
    pension_history: Decimal = Decimal("0.00")
    medical_history: Decimal = Decimal("0.00")
    housing_fund_history: Decimal = Decimal("0.00")


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None
    pension_history: Optional[Decimal] = None
    medical_history: Optional[Decimal] = None
    housing_fund_history: Optional[Decimal] = None


class PersonOut(BaseModel):
    id: int
    name: str
    note: Optional[str] = None
    pension_history: Decimal
    medical_history: Decimal
    housing_fund_history: Decimal