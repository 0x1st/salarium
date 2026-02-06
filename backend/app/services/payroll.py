from decimal import Decimal, ROUND_HALF_UP


def compute_payroll(
    *,
    base_salary,
    performance_salary,
    pension_insurance,
    medical_insurance,
    unemployment_insurance,
    critical_illness_insurance,
    enterprise_annuity,
    housing_fund,
    tax,
    custom_fields=None,  # List of dicts: [{field_type, is_non_cash, amount}, ...]
    # Accept legacy allowance fields for compatibility (deprecated, use custom_fields)
    high_temp_allowance=None,
    low_temp_allowance=None,
    meal_allowance=None,
    computer_allowance=None,
    communication_allowance=None,
    comprehensive_allowance=None,
    mid_autumn_benefit=None,
    dragon_boat_benefit=None,
    spring_festival_benefit=None,
    other_income=None,
    other_deductions=None,
    labor_union_fee=None,
    performance_deduction=None,
    **kwargs,  # Accept any other fields gracefully
):
    D = lambda v: v if isinstance(v, Decimal) else Decimal(str(v or 0))
    q = Decimal("0.01")

    base_salary = D(base_salary)
    performance_salary = D(performance_salary)

    pension_insurance = D(pension_insurance)
    medical_insurance = D(medical_insurance)
    unemployment_insurance = D(unemployment_insurance)
    critical_illness_insurance = D(critical_illness_insurance)
    enterprise_annuity = D(enterprise_annuity)
    housing_fund = D(housing_fund)
    tax = D(tax)

    # Process custom fields
    custom_income = Decimal("0")
    custom_deductions = Decimal("0")
    custom_non_cash = Decimal("0")
    custom_cash_income = Decimal("0")

    if custom_fields:
        for cf in custom_fields:
            amount = D(cf.get("amount", 0))
            field_type = cf.get("field_type", "income")
            is_non_cash = cf.get("is_non_cash", False)

            if field_type == "income":
                custom_income += amount
                if is_non_cash:
                    custom_non_cash += amount
                else:
                    custom_cash_income += amount
            elif field_type == "deduction":
                custom_deductions += amount

    # Non-cash benefits (not included in actual take-home)
    non_cash_benefits = custom_non_cash.quantize(q, rounding=ROUND_HALF_UP)

    # Total income includes base + performance + custom income
    total_income = (
        base_salary
        + performance_salary
        + custom_income
    ).quantize(q, rounding=ROUND_HALF_UP)

    # Total deductions (五险一金 + custom deductions)
    total_deductions = (
        pension_insurance
        + medical_insurance
        + unemployment_insurance
        + critical_illness_insurance
        + enterprise_annuity
        + housing_fund
        + custom_deductions
    ).quantize(q, rounding=ROUND_HALF_UP)

    gross_income = total_income
    net_income = (gross_income - total_deductions - tax).quantize(q, rounding=ROUND_HALF_UP)

    # Actual take-home = cash income - deductions - tax
    # Excludes non-cash benefits
    actual_take_home = (
        base_salary
        + performance_salary
        + custom_cash_income
        - total_deductions
        - tax
    ).quantize(q, rounding=ROUND_HALF_UP)

    return {
        "total_income": total_income,
        "total_deductions": total_deductions,
        "gross_income": gross_income,
        "tax": tax.quantize(q, rounding=ROUND_HALF_UP),
        "net_income": net_income,
        "actual_take_home": actual_take_home,
        "non_cash_benefits": non_cash_benefits,
    }
