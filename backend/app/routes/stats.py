from typing import List, Optional, Dict
from fastapi import APIRouter, Query, Depends
from decimal import Decimal

from ..models import (
    SalaryRecord,
    CustomSalaryValue,
)
from ..schemas.stats import (
    MonthlyStats,
    IncomeComposition,
    DeductionsBreakdown,
    DeductionsMonthly,
    DeductionsBreakdownItem,
)
from ..utils.auth import get_current_user


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
                "field_key": v.salary_field.field_key,
                "label": v.salary_field.name,
            }
        )
    return payroll_map


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


def _custom_sums(custom_items: List[dict]) -> (Decimal, Decimal, Decimal):
    custom_cash = Decimal("0")
    custom_non_cash = Decimal("0")
    custom_deduction = Decimal("0")
    for cf in custom_items or []:
        amount = _D(cf.get("amount", 0))
        field_type = cf.get("field_type")
        if field_type == "income":
            if cf.get("is_non_cash"):
                custom_non_cash += amount
            else:
                custom_cash += amount
        elif field_type == "deduction":
            custom_deduction += amount
    return custom_cash, custom_non_cash, custom_deduction


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
        custom_cash, custom_non_cash, custom_deduction = _custom_sums(
            custom_payroll_map.get(r.id, [])
        )
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
        benefits_total = _benefits_sum(r) + custom_non_cash
        cash_income = (
            _D(r.base_salary)
            + _D(r.performance_salary)
            + _allowances_sum_full(r)
            + _D(_F(r, "other_income"))
            + custom_cash
        )
        deductions_total = (
            _deductions_sum(r) + custom_deduction
        )
        actual_take_home = cash_income - deductions_total - _D(r.tax)
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
                tax=float(_D(r.tax)),
                gross_income=float(cash_income),
                net_income=float(actual_take_home),
                actual_take_home=float(actual_take_home),
                non_cash_benefits=float(benefits_total),
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

    result: List[IncomeComposition] = []

    for r in recs:
        custom_income = Decimal("0")
        custom_non_cash = Decimal("0")
        custom_cash = Decimal("0")
        custom_items = []
        custom_non_cash_items = []
        for cf in custom_payroll_map.get(r.id, []):
            amount = _D(cf.get("amount", 0))
            if cf.get("field_type") != "income":
                continue
            custom_income += amount
            if cf.get("is_non_cash"):
                custom_non_cash += amount
                if amount != 0:
                    custom_non_cash_items.append(
                        {
                            "key": cf.get("field_key") or "",
                            "label": (
                                cf.get("label")
                                or cf.get("field_key")
                                or "自定义福利"
                            ),
                            "amount": float(amount),
                        }
                    )
            else:
                custom_cash += amount
                if amount != 0:
                    custom_items.append(
                        {
                            "key": cf.get("field_key") or "",
                            "label": (
                                cf.get("label")
                                or cf.get("field_key")
                                or "自定义收入"
                            ),
                            "amount": float(amount),
                        }
                    )

        allowances = float(_allowances_sum_full(r))
        base_other = _D(_F(r, "other_income"))
        benefits = float(_benefits_sum(r) + custom_non_cash)
        other_income = float(base_other + custom_cash)
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
                mid_autumn_benefit=float(_D(_F(r, "mid_autumn_benefit"))),
                dragon_boat_benefit=float(_D(_F(r, "dragon_boat_benefit"))),
                spring_festival_benefit=float(
                    _D(_F(r, "spring_festival_benefit"))
                ),
                other_income=other_income,
                other_income_base=float(base_other),
                non_cash_benefits=float(_D(benefits)),
                custom_income_items=custom_items,
                custom_non_cash_items=custom_non_cash_items,
                total_income=total_income,
                base_salary_percent=base_salary_percent,
                performance_percent=performance_percent,
                allowances_percent=allowances_percent,
                benefits_percent=benefits_percent,
                other_percent=other_percent,
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

