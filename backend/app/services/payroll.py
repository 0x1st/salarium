def compute_payroll(
    *,
    base_salary: float,
    performance_salary: float,
    high_temp_allowance: float,
    low_temp_allowance: float,
    computer_allowance: float,
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
):
    # Non-cash benefits (not included in actual take-home)
    non_cash_benefits = (
        meal_allowance
        + mid_autumn_benefit
        + dragon_boat_benefit
        + spring_festival_benefit
    )
    
    # Total income includes everything
    total_income = (
        base_salary
        + performance_salary
        + high_temp_allowance
        + low_temp_allowance
        + computer_allowance
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
    net_income = gross_income - total_deductions - tax
    
    # Actual take-home = cash income - deductions - tax
    # Excludes non-cash benefits (meal, festival benefits)
    actual_take_home = (
        base_salary
        + performance_salary
        + high_temp_allowance
        + low_temp_allowance
        + computer_allowance
        + other_income
        - total_deductions
    )
    
    return {
        "total_income": total_income,
        "total_deductions": total_deductions,
        "gross_income": gross_income,
        "tax": tax,
        "net_income": net_income,
        "actual_take_home": actual_take_home,
        "non_cash_benefits": non_cash_benefits,
    }