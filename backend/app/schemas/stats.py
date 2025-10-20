from pydantic import BaseModel
from typing import Dict, List
from decimal import Decimal


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


class YearlyStats(BaseModel):
    person_id: int
    year: int
    months: int
    total_gross: float
    total_net: float
    avg_net: float
    insurance_total: float
    tax_total: float
    allowances_total: float
    bonuses_total: float
    total_actual_take_home: float
    total_non_cash_benefits: float


class FamilySummary(BaseModel):
    year: int
    persons: List[int]
    total_gross: float
    total_net: float
    insurance_total: float
    tax_total: float
    by_person: Dict[int, float]


class PersonCumulativeInsurance(BaseModel):
    person_id: int
    person_name: str
    pension_history: Decimal
    medical_history: Decimal
    housing_fund_history: Decimal
    pension_system: float
    medical_system: float
    housing_fund_system: float
    pension_total: Decimal
    medical_total: Decimal
    housing_fund_total: Decimal


class BenefitStats(BaseModel):
    year: int
    month: int
    person_id: int
    meal_allowance: float
    mid_autumn_benefit: float
    dragon_boat_benefit: float
    spring_festival_benefit: float
    total_benefits: float


class IncomeComposition(BaseModel):
    person_id: int
    year: int
    month: int
    base_salary: float
    performance_salary: float
    high_temp_allowance: float
    low_temp_allowance: float
    computer_allowance: float
    other_income: float
    non_cash_benefits: float
    total_income: float
    base_salary_percent: float
    performance_percent: float
    allowances_percent: float
    benefits_percent: float
    other_percent: float