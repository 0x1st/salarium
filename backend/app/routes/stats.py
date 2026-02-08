from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Depends
from decimal import Decimal

from ..models import (
    SalaryRecord,
    Person,
    CustomSalaryValue,
    INCOME_CATEGORIES,
    DEDUCTION_CATEGORIES,
)
from ..schemas.stats import (
    MonthlyStats, YearlyStats, FamilySummary,
    PersonCumulativeInsurance, BenefitStats, IncomeComposition,
    MonthlyNetIncome, GrossVsNetMonthly,
    DeductionsBreakdown, DeductionsMonthly, DeductionsBreakdownItem,
    ContributionsCumulative, ContributionsCumulativePoint,
    MonthlyTableRow, AnnualTableRow, AnnualMonthlyRow,
    CategorySummary, CategorySummaryItem,
)
from ..utils.auth import get_current_user
from ..services.payroll import compute_payroll


router = APIRouter()


# Helpers for stats calculations aligned with the unified calculation spec
def _D(v):
    return v if isinstance(v, Decimal) else Decimal(str(v or 0))

# Safe field accessor - handles both direct fields and missing custom fields
def _F(record, field_name, default=0):
    """Safely get a field value from record, returns default if missing."""
    try:
        return getattr(record, field_name, default)
    except AttributeError:
        return default


async def load_custom_fields_for_payroll(
    record_ids: List[int],
) -> Dict[int, List[dict]]:
    """Batch load custom field info for payroll calculation."""
    if not record_ids:
        return {}
    values = await CustomSalaryValue.filter(
        salary_record_id__in=record_ids
    ).prefetch_related("salary_field").all()
    payroll_map: Dict[int, List[dict]] = {}
    for v in values:
        payroll_map.setdefault(v.salary_record_id, []).append(
            {
                "field_type": v.salary_field.field_type,
                "is_non_cash": v.salary_field.is_non_cash,
                "amount": float(v.amount),
            }
        )
    return payroll_map


# Allowances used for net income (exclude meal allowance as per spec)
# net = base + performance + high + low + computer - deductions
# meal allowance is not counted toward actual take-home

def _allowances_sum_net(r: SalaryRecord) -> Decimal:
    return (
        _D(_F(r, "high_temp_allowance"))
        + _D(_F(r, "low_temp_allowance"))
        + _D(_F(r, "computer_allowance"))
        + _D(_F(r, "communication_allowance"))
        + _D(_F(r, "comprehensive_allowance"))
    )

# Allowances for composition/gross (include meal allowance)

def _allowances_sum_full(r: SalaryRecord) -> Decimal:
    return (
        _D(_F(r, "high_temp_allowance"))
        + _D(_F(r, "low_temp_allowance"))
        + _D(_F(r, "meal_allowance"))
        + _D(_F(r, "computer_allowance"))
        + _D(_F(r, "communication_allowance"))
        + _D(_F(r, "comprehensive_allowance"))
    )

# Benefits grouping (festival welfare only; excludes meal allowance)

def _benefits_sum(r: SalaryRecord) -> Decimal:
    return (
        _D(_F(r, "mid_autumn_benefit"))
        + _D(_F(r, "dragon_boat_benefit"))
        + _D(_F(r, "spring_festival_benefit"))
    )


def _gross_income_for_net_charts(r: SalaryRecord) -> Decimal:
    """Gross income for waterfall and gross-vs-net charts.

    Excludes meal allowance and festival benefits per unified spec.
    应发 = 基本工资 + 绩效工资 + 高温补贴 + 低温补贴 + 电脑补贴 + 其他
    （排除：餐补、三节福利）
    """
    return (
        _D(r.base_salary)
        + _D(r.performance_salary)
        + _allowances_sum_net(r)  # excludes meal allowance
        + _D(_F(r, "other_income"))
    )


def _deductions_sum(r: SalaryRecord) -> Decimal:
    return (
        _D(r.pension_insurance)
        + _D(r.medical_insurance)
        + _D(r.unemployment_insurance)
        + _D(r.critical_illness_insurance)
        + _D(r.enterprise_annuity)
        + _D(r.housing_fund)
        + _D(_F(r, "other_deductions"))
        + _D(_F(r, "labor_union_fee"))
        + _D(_F(r, "performance_deduction"))
    )


def _unified_net_income(r: SalaryRecord) -> Decimal:
    """Net income according to unified spec:
    net = base + performance + high + low + computer - (all deductions)
    Note: excludes meal/benefits and excludes other_income and tax.
    """
    return (
        _D(r.base_salary)
        + _D(r.performance_salary)
        + _allowances_sum_net(r)
        - _deductions_sum(r)
    )


def _gross_income_full(r: SalaryRecord) -> Decimal:
    """Gross income for charts: sum of all income incl. non-cash and other income."""
    return (
        _D(r.base_salary)
        + _D(r.performance_salary)
        + _allowances_sum_full(r)
        + _benefits_sum(r)
        + _D(_F(r, "other_income"))
    )


def _ordered_categories(categories, totals):
    ordered_keys = [k for k, _ in categories if k in totals]
    extras = sorted(k for k in totals.keys() if k not in ordered_keys)
    return ordered_keys + extras


def _ym_num(y: int, m: int) -> int:
    return y * 100 + m


def _parse_range(range_str: str) -> (int, int):
    """Parse a flexible range string into start/end numeric YYYYMM bounds (inclusive).
    Accepted formats:
    - '2024' -> 202401..202412
    - '2024-03' -> 202403..202403
    - '2024-01..2024-06', '2024-01:2024-06', '2024-01,2024-06', '2024-01_2024-06'
    """
    s = (range_str or "").strip()
    if not s:
        return (0, 999999)

    def parse_one(part: str, is_start: bool) -> (int, int):
        p = part.strip()
        if not p:
            return (0, 1) if is_start else (9999, 12)
        if len(p) == 4 and p.isdigit():
            y = int(p)
            return (y, 1) if is_start else (y, 12)
        # Expect YYYY-MM
        if "-" in p:
            try:
                y_str, m_str = p.split("-", 1)
                y = int(y_str)
                m = int(m_str)
                return (y, m)
            except Exception:
                pass
        # Fallback
        return (0, 1) if is_start else (9999, 12)

    sep = None
    for candidate in ("..", ":", ",", "_"):
        if candidate in s:
            sep = candidate
            break
    if not sep:
        y, m = parse_one(s, True)
        return (_ym_num(y, m), _ym_num(y, m))

    left, right = s.split(sep, 1)
    y1, m1 = parse_one(left, True)
    y2, m2 = parse_one(right, False)
    return (_ym_num(y1, m1), _ym_num(y2, m2))


def _apply_range(
    recs: List[SalaryRecord],
    range_str: Optional[str],
) -> List[SalaryRecord]:
    if not range_str:
        return recs
    start_num, end_num = _parse_range(range_str)
    return [r for r in recs if start_num <= _ym_num(r.year, r.month) <= end_num]


def _salary_query(
    user_id: int,
    person_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
):
    q = SalaryRecord.filter(person__user_id=user_id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    return q


def _payroll_args(r: SalaryRecord, custom_fields: Optional[List[dict]]):
    return dict(
        base_salary=r.base_salary,
        performance_salary=r.performance_salary,
        high_temp_allowance=_F(r, "high_temp_allowance"),
        low_temp_allowance=_F(r, "low_temp_allowance"),
        computer_allowance=_F(r, "computer_allowance"),
        meal_allowance=_F(r, "meal_allowance"),
        mid_autumn_benefit=_F(r, "mid_autumn_benefit"),
        dragon_boat_benefit=_F(r, "dragon_boat_benefit"),
        spring_festival_benefit=_F(r, "spring_festival_benefit"),
        other_income=_F(r, "other_income"),
        comprehensive_allowance=_F(r, "comprehensive_allowance"),
        pension_insurance=r.pension_insurance,
        medical_insurance=r.medical_insurance,
        unemployment_insurance=r.unemployment_insurance,
        critical_illness_insurance=r.critical_illness_insurance,
        enterprise_annuity=r.enterprise_annuity,
        housing_fund=r.housing_fund,
        other_deductions=_F(r, "other_deductions"),
        labor_union_fee=_F(r, "labor_union_fee"),
        performance_deduction=_F(r, "performance_deduction"),
        tax=r.tax,
        custom_fields=custom_fields or [],
    )


@router.get("/monthly", response_model=List[MonthlyStats])
async def monthly_stats(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    q = _salary_query(user.id, person_id=person_id, year=year, month=month)
    recs = await q.all()
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])
    result: List[MonthlyStats] = []
    for r in recs:
        calc = compute_payroll(**_payroll_args(r, custom_payroll_map.get(r.id)))
        allowances_total = (
            _F(r, "high_temp_allowance")
            + _F(r, "low_temp_allowance")
            + _F(r, "computer_allowance")
            + _F(r, "communication_allowance")
            + _F(r, "comprehensive_allowance")
        )
        insurance_total = (
            r.pension_insurance
            + r.medical_insurance
            + r.unemployment_insurance
            + r.critical_illness_insurance
            + r.enterprise_annuity
            + r.housing_fund
        )
        result.append(
            MonthlyStats(
                person_id=r.person_id,
                year=r.year,
                month=r.month,
                base_salary=r.base_salary,
                performance=r.performance_salary,
                allowances_total=allowances_total,
                bonuses_total=0.0,
                insurance_total=insurance_total,
                tax=calc["tax"],
                gross_income=calc["gross_income"],
                net_income=calc["net_income"],
                actual_take_home=calc["actual_take_home"],
                non_cash_benefits=calc["non_cash_benefits"],
            )
        )
    return result


@router.get("/yearly", response_model=List[YearlyStats])
async def yearly_stats(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: int = Query(...),
):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = {p.id for p in persons}
    if person_id and person_id not in person_ids:
        raise HTTPException(status_code=404, detail="人员不存在")
    if person_id:
        person_ids = {person_id}
    recs = await SalaryRecord.filter(person_id__in=list(person_ids), year=year).all()
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])
    stats_map = {}
    for r in recs:
        calc = compute_payroll(**_payroll_args(r, custom_payroll_map.get(r.id)))
        allowances_total = (
            _F(r, "high_temp_allowance")
            + _F(r, "low_temp_allowance")
            + _F(r, "computer_allowance")
            + _F(r, "communication_allowance")
            + _F(r, "comprehensive_allowance")
        )
        bonuses_total = (
            _F(r, "mid_autumn_benefit")
            + _F(r, "dragon_boat_benefit")
            + _F(r, "spring_festival_benefit")
            + _F(r, "other_income")
        )
        insurance_total = (
            r.pension_insurance
            + r.medical_insurance
            + r.unemployment_insurance
            + r.critical_illness_insurance
            + r.enterprise_annuity
            + r.housing_fund
        )

        s = stats_map.get(r.person_id, {
            "months": 0,
            "gross": Decimal("0"),
            "net": Decimal("0"),
            "insurance": Decimal("0"),
            "tax": Decimal("0"),
            "allowances": Decimal("0"),
            "bonuses": Decimal("0"),
            "actual_take_home": Decimal("0"),
            "non_cash_benefits": Decimal("0"),
        })
        s["months"] += 1
        s["gross"] += calc["gross_income"]
        s["net"] += calc["net_income"]
        s["insurance"] += insurance_total
        s["tax"] += calc["tax"]
        s["allowances"] += allowances_total
        s["actual_take_home"] += calc["actual_take_home"]
        s["non_cash_benefits"] += calc["non_cash_benefits"]
        s["bonuses"] += bonuses_total
        stats_map[r.person_id] = s
    result: List[YearlyStats] = []
    for pid, s in stats_map.items():
        avg_net = s["net"] / s["months"] if s["months"] else Decimal("0")
        result.append(
            YearlyStats(
                person_id=pid,
                year=year,
                months=s["months"],
                total_gross=s["gross"],
                total_net=s["net"],
                avg_net=avg_net,
                insurance_total=s["insurance"],
                tax_total=s["tax"],
                allowances_total=s["allowances"],
                bonuses_total=s["bonuses"],
                total_actual_take_home=s["actual_take_home"],
                total_non_cash_benefits=s["non_cash_benefits"],
            )
        )
    return result


@router.get("/family", response_model=FamilySummary)
async def family_summary(user=Depends(get_current_user), year: int = Query(...)):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = [p.id for p in persons]
    recs = await SalaryRecord.filter(person_id__in=person_ids, year=year).all()
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])
    totals = {pid: Decimal("0") for pid in person_ids}
    insurance_total = Decimal("0")
    tax_total = Decimal("0")
    total_gross = Decimal("0")
    total_net = Decimal("0")
    for r in recs:
        calc = compute_payroll(**_payroll_args(r, custom_payroll_map.get(r.id)))
        insurance_calc = (
            r.pension_insurance
            + r.medical_insurance
            + r.unemployment_insurance
            + r.critical_illness_insurance
            + r.enterprise_annuity
            + r.housing_fund
        )
        totals[r.person_id] += calc["net_income"]
        insurance_total += insurance_calc
        tax_total += calc["tax"]
        total_gross += calc["gross_income"]
        total_net += calc["net_income"]
    return FamilySummary(
        year=year,
        persons=person_ids,
        total_gross=total_gross,
        total_net=total_net,
        insurance_total=insurance_total,
        tax_total=tax_total,
        by_person=totals,
    )


@router.get("/cumulative-insurance", response_model=List[PersonCumulativeInsurance])
async def cumulative_insurance(user=Depends(get_current_user)):
    """Get cumulative insurance and housing fund for all persons"""
    persons = await Person.filter(user_id=user.id).all()
    result: List[PersonCumulativeInsurance] = []

    for person in persons:
        # Get all salary records for this person
        recs = await SalaryRecord.filter(person_id=person.id).all()

        # Calculate system totals
        pension_system = sum(r.pension_insurance for r in recs)
        medical_system = sum(r.medical_insurance for r in recs)
        housing_fund_system = sum(r.housing_fund for r in recs)

        # Calculate total = history + system
        pension_total = Decimal(str(person.pension_history)) + Decimal(
            str(pension_system)
        )
        medical_total = Decimal(str(person.medical_history)) + Decimal(
            str(medical_system)
        )
        housing_fund_total = Decimal(str(person.housing_fund_history)) + Decimal(
            str(housing_fund_system)
        )

        result.append(
            PersonCumulativeInsurance(
                person_id=person.id,
                person_name=person.name,
                pension_history=person.pension_history,
                medical_history=person.medical_history,
                housing_fund_history=person.housing_fund_history,
                pension_system=pension_system,
                medical_system=medical_system,
                housing_fund_system=housing_fund_system,
                pension_total=pension_total,
                medical_total=medical_total,
                housing_fund_total=housing_fund_total,
            )
        )

    return result


@router.get("/benefits", response_model=List[BenefitStats])
async def benefit_stats(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
):
    """Get non-cash benefit statistics"""
    q = _salary_query(user.id, person_id=person_id, year=year)
    recs = await q.all()
    result: List[BenefitStats] = []

    for r in recs:
        total_benefits = (
            _F(r, "meal_allowance")
            + _F(r, "mid_autumn_benefit")
            + _F(r, "dragon_boat_benefit")
            + _F(r, "spring_festival_benefit")
        )
        result.append(
            BenefitStats(
                year=r.year,
                month=r.month,
                person_id=r.person_id,
                meal_allowance=_F(r, "meal_allowance"),
                mid_autumn_benefit=_F(r, "mid_autumn_benefit"),
                dragon_boat_benefit=_F(r, "dragon_boat_benefit"),
                spring_festival_benefit=_F(r, "spring_festival_benefit"),
                total_benefits=total_benefits,
            )
        )

    return result


@router.get("/income-composition", response_model=List[IncomeComposition])
async def income_composition(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12 或 2024-01,2024-12"
    ),
):
    """Get income composition with grouped categories per latest spec.
    补贴 = 高温补贴 + 低温补贴 + 餐补 + 电脑补贴
    福利 = 中秋福利 + 端午福利 + 春节福利
    """
    q = _salary_query(user.id, person_id=person_id, year=year, month=month)
    recs = _apply_range(await q.all(), range)
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])

    result: List[IncomeComposition] = []

    for r in recs:
        custom_income = Decimal("0")
        custom_non_cash = Decimal("0")
        for cf in custom_payroll_map.get(r.id, []):
            amount = _D(cf.get("amount", 0))
            if cf.get("field_type") != "income":
                continue
            custom_income += amount
            if cf.get("is_non_cash"):
                custom_non_cash += amount
        custom_cash = custom_income - custom_non_cash

        allowances = float(_allowances_sum_full(r))
        benefits = float(_benefits_sum(r) + custom_non_cash)
        other_income = float(_D(_F(r, "other_income")) + custom_cash)
        total_income = float(
            _D(r.base_salary)
            + _D(r.performance_salary)
            + _D(allowances)
            + _D(benefits)
            + _D(other_income)
        )
        
        # Calculate percentages (avoid division by zero)
        if total_income > 0:
            base_salary_percent = float(
                _D(r.base_salary) / _D(total_income) * 100
            )
            performance_percent = float(
                _D(r.performance_salary) / _D(total_income) * 100
            )
            allowances_percent = float(
                _D(allowances) / _D(total_income) * 100
            )
            benefits_percent = float(
                _D(benefits) / _D(total_income) * 100
            )
            other_percent = float(_D(other_income) / _D(total_income) * 100)
        else:
            base_salary_percent = 0.0
            performance_percent = 0.0
            allowances_percent = 0.0
            benefits_percent = 0.0
            other_percent = 0.0
        
        result.append(
            IncomeComposition(
                person_id=r.person_id,
                year=r.year,
                month=r.month,
                base_salary=float(_D(r.base_salary)),
                performance_salary=float(_D(r.performance_salary)),
                high_temp_allowance=float(_D(_F(r, "high_temp_allowance"))),
                low_temp_allowance=float(_D(_F(r, "low_temp_allowance"))),
                computer_allowance=float(_D(_F(r, "computer_allowance"))),
                communication_allowance=float(
                    _D(_F(r, "communication_allowance"))
                ),
                comprehensive_allowance=float(
                    _D(_F(r, "comprehensive_allowance"))
                ),
                meal_allowance=float(_D(_F(r, "meal_allowance"))),
                other_income=other_income,
                non_cash_benefits=float(_D(benefits)),
                total_income=total_income,
                base_salary_percent=base_salary_percent,
                performance_percent=performance_percent,
                allowances_percent=allowances_percent,
                benefits_percent=benefits_percent,
                other_percent=other_percent,
            )
        )

    return result


@router.get("/categories/summary", response_model=CategorySummary)
async def categories_summary(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12"
    ),
):
    """Summary totals grouped by income/deduction category."""
    q = _salary_query(user.id, person_id=person_id, year=year, month=month)
    recs = _apply_range(await q.all(), range)

    income_totals = {k: Decimal("0") for k, _ in INCOME_CATEGORIES}
    deduction_totals = {k: Decimal("0") for k, _ in DEDUCTION_CATEGORIES}

    for r in recs:
        income_totals["base_salary"] += _D(r.base_salary)
        income_totals["performance"] += _D(r.performance_salary)
        income_totals["allowance"] += _allowances_sum_full(r)
        income_totals["welfare"] += _benefits_sum(r)
        income_totals["other_income"] += _D(_F(r, "other_income"))

        deduction_totals["insurance"] += (
            _D(r.pension_insurance)
            + _D(r.medical_insurance)
            + _D(r.unemployment_insurance)
            + _D(r.critical_illness_insurance)
            + _D(r.enterprise_annuity)
        )
        deduction_totals["housing_fund"] += _D(r.housing_fund)
        deduction_totals["tax"] += _D(r.tax)
        deduction_totals["other_deduction"] += (
            _D(_F(r, "other_deductions"))
            + _D(_F(r, "labor_union_fee"))
            + _D(_F(r, "performance_deduction"))
        )

    record_ids = [r.id for r in recs]
    if record_ids:
        values = await CustomSalaryValue.filter(
            salary_record_id__in=record_ids
        ).prefetch_related("salary_field").all()
        for v in values:
            cat = v.salary_field.category
            amount = _D(v.amount)
            if v.salary_field.field_type == "income":
                income_totals[cat] = income_totals.get(cat, Decimal("0")) + amount
            else:
                deduction_totals[cat] = deduction_totals.get(cat, Decimal("0")) + amount

    income_labels = {k: v for k, v in INCOME_CATEGORIES}
    deduction_labels = {k: v for k, v in DEDUCTION_CATEGORIES}

    income_items = []
    for key in _ordered_categories(INCOME_CATEGORIES, income_totals):
        amount = income_totals.get(key, Decimal("0"))
        if amount == 0:
            continue
        income_items.append(
            CategorySummaryItem(
                category=key, label=income_labels.get(key, key), amount=float(amount)
            )
        )

    deduction_items = []
    for key in _ordered_categories(DEDUCTION_CATEGORIES, deduction_totals):
        amount = deduction_totals.get(key, Decimal("0"))
        if amount == 0:
            continue
        deduction_items.append(
            CategorySummaryItem(
                category=key,
                label=deduction_labels.get(key, key),
                amount=float(amount),
            )
        )

    total_income = sum(income_totals.values())
    total_deduction = sum(deduction_totals.values())
    return CategorySummary(
        income=income_items,
        deduction=deduction_items,
        total_income=float(total_income),
        total_deduction=float(total_deduction),
    )


@router.get("/net-income/monthly", response_model=List[MonthlyNetIncome])
async def net_income_monthly(
    user=Depends(get_current_user),
    year: Optional[int] = Query(default=None),
    person_id: Optional[int] = Query(default=None),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12"
    ),
):
    """Monthly net income series (unified calculation)."""
    q = _salary_query(user.id, person_id=person_id, year=year)
    recs = _apply_range(await q.all(), range)

    sums = {}
    for r in recs:
        key = (r.year, r.month)
        sums[key] = sums.get(key, Decimal("0")) + _unified_net_income(r)

    result: List[MonthlyNetIncome] = []
    for (y, m) in sorted(sums.keys()):
        result.append(
            MonthlyNetIncome(year=y, month=m, net_income=float(sums[(y, m)]))
        )
    return result


@router.get("/gross-vs-net/monthly", response_model=List[GrossVsNetMonthly])
async def gross_vs_net_monthly(
    user=Depends(get_current_user),
    year: Optional[int] = Query(default=None),
    person_id: Optional[int] = Query(default=None),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12"
    ),
):
    """Monthly gross vs net income (unified net).

    应发 = 基本工资 + 绩效工资 + 高温补贴 + 低温补贴 + 电脑补贴 + 其他
    （排除：餐补、三节福利）
    实际到手 = 应发 - 扣除
    """
    q = _salary_query(user.id, person_id=person_id, year=year)
    recs = _apply_range(await q.all(), range)

    sums = {}
    for r in recs:
        key = (r.year, r.month)
        gross = _gross_income_for_net_charts(r)
        deductions = _deductions_sum(r)
        net = gross - deductions  # For waterfall: net = gross - deductions
        prev_g, prev_n = sums.get(key, (Decimal("0"), Decimal("0")))
        sums[key] = (prev_g + gross, prev_n + net)

    result: List[GrossVsNetMonthly] = []
    for (y, m) in sorted(sums.keys()):
        g, n = sums[(y, m)]
        result.append(
            GrossVsNetMonthly(
                year=y, month=m, gross_income=float(g), net_income=float(n)
            )
        )
    return result


@router.get("/deductions/breakdown", response_model=DeductionsBreakdown)
async def deductions_breakdown(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12"
    ),
):
    """Breakdown of deduction categories with monthly series and percentage share.
    支持按人员、年份、月份过滤；为兼容性保留 range，但前端已不使用。
    """
    q = _salary_query(user.id, person_id=person_id, year=year, month=month)
    recs = _apply_range(await q.all(), range)
    custom_payroll_map = await load_custom_fields_for_payroll([r.id for r in recs])

    # Summary totals by category
    categories = [
        ("养老保险", "pension_insurance"),
        ("医疗保险", "medical_insurance"),
        ("失业保险", "unemployment_insurance"),
        ("大病互助保险", "critical_illness_insurance"),
        ("企业年金", "enterprise_annuity"),
        ("住房公积金", "housing_fund"),
        ("其他扣除", "other_deductions"),
        ("工会", "labor_union_fee"),
        ("绩效扣除", "performance_deduction"),
    ]

    totals = {key: Decimal("0") for _, key in categories}
    for r in recs:
        custom_deduction = Decimal("0")
        for cf in custom_payroll_map.get(r.id, []):
            if cf.get("field_type") == "deduction":
                custom_deduction += _D(cf.get("amount", 0))
        for _, key in categories:
            if key == "other_deductions":
                totals[key] += _D(_F(r, key)) + custom_deduction
            else:
                totals[key] += _D(_F(r, key))

    grand_total = sum(totals.values()) if totals else Decimal("0")
    summary: List[DeductionsBreakdownItem] = []
    for name, key in categories:
        amount = totals[key]
        percent = float((amount / grand_total * 100) if grand_total > 0 else 0)
        summary.append(
            DeductionsBreakdownItem(
                category=name, amount=float(amount), percent=percent
            )
        )

    # Monthly series
    monthly_map = {}
    for r in recs:
        k = (r.year, r.month)
        if k not in monthly_map:
            monthly_map[k] = {key: Decimal("0") for _, key in categories}
        custom_deduction = Decimal("0")
        for cf in custom_payroll_map.get(r.id, []):
            if cf.get("field_type") == "deduction":
                custom_deduction += _D(cf.get("amount", 0))
        for _, key in categories:
            if key == "other_deductions":
                monthly_map[k][key] += _D(_F(r, key)) + custom_deduction
            else:
                monthly_map[k][key] += _D(_F(r, key))

    monthly: List[DeductionsMonthly] = []
    for (y, m) in sorted(monthly_map.keys()):
        data = monthly_map[(y, m)]
        total = sum(data.values())
        monthly.append(
            DeductionsMonthly(
                year=y,
                month=m,
                pension_insurance=float(data["pension_insurance"]),
                medical_insurance=float(data["medical_insurance"]),
                unemployment_insurance=float(data["unemployment_insurance"]),
                critical_illness_insurance=float(
                    data["critical_illness_insurance"]
                ),
                enterprise_annuity=float(data["enterprise_annuity"]),
                housing_fund=float(data["housing_fund"]),
                other_deductions=float(data["other_deductions"]),
                labor_union_fee=float(data["labor_union_fee"]),
                performance_deduction=float(data["performance_deduction"]),
                total=float(total),
            )
        )

    return DeductionsBreakdown(summary=summary, monthly=monthly)


@router.get("/contributions/cumulative", response_model=ContributionsCumulative)
async def contributions_cumulative(
    user=Depends(get_current_user),
    person_id: int = Query(..., description="人员ID"),
    range: Optional[str] = Query(
        default=None, description="时间范围，如 2024-01..2024-12"
    ),
):
    """Cumulative lines for pension/medical/housing fund, with history."""
    person = await Person.get_or_none(id=person_id, user_id=user.id)
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    all_recs = await SalaryRecord.filter(person_id=person_id).all()
    all_recs.sort(key=lambda r: _ym_num(r.year, r.month))

    if range:
        start_num, end_num = _parse_range(range)
    else:
        start_num, end_num = (0, 999999)

    # Base offsets include history plus any system amounts before the range start
    base_pension = _D(person.pension_history)
    base_medical = _D(person.medical_history)
    base_housing = _D(person.housing_fund_history)

    for r in all_recs:
        ym = _ym_num(r.year, r.month)
        if ym < start_num:
            base_pension += _D(r.pension_insurance)
            base_medical += _D(r.medical_insurance)
            base_housing += _D(r.housing_fund)

    # Iterate points inside range
    points: List[ContributionsCumulativePoint] = []
    cur_p = base_pension
    cur_m = base_medical
    cur_h = base_housing

    for r in all_recs:
        ym = _ym_num(r.year, r.month)
        if ym < start_num or ym > end_num:
            continue
        cur_p += _D(r.pension_insurance)
        cur_m += _D(r.medical_insurance)
        cur_h += _D(r.housing_fund)
        points.append(
            ContributionsCumulativePoint(
                year=r.year,
                month=r.month,
                pension_cumulative=float(cur_p),
                medical_cumulative=float(cur_m),
                housing_fund_cumulative=float(cur_h),
            )
        )

    # Totals over entire dataset (history + system)
    pension_system_total = float(sum(_D(r.pension_insurance) for r in all_recs))
    medical_system_total = float(sum(_D(r.medical_insurance) for r in all_recs))
    housing_system_total = float(sum(_D(r.housing_fund) for r in all_recs))

    return ContributionsCumulative(
        person_id=person.id,
        person_name=person.name,
        pension_history=person.pension_history,
        medical_history=person.medical_history,
        housing_fund_history=person.housing_fund_history,
        points=points,
        pension_system_total=pension_system_total,
        medical_system_total=medical_system_total,
        housing_fund_system_total=housing_system_total,
        pension_total=float(_D(person.pension_history) + _D(pension_system_total)),
        medical_total=float(_D(person.medical_history) + _D(medical_system_total)),
        housing_fund_total=float(
            _D(person.housing_fund_history) + _D(housing_system_total)
        ),
    )


@router.get("/tables/monthly", response_model=List[MonthlyTableRow])
async def monthly_table(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
    range: Optional[str] = Query(default=None),
):
    """Monthly detail table: income items, deduction subtotal, net income (unified),
    benefits total, note.
    支持按人员、年份、月份过滤；为兼容性保留 range，但前端已不使用。
    """
    q = _salary_query(user.id, person_id=person_id, year=year, month=month)
    recs = _apply_range(await q.all(), range)

    # Load person names
    persons = {p.id: p.name for p in await Person.filter(user_id=user.id).all()}

    rows: List[MonthlyTableRow] = []
    for r in sorted(recs, key=lambda x: (x.year, x.month, x.person_id)):
        benefits = _benefits_sum(r)
        deductions = _deductions_sum(r)
        net = _unified_net_income(r)
        income_total = _gross_income_full(r)
        rows.append(
            MonthlyTableRow(
                person_id=r.person_id,
                person_name=persons.get(r.person_id, str(r.person_id)),
                year=r.year,
                month=r.month,
                # incomes
                base_salary=float(_D(r.base_salary)),
                performance_salary=float(_D(r.performance_salary)),
                high_temp_allowance=float(_D(_F(r, "high_temp_allowance"))),
                low_temp_allowance=float(_D(_F(r, "low_temp_allowance"))),
                computer_allowance=float(_D(_F(r, "computer_allowance"))),
                communication_allowance=float(
                    _D(_F(r, "communication_allowance"))
                ),
                comprehensive_allowance=float(
                    _D(_F(r, "comprehensive_allowance"))
                ),
                meal_allowance=float(_D(_F(r, "meal_allowance"))),
                mid_autumn_benefit=float(_D(_F(r, "mid_autumn_benefit"))),
                dragon_boat_benefit=float(_D(_F(r, "dragon_boat_benefit"))),
                spring_festival_benefit=float(
                    _D(_F(r, "spring_festival_benefit"))
                ),
                other_income=float(_D(_F(r, "other_income"))),
                # deductions
                pension_insurance=float(_D(r.pension_insurance)),
                medical_insurance=float(_D(r.medical_insurance)),
                unemployment_insurance=float(_D(r.unemployment_insurance)),
                critical_illness_insurance=float(
                    _D(r.critical_illness_insurance)
                ),
                enterprise_annuity=float(_D(r.enterprise_annuity)),
                housing_fund=float(_D(r.housing_fund)),
                other_deductions=float(_D(_F(r, "other_deductions"))),
                labor_union_fee=float(_D(_F(r, "labor_union_fee"))),
                performance_deduction=float(
                    _D(_F(r, "performance_deduction"))
                ),
                # totals
                income_total=float(income_total),
                deductions_total=float(deductions),
                benefits_total=float(benefits),
                allowances_total=float(
                    _D(_F(r, "meal_allowance")) + _D(_F(r, "other_income"))
                ),
                actual_take_home=float(net),
                net_income=float(net),
                tax=float(_D(r.tax)),
                note=r.note,
            )
        )

    return rows


@router.get("/tables/annual", response_model=List[AnnualTableRow])
async def annual_table(
    user=Depends(get_current_user),
    year: int = Query(...),
):
    """Annual summary table per person with YoY growth based on unified net income."""
    persons = await Person.filter(user_id=user.id).all()
    person_ids = [p.id for p in persons]
    name_map = {p.id: p.name for p in persons}

    recs = await SalaryRecord.filter(person_id__in=person_ids, year=year).all()

    # Current year aggregates across all fixed fields
    agg = {}
    for r in recs:
        pid = r.person_id
        cur = agg.get(pid, {
            # income items
            "base_salary": Decimal("0"),
            "performance_salary": Decimal("0"),
            "high_temp_allowance": Decimal("0"),
            "low_temp_allowance": Decimal("0"),
            "computer_allowance": Decimal("0"),
            "communication_allowance": Decimal("0"),
            "meal_allowance": Decimal("0"),
            "mid_autumn_benefit": Decimal("0"),
            "dragon_boat_benefit": Decimal("0"),
            "spring_festival_benefit": Decimal("0"),
            "other_income": Decimal("0"),
            # deduction items
            "pension_insurance": Decimal("0"),
            "medical_insurance": Decimal("0"),
            "unemployment_insurance": Decimal("0"),
            "critical_illness_insurance": Decimal("0"),
            "enterprise_annuity": Decimal("0"),
            "housing_fund": Decimal("0"),
            "other_deductions": Decimal("0"),
            "labor_union_fee": Decimal("0"),
            "performance_deduction": Decimal("0"),
            # derived totals
            "income_total": Decimal("0"),
            "deductions_total": Decimal("0"),
            "benefits_total": Decimal("0"),
            "actual_take_home_total": Decimal("0"),
            "net": Decimal("0"),
        })
        # accumulate incomes
        cur["base_salary"] += _D(r.base_salary)
        cur["performance_salary"] += _D(r.performance_salary)
        cur["high_temp_allowance"] += _D(_F(r, "high_temp_allowance"))
        cur["low_temp_allowance"] += _D(_F(r, "low_temp_allowance"))
        cur["computer_allowance"] += _D(_F(r, "computer_allowance"))
        cur["communication_allowance"] += _D(_F(r, "communication_allowance"))
        cur["meal_allowance"] += _D(_F(r, "meal_allowance"))
        cur["mid_autumn_benefit"] += _D(_F(r, "mid_autumn_benefit"))
        cur["dragon_boat_benefit"] += _D(_F(r, "dragon_boat_benefit"))
        cur["spring_festival_benefit"] += _D(_F(r, "spring_festival_benefit"))
        cur["other_income"] += _D(_F(r, "other_income"))
        # accumulate deductions
        cur["pension_insurance"] += _D(r.pension_insurance)
        cur["medical_insurance"] += _D(r.medical_insurance)
        cur["unemployment_insurance"] += _D(r.unemployment_insurance)
        cur["critical_illness_insurance"] += _D(r.critical_illness_insurance)
        cur["enterprise_annuity"] += _D(r.enterprise_annuity)
        cur["housing_fund"] += _D(r.housing_fund)
        cur["other_deductions"] += _D(_F(r, "other_deductions"))
        cur["labor_union_fee"] += _D(_F(r, "labor_union_fee"))
        cur["performance_deduction"] += _D(_F(r, "performance_deduction"))
        # derived
        cur["income_total"] += _gross_income_full(r)
        cur["deductions_total"] += _deductions_sum(r)
        b_total = _benefits_sum(r)
        cur["benefits_total"] += b_total
        n = _unified_net_income(r)
        cur["actual_take_home_total"] += n
        cur["net"] += n
        agg[pid] = cur

    # Previous year nets for YoY
    prev_recs = await SalaryRecord.filter(
        person_id__in=person_ids, year=year - 1
    ).all()
    prev_net = {}
    for r in prev_recs:
        prev_net[r.person_id] = prev_net.get(
            r.person_id, Decimal("0")
        ) + _unified_net_income(r)

    rows: List[AnnualTableRow] = []
    for pid, cur in agg.items():
        pn = prev_net.get(pid, Decimal("0"))
        yoy = float(((cur["net"] - pn) / pn * 100)) if pn > 0 else None
        rows.append(
            AnnualTableRow(
                person_id=pid,
                person_name=name_map.get(pid, str(pid)),
                year=year,
                # income totals
                base_salary_total=float(cur["base_salary"]),
                performance_salary_total=float(cur["performance_salary"]),
                high_temp_allowance_total=float(cur["high_temp_allowance"]),
                low_temp_allowance_total=float(cur["low_temp_allowance"]),
                computer_allowance_total=float(cur["computer_allowance"]),
                communication_allowance_total=float(
                    cur["communication_allowance"]
                ),
                meal_allowance_total=float(cur["meal_allowance"]),
                mid_autumn_benefit_total=float(cur["mid_autumn_benefit"]),
                dragon_boat_benefit_total=float(cur["dragon_boat_benefit"]),
                spring_festival_benefit_total=float(
                    cur["spring_festival_benefit"]
                ),
                other_income_total=float(cur["other_income"]),
                # deduction totals
                pension_insurance_total=float(cur["pension_insurance"]),
                medical_insurance_total=float(cur["medical_insurance"]),
                unemployment_insurance_total=float(cur["unemployment_insurance"]),
                critical_illness_insurance_total=float(
                    cur["critical_illness_insurance"]
                ),
                enterprise_annuity_total=float(cur["enterprise_annuity"]),
                housing_fund_total=float(cur["housing_fund"]),
                other_deductions_total=float(cur["other_deductions"]),
                labor_union_fee_total=float(cur["labor_union_fee"]),
                performance_deduction_total=float(
                    cur["performance_deduction"]
                ),
                # grand totals
                income_total=float(cur["income_total"]),
                deductions_total=float(cur["deductions_total"]),
                benefits_total=float(cur["benefits_total"]),
                actual_take_home_total=float(cur["actual_take_home_total"]),
                yoy_growth=yoy,
            )
        )

    # Sort by actual_take_home_total desc
    rows.sort(key=lambda r: r.actual_take_home_total, reverse=True)
    return rows


@router.get("/tables/annual-monthly", response_model=List[AnnualMonthlyRow])
async def annual_monthly_table(
    user=Depends(get_current_user),
    year: int = Query(...),
    person_id: Optional[int] = Query(default=None),
    hide_empty: bool = Query(default=False, description="Hide months with no data"),
):
    """Annual summary aggregated by month (1-12) for the given year.

    Shows all fixed fields summed across all persons (or filtered person).
    If hide_empty=true, only returns months with actual data.
    """
    persons = await Person.filter(user_id=user.id).all()
    person_ids = [p.id for p in persons]

    if person_id:
        if person_id not in person_ids:
            raise HTTPException(status_code=404, detail="人员不存在")
        person_ids = [person_id]

    recs = await SalaryRecord.filter(person_id__in=person_ids, year=year).all()

    # Aggregate by month (1-12)
    monthly_agg = {}
    for m in range(1, 13):
        monthly_agg[m] = {
            "base_salary": Decimal("0"),
            "performance_salary": Decimal("0"),
            "high_temp_allowance": Decimal("0"),
            "low_temp_allowance": Decimal("0"),
            "computer_allowance": Decimal("0"),
            "communication_allowance": Decimal("0"),
            "comprehensive_allowance": Decimal("0"),
            "meal_allowance": Decimal("0"),
            "mid_autumn_benefit": Decimal("0"),
            "dragon_boat_benefit": Decimal("0"),
            "spring_festival_benefit": Decimal("0"),
            "other_income": Decimal("0"),
            "pension_insurance": Decimal("0"),
            "medical_insurance": Decimal("0"),
            "unemployment_insurance": Decimal("0"),
            "critical_illness_insurance": Decimal("0"),
            "enterprise_annuity": Decimal("0"),
            "housing_fund": Decimal("0"),
            "other_deductions": Decimal("0"),
            "labor_union_fee": Decimal("0"),
            "performance_deduction": Decimal("0"),
            "income_total": Decimal("0"),
            "deductions_total": Decimal("0"),
            "benefits_total": Decimal("0"),
            "actual_take_home": Decimal("0"),
        }

    for r in recs:
        m = r.month
        agg = monthly_agg[m]

        # Accumulate income fields
        agg["base_salary"] += _D(r.base_salary)
        agg["performance_salary"] += _D(r.performance_salary)
        agg["high_temp_allowance"] += _D(_F(r, "high_temp_allowance"))
        agg["low_temp_allowance"] += _D(_F(r, "low_temp_allowance"))
        agg["computer_allowance"] += _D(_F(r, "computer_allowance"))
        agg["communication_allowance"] += _D(_F(r, "communication_allowance"))
        agg["comprehensive_allowance"] += _D(_F(r, "comprehensive_allowance"))
        agg["meal_allowance"] += _D(_F(r, "meal_allowance"))
        agg["mid_autumn_benefit"] += _D(_F(r, "mid_autumn_benefit"))
        agg["dragon_boat_benefit"] += _D(_F(r, "dragon_boat_benefit"))
        agg["spring_festival_benefit"] += _D(_F(r, "spring_festival_benefit"))
        agg["other_income"] += _D(_F(r, "other_income"))

        # Accumulate deduction fields
        agg["pension_insurance"] += _D(r.pension_insurance)
        agg["medical_insurance"] += _D(r.medical_insurance)
        agg["unemployment_insurance"] += _D(r.unemployment_insurance)
        agg["critical_illness_insurance"] += _D(r.critical_illness_insurance)
        agg["enterprise_annuity"] += _D(r.enterprise_annuity)
        agg["housing_fund"] += _D(r.housing_fund)
        agg["other_deductions"] += _D(_F(r, "other_deductions"))
        agg["labor_union_fee"] += _D(_F(r, "labor_union_fee"))
        agg["performance_deduction"] += _D(_F(r, "performance_deduction"))

        # Calculate totals
        agg["income_total"] += _gross_income_full(r)
        agg["deductions_total"] += _deductions_sum(r)
        agg["benefits_total"] += _benefits_sum(r)
        agg["allowances_total"] = agg.get(
            "allowances_total", Decimal("0")
        ) + (_D(_F(r, "meal_allowance")) + _D(_F(r, "other_income")))
        agg["actual_take_home"] += _unified_net_income(r)

    def is_empty(agg):
        """Check if a month's aggregation is empty (all zeros)."""
        return all(agg[k] == Decimal("0") for k in agg.keys())

    rows: List[AnnualMonthlyRow] = []
    for m in range(1, 13):
        agg = monthly_agg[m]

        # Skip empty months if hide_empty is true
        if hide_empty and is_empty(agg):
            continue
            
        rows.append(
            AnnualMonthlyRow(
                month=m,
                base_salary=float(agg["base_salary"]),
                performance_salary=float(agg["performance_salary"]),
                high_temp_allowance=float(agg["high_temp_allowance"]),
                low_temp_allowance=float(agg["low_temp_allowance"]),
                computer_allowance=float(agg["computer_allowance"]),
                communication_allowance=float(agg["communication_allowance"]),
                comprehensive_allowance=float(
                    agg["comprehensive_allowance"]
                )
                if "comprehensive_allowance" in agg
                else 0.0,
                meal_allowance=float(agg["meal_allowance"]),
                mid_autumn_benefit=float(agg["mid_autumn_benefit"]),
                dragon_boat_benefit=float(agg["dragon_boat_benefit"]),
                spring_festival_benefit=float(agg["spring_festival_benefit"]),
                other_income=float(agg["other_income"]),
                pension_insurance=float(agg["pension_insurance"]),
                medical_insurance=float(agg["medical_insurance"]),
                unemployment_insurance=float(agg["unemployment_insurance"]),
                critical_illness_insurance=float(
                    agg["critical_illness_insurance"]
                ),
                enterprise_annuity=float(agg["enterprise_annuity"]),
                housing_fund=float(agg["housing_fund"]),
                other_deductions=float(agg["other_deductions"]),
                labor_union_fee=float(agg["labor_union_fee"]),
                performance_deduction=float(
                    agg["performance_deduction"]
                )
                if "performance_deduction" in agg
                else 0.0,
                income_total=float(agg["income_total"]),
                deductions_total=float(agg["deductions_total"]),
                benefits_total=float(agg["benefits_total"]),
                allowances_total=float(
                    agg.get("allowances_total", Decimal("0"))
                ),
                actual_take_home=float(agg["actual_take_home"]),
            )
        )

    return rows
