from typing import Dict, Optional, Tuple


def sum_map(values: Optional[Dict[str, float]]) -> float:
    return sum(values.values()) if values else 0.0


def compute_performance(base_salary: float, percent: Optional[float], fixed: Optional[float]) -> float:
    perf_by_percent = base_salary * percent if percent is not None else 0.0
    perf_by_fixed = fixed if fixed is not None else 0.0
    return perf_by_percent + perf_by_fixed


def compute_insurance_total(
    pension: float,
    medical: float,
    unemployment: float,
    injury: float,
    maternity: float,
    housing_fund: float,
) -> float:
    return sum([pension, medical, unemployment, injury, maternity, housing_fund])


def compute_tax_auto(gross: float, insurance_total: float) -> float:
    taxable = max(0.0, gross - insurance_total - 5000.0)
    # 简化的中国个税速算扣除法（示意用，非精确）
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
    performance_percent: Optional[float],
    performance_fixed: Optional[float],
    allowances: Optional[Dict[str, float]],
    bonuses: Optional[Dict[str, float]],
    deductions: Optional[Dict[str, float]],
    ins_pension: float,
    ins_medical: float,
    ins_unemployment: float,
    ins_injury: float,
    ins_maternity: float,
    housing_fund: float,
    tax: float,
    auto_tax: bool,
):
    performance = compute_performance(base_salary, performance_percent, performance_fixed)
    allowances_total = sum_map(allowances)
    bonuses_total = sum_map(bonuses)
    deductions_total = sum_map(deductions)
    gross_income = base_salary + performance + allowances_total + bonuses_total
    insurance_total = compute_insurance_total(
        ins_pension, ins_medical, ins_unemployment, ins_injury, ins_maternity, housing_fund
    )
    tax_final = compute_tax_auto(gross_income, insurance_total) if auto_tax else tax
    net_income = gross_income - insurance_total - deductions_total - tax_final
    return {
        "performance": performance,
        "allowances_total": allowances_total,
        "bonuses_total": bonuses_total,
        "deductions_total": deductions_total,
        "gross_income": gross_income,
        "insurance_total": insurance_total,
        "tax": tax_final,
        "net_income": net_income,
    }