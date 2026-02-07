from typing import List, Optional, Dict, Tuple
from fastapi import APIRouter, HTTPException, Query, Depends
from tortoise.exceptions import IntegrityError

from ..models import SalaryRecord, Person, SalaryField, CustomSalaryValue
from ..schemas.salary import SalaryCreate, SalaryUpdate, SalaryOut
from ..services.payroll import compute_payroll
from ..utils.auth import get_current_user


router = APIRouter()


async def load_custom_fields(
    record_ids: List[int],
) -> Tuple[Dict[int, Dict[str, float]], Dict[int, List[dict]]]:
    """Batch load custom field values for salary records."""
    if not record_ids:
        return {}, {}

    values = await CustomSalaryValue.filter(
        salary_record_id__in=record_ids
    ).prefetch_related("salary_field").all()

    by_record: Dict[int, Dict[str, float]] = {}
    for v in values:
        by_record.setdefault(v.salary_record_id, {})[v.salary_field.field_key] = float(
            v.amount
        )

    payroll_by_record: Dict[int, List[dict]] = {}
    for v in values:
        payroll_by_record.setdefault(v.salary_record_id, []).append(
            {
                "field_type": v.salary_field.field_type,
                "is_non_cash": v.salary_field.is_non_cash,
                "amount": float(v.amount),
            }
        )

    return by_record, payroll_by_record


async def save_custom_fields(
    record_id: int, user_id: int, custom_fields: dict
) -> None:
    """Save custom field values for a salary record."""
    if not custom_fields:
        return

    # Get user's field definitions
    field_defs = await SalaryField.filter(user_id=user_id, is_active=True).all()
    field_map = {f.field_key: f for f in field_defs}

    # Delete existing custom values for this record
    await CustomSalaryValue.filter(salary_record_id=record_id).delete()

    # Create new custom values
    for field_key, amount in custom_fields.items():
        if field_key in field_map and amount != 0:
            await CustomSalaryValue.create(
                salary_record_id=record_id,
                salary_field_id=field_map[field_key].id,
                amount=amount,
            )


def build_salary_out(
    rec: SalaryRecord,
    custom_fields_data: Dict[str, float],
    custom_fields_payroll: List[dict],
) -> SalaryOut:
    data = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        tax=rec.tax,
        custom_fields=custom_fields_payroll or [],
    )
    return SalaryOut(
        id=rec.id,
        year=rec.year,
        month=rec.month,
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        tax=data["tax"],
        total_income=data["total_income"],
        total_deductions=data["total_deductions"],
        gross_income=data["gross_income"],
        net_income=data["net_income"],
        actual_take_home=data["actual_take_home"],
        non_cash_benefits=data["non_cash_benefits"],
        note=rec.note,
        custom_fields=custom_fields_data or {},
    )


@router.get("/", response_model=List[SalaryOut])
async def list_salaries(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    records = await q.all()
    record_ids = [r.id for r in records]
    custom_data_map, custom_payroll_map = await load_custom_fields(record_ids)
    return [
        build_salary_out(
            r,
            custom_data_map.get(r.id, {}),
            custom_payroll_map.get(r.id, []),
        )
        for r in records
    ]


@router.post("/{person_id}", response_model=SalaryOut)
async def create_salary(
    person_id: int, payload: SalaryCreate, user=Depends(get_current_user)
):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    try:
        rec = await SalaryRecord.create(
            person_id=person_id,
            year=payload.year,
            month=payload.month,
            base_salary=payload.base_salary,
            performance_salary=payload.performance_salary,
            pension_insurance=payload.pension_insurance,
            medical_insurance=payload.medical_insurance,
            unemployment_insurance=payload.unemployment_insurance,
            critical_illness_insurance=payload.critical_illness_insurance,
            enterprise_annuity=payload.enterprise_annuity,
            housing_fund=payload.housing_fund,
            tax=payload.tax,
            note=payload.note,
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="该月份工资记录已存在")

    # Save custom fields
    if payload.custom_fields:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.get("/{record_id}", response_model=SalaryOut)
async def get_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.put("/{record_id}", response_model=SalaryOut)
async def update_salary(
    record_id: int, payload: SalaryUpdate, user=Depends(get_current_user)
):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Update fixed fields
    update_data = payload.model_dump(exclude_unset=True, exclude={"custom_fields"})
    for field, value in update_data.items():
        setattr(rec, field, value)
    await rec.save()

    # Update custom fields if provided
    if payload.custom_fields is not None:
        await save_custom_fields(rec.id, user.id, payload.custom_fields)

    custom_data_map, custom_payroll_map = await load_custom_fields([rec.id])
    return build_salary_out(
        rec,
        custom_data_map.get(rec.id, {}),
        custom_payroll_map.get(rec.id, []),
    )


@router.delete("/{record_id}")
async def delete_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Delete custom values first (cascade)
    await CustomSalaryValue.filter(salary_record_id=rec.id).delete()

    await rec.delete()
    return {"ok": True}
