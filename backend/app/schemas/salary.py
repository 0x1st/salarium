from typing import Optional
from pydantic import BaseModel


class SalaryCreate(BaseModel):
    year: int
    month: int
    base_salary: float = 0.0
    performance_salary: float = 0.0
    high_temp_allowance: float = 0.0
    low_temp_allowance: float = 0.0
    meal_allowance: float = 0.0
    mid_autumn_benefit: float = 0.0
    dragon_boat_benefit: float = 0.0
    spring_festival_benefit: float = 0.0
    other_income: float = 0.0
    pension_insurance: float = 0.0
    medical_insurance: float = 0.0
    unemployment_insurance: float = 0.0
    critical_illness_insurance: float = 0.0
    enterprise_annuity: float = 0.0
    housing_fund: float = 0.0
    other_deductions: float = 0.0
    tax: float = 0.0
    note: Optional[str] = None


class SalaryUpdate(BaseModel):
    base_salary: Optional[float] = None
    performance_salary: Optional[float] = None
    high_temp_allowance: Optional[float] = None
    low_temp_allowance: Optional[float] = None
    meal_allowance: Optional[float] = None
    mid_autumn_benefit: Optional[float] = None
    dragon_boat_benefit: Optional[float] = None
    spring_festival_benefit: Optional[float] = None
    other_income: Optional[float] = None
    pension_insurance: Optional[float] = None
    medical_insurance: Optional[float] = None
    unemployment_insurance: Optional[float] = None
    critical_illness_insurance: Optional[float] = None
    enterprise_annuity: Optional[float] = None
    housing_fund: Optional[float] = None
    other_deductions: Optional[float] = None
    tax: Optional[float] = None
    note: Optional[str] = None


class SalaryOut(BaseModel):
    id: int
    year: int
    month: int
    base_salary: float
    performance_salary: float
    high_temp_allowance: float
    low_temp_allowance: float
    meal_allowance: float
    mid_autumn_benefit: float
    dragon_boat_benefit: float
    spring_festival_benefit: float
    other_income: float
    pension_insurance: float
    medical_insurance: float
    unemployment_insurance: float
    critical_illness_insurance: float
    enterprise_annuity: float
    housing_fund: float
    other_deductions: float
    tax: float
    total_income: float
    total_deductions: float
    gross_income: float
    net_income: float
    note: Optional[str] = None