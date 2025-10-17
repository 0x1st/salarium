from typing import Tuple


def compute_tax_auto(gross: float, total_deductions: float) -> float:
    taxable = max(0.0, gross - total_deductions - 5000.0)
    brackets: Tuple[Tuple[float, float, float], ...] = (
        (36000, 0.03, 0),
        (144000, 0.10, 2520),
        (300000, 0.20, 16920),
        (420000, 0.25, 31920),
        (660000, 0.30, 52920),
        (960000, 0.35, 85920),
        (float("inf"), 0.45, 181920),
    )
    for limit, rate, quick in brackets:
        if taxable <= limit:
            return taxable * rate - quick
    return 0.0


def compute_payroll(
    *,
    base_salary: float,
    performance_salary: float,
    high_temp_allowance: float,
    low_temp_allowance: float,
    meal_allowance: float,
    mid_autumn_benefit: float,
    dragon_boat_benefit: float,
    spring_festival_benefit: float,
    other_income: float,
    pension_insurance: float,
    medical_insurance: float,
    unemployment_insurance: float,
    critical_illness_insurance: float,
    enterprise_annuity: float,
    housing_fund: float,
    other_deductions: float,
    tax: float,
    auto_tax: bool,
):
    total_income = (
        base_salary
        + performance_salary
        + high_temp_allowance
        + low_temp_allowance
        + meal_allowance
        + mid_autumn_benefit
        + dragon_boat_benefit
        + spring_festival_benefit
        + other_income
    )
    
    total_deductions = (
        pension_insurance
        + medical_insurance
        + unemployment_insurance
        + critical_illness_insurance
        + enterprise_annuity
        + housing_fund
        + other_deductions
    )
    
    gross_income = total_income
    tax_final = compute_tax_auto(gross_income, total_deductions) if auto_tax else tax
    net_income = gross_income - total_deductions - tax_final
    
    return {
        "total_income": total_income,
        "total_deductions": total_deductions,
        "gross_income": gross_income,
        "tax": tax_final,
        "net_income": net_income,
    }