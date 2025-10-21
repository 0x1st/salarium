from pydantic import BaseModel
from typing import Dict, List, Optional
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
    meal_allowance: float
    other_income: float
    non_cash_benefits: float
    total_income: float
    base_salary_percent: float
    performance_percent: float
    allowances_percent: float
    benefits_percent: float
    other_percent: float


class MonthlyNetIncome(BaseModel):
    year: int
    month: int
    net_income: float


class GrossVsNetMonthly(BaseModel):
    year: int
    month: int
    gross_income: float
    net_income: float


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
    total: float


class DeductionsBreakdown(BaseModel):
    summary: List[DeductionsBreakdownItem]
    monthly: List[DeductionsMonthly]


class ContributionsCumulativePoint(BaseModel):
    year: int
    month: int
    pension_cumulative: float
    medical_cumulative: float
    housing_fund_cumulative: float


class ContributionsCumulative(BaseModel):
    person_id: int
    person_name: str
    pension_history: Decimal
    medical_history: Decimal
    housing_fund_history: Decimal
    points: List[ContributionsCumulativePoint]
    pension_system_total: float
    medical_system_total: float
    housing_fund_system_total: float
    pension_total: float
    medical_total: float
    housing_fund_total: float


class MonthlyTableRow(BaseModel):
    person_id: int
    person_name: str
    year: int
    month: int
    # Income fields
    base_salary: float
    performance_salary: float
    high_temp_allowance: float
    low_temp_allowance: float
    computer_allowance: float
    meal_allowance: float
    mid_autumn_benefit: float
    dragon_boat_benefit: float
    spring_festival_benefit: float
    other_income: float
    # Deduction fields
    pension_insurance: float
    medical_insurance: float
    unemployment_insurance: float
    critical_illness_insurance: float
    enterprise_annuity: float
    housing_fund: float
    other_deductions: float
    # Totals
    income_total: float
    deductions_total: float
    benefits_total: float
    actual_take_home: float
    net_income: float
    tax: float
    note: Optional[str]


class AnnualTableRow(BaseModel):
    person_id: int
    person_name: str
    year: int
    # Income totals
    base_salary_total: float
    performance_salary_total: float
    high_temp_allowance_total: float
    low_temp_allowance_total: float
    computer_allowance_total: float
    meal_allowance_total: float
    mid_autumn_benefit_total: float
    dragon_boat_benefit_total: float
    spring_festival_benefit_total: float
    other_income_total: float
    # Deduction totals
    pension_insurance_total: float
    medical_insurance_total: float
    unemployment_insurance_total: float
    critical_illness_insurance_total: float
    enterprise_annuity_total: float
    housing_fund_total: float
    other_deductions_total: float
    # Grand totals
    income_total: float
    deductions_total: float
    benefits_total: float
    actual_take_home_total: float
    yoy_growth: Optional[float]
