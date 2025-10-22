from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP


def _q2(v: Optional[Decimal]) -> Optional[Decimal]:
    if v is None:
        return None
    if not isinstance(v, Decimal):
        v = Decimal(str(v))
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    note: Optional[str] = Field(default=None, max_length=255)
    pension_history: Decimal = Field(default=Decimal("0.00"), ge=0)
    medical_history: Decimal = Field(default=Decimal("0.00"), ge=0)
    housing_fund_history: Decimal = Field(default=Decimal("0.00"), ge=0)

    @field_validator("pension_history", "medical_history", "housing_fund_history", mode="before")
    @classmethod
    def _quantize_create(cls, v):
        return _q2(v)


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    note: Optional[str] = Field(default=None, max_length=255)
    pension_history: Optional[Decimal] = Field(default=None, ge=0)
    medical_history: Optional[Decimal] = Field(default=None, ge=0)
    housing_fund_history: Optional[Decimal] = Field(default=None, ge=0)

    @field_validator("pension_history", "medical_history", "housing_fund_history", mode="before")
    @classmethod
    def _quantize_update(cls, v):
        return _q2(v)


class PersonOut(BaseModel):
    id: int
    name: str
    note: Optional[str] = None
    pension_history: Decimal
    medical_history: Decimal
    housing_fund_history: Decimal
