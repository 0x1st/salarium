from typing import Dict, Optional
from pydantic import BaseModel, Field


class SalaryCreate(BaseModel):
    year: int
    month: int
    base_salary: float = 0.0
    performance_percent: Optional[float] = Field(default=None, description="比例，例如 0.1 表示 10%")
    performance_fixed: Optional[float] = None
    allowances: Optional[Dict[str, float]] = None
    bonuses: Optional[Dict[str, float]] = None
    deductions: Optional[Dict[str, float]] = None
    ins_pension: float = 0.0
    ins_medical: float = 0.0
    ins_unemployment: float = 0.0
    ins_injury: float = 0.0
    ins_maternity: float = 0.0
    housing_fund: float = 0.0
    tax: float = 0.0
    auto_tax: bool = False
    note: Optional[str] = None


class SalaryUpdate(BaseModel):
    base_salary: Optional[float] = None
    performance_percent: Optional[float] = None
    performance_fixed: Optional[float] = None
    allowances: Optional[Dict[str, float]] = None
    bonuses: Optional[Dict[str, float]] = None
    deductions: Optional[Dict[str, float]] = None
    ins_pension: Optional[float] = None
    ins_medical: Optional[float] = None
    ins_unemployment: Optional[float] = None
    ins_injury: Optional[float] = None
    ins_maternity: Optional[float] = None
    housing_fund: Optional[float] = None
    tax: Optional[float] = None
    auto_tax: Optional[bool] = None
    note: Optional[str] = None


class SalaryOut(BaseModel):
    id: int
    year: int
    month: int
    base_salary: float
    performance: float
    allowances_total: float
    bonuses_total: float
    deductions_total: float
    insurance_total: float
    tax: float
    gross_income: float
    net_income: float
    note: Optional[str] = None