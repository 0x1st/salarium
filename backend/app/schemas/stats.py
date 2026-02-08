from pydantic import BaseModel
from typing import List


class MonthlyStats(BaseModel):
    person_id: int
    year: int
    month: int
    base_salary: float
    performance: float
    allowances_total: float
    bonuses_total: float
    insurance_total: float
    tax: float
    gross_income: float
    net_income: float
    actual_take_home: float
    non_cash_benefits: float


class BreakdownItem(BaseModel):
    key: str
    label: str
    amount: float


class IncomeComposition(BaseModel):
    person_id: int
    year: int
    month: int
    base_salary: float
    performance_salary: float
    high_temp_allowance: float
    low_temp_allowance: float
    computer_allowance: float
    communication_allowance: float
    comprehensive_allowance: float
    meal_allowance: float
    mid_autumn_benefit: float
    dragon_boat_benefit: float
    spring_festival_benefit: float
    other_income: float
    other_income_base: float
    non_cash_benefits: float
    custom_income_items: list[BreakdownItem] = []
    custom_non_cash_items: list[BreakdownItem] = []
    total_income: float
    base_salary_percent: float
    performance_percent: float
    allowances_percent: float
    benefits_percent: float
    other_percent: float


class DeductionsBreakdownItem(BaseModel):
    category: str
    amount: float
    percent: float


class DeductionsMonthly(BaseModel):
    year: int
    month: int
    pension_insurance: float
    medical_insurance: float
    unemployment_insurance: float
    critical_illness_insurance: float
    enterprise_annuity: float
    housing_fund: float
    other_deductions: float
    labor_union_fee: float
    performance_deduction: float
    total: float


class DeductionsBreakdown(BaseModel):
    summary: List[DeductionsBreakdownItem]
    monthly: List[DeductionsMonthly]
