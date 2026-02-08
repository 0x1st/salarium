from typing import Optional, Dict
from pydantic import BaseModel


class SalaryCreate(BaseModel):
    year: int
    month: int
    base_salary: float = 0.0
    performance_salary: float = 0.0
    pension_insurance: float = 0.0
    medical_insurance: float = 0.0
    unemployment_insurance: float = 0.0
    critical_illness_insurance: float = 0.0
    enterprise_annuity: float = 0.0
    housing_fund: float = 0.0
    tax: float = 0.0
    note: Optional[str] = None
    custom_fields: Optional[Dict[str, float]] = None  # {field_key: amount}


class SalaryUpdate(BaseModel):
    base_salary: Optional[float] = None
    performance_salary: Optional[float] = None
    pension_insurance: Optional[float] = None
    medical_insurance: Optional[float] = None
    unemployment_insurance: Optional[float] = None
    critical_illness_insurance: Optional[float] = None
    enterprise_annuity: Optional[float] = None
    housing_fund: Optional[float] = None
    tax: Optional[float] = None
    note: Optional[str] = None
    custom_fields: Optional[Dict[str, float]] = None  # {field_key: amount}


class SalaryOut(BaseModel):
    id: int
    year: int
    month: int
    base_salary: float
    performance_salary: float
    pension_insurance: float
    medical_insurance: float
    unemployment_insurance: float
    critical_illness_insurance: float
    enterprise_annuity: float
    housing_fund: float
    insurance_total: float
    tax: float
    total_income: float
    total_deductions: float
    gross_income: float
    net_income: float
    actual_take_home: float
    non_cash_benefits: float
    note: Optional[str] = None
    custom_fields: Dict[str, float] = {}  # {field_key: amount}
