from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from ..models import SalaryRecord, Person
from ..schemas.salary import SalaryCreate, SalaryUpdate, SalaryOut
from ..services.payroll import compute_payroll
from ..utils.auth import get_current_user


router = APIRouter()


def to_out(rec: SalaryRecord) -> SalaryOut:
    data = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        high_temp_allowance=rec.high_temp_allowance,
        low_temp_allowance=rec.low_temp_allowance,
        computer_allowance=rec.computer_allowance,
        meal_allowance=rec.meal_allowance,
        mid_autumn_benefit=rec.mid_autumn_benefit,
        dragon_boat_benefit=rec.dragon_boat_benefit,
        spring_festival_benefit=rec.spring_festival_benefit,
        other_income=rec.other_income,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        other_deductions=rec.other_deductions,
        tax=rec.tax,
    )
    return SalaryOut(
        id=rec.id,
        year=rec.year,
        month=rec.month,
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        high_temp_allowance=rec.high_temp_allowance,
        low_temp_allowance=rec.low_temp_allowance,
        computer_allowance=rec.computer_allowance,
        meal_allowance=rec.meal_allowance,
        mid_autumn_benefit=rec.mid_autumn_benefit,
        dragon_boat_benefit=rec.dragon_boat_benefit,
        spring_festival_benefit=rec.spring_festival_benefit,
        other_income=rec.other_income,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        other_deductions=rec.other_deductions,
        tax=data["tax"],
        total_income=data["total_income"],
        total_deductions=data["total_deductions"],
        gross_income=data["gross_income"],
        net_income=data["net_income"],
        actual_take_home=data["actual_take_home"],
        non_cash_benefits=data["non_cash_benefits"],
        note=rec.note,
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
    return [to_out(r) for r in records]


@router.post("/{person_id}", response_model=SalaryOut)
async def create_salary(person_id: int, payload: SalaryCreate, user=Depends(get_current_user)):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    calc = compute_payroll(
        base_salary=payload.base_salary,
        performance_salary=payload.performance_salary,
        high_temp_allowance=payload.high_temp_allowance,
        low_temp_allowance=payload.low_temp_allowance,
        computer_allowance=payload.computer_allowance,
        meal_allowance=payload.meal_allowance,
        mid_autumn_benefit=payload.mid_autumn_benefit,
        dragon_boat_benefit=payload.dragon_boat_benefit,
        spring_festival_benefit=payload.spring_festival_benefit,
        other_income=payload.other_income,
        pension_insurance=payload.pension_insurance,
        medical_insurance=payload.medical_insurance,
        unemployment_insurance=payload.unemployment_insurance,
        critical_illness_insurance=payload.critical_illness_insurance,
        enterprise_annuity=payload.enterprise_annuity,
        housing_fund=payload.housing_fund,
        other_deductions=payload.other_deductions,
        tax=payload.tax,
    )
    rec = await SalaryRecord.create(
        person_id=person_id,
        year=payload.year,
        month=payload.month,
        base_salary=payload.base_salary,
        performance_salary=payload.performance_salary,
        high_temp_allowance=payload.high_temp_allowance,
        low_temp_allowance=payload.low_temp_allowance,
        computer_allowance=payload.computer_allowance,
        meal_allowance=payload.meal_allowance,
        mid_autumn_benefit=payload.mid_autumn_benefit,
        dragon_boat_benefit=payload.dragon_boat_benefit,
        spring_festival_benefit=payload.spring_festival_benefit,
        other_income=payload.other_income,
        pension_insurance=payload.pension_insurance,
        medical_insurance=payload.medical_insurance,
        unemployment_insurance=payload.unemployment_insurance,
        critical_illness_insurance=payload.critical_illness_insurance,
        enterprise_annuity=payload.enterprise_annuity,
        housing_fund=payload.housing_fund,
        other_deductions=payload.other_deductions,
        tax=calc["tax"],
        note=payload.note,
    )
    return to_out(rec)


@router.get("/{record_id}", response_model=SalaryOut)
async def get_salary(record_id: int, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    return to_out(rec)


@router.put("/{record_id}", response_model=SalaryOut)
async def update_salary(record_id: int, payload: SalaryUpdate, user=Depends(get_current_user)):
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field != 'auto_tax':
            setattr(rec, field, value)
    await rec.save()
    calc = compute_payroll(
        base_salary=rec.base_salary,
        performance_salary=rec.performance_salary,
        high_temp_allowance=rec.high_temp_allowance,
        low_temp_allowance=rec.low_temp_allowance,
        computer_allowance=rec.computer_allowance,
        meal_allowance=rec.meal_allowance,
        mid_autumn_benefit=rec.mid_autumn_benefit,
        dragon_boat_benefit=rec.dragon_boat_benefit,
        spring_festival_benefit=rec.spring_festival_benefit,
        other_income=rec.other_income,
        pension_insurance=rec.pension_insurance,
        medical_insurance=rec.medical_insurance,
        unemployment_insurance=rec.unemployment_insurance,
        critical_illness_insurance=rec.critical_illness_insurance,
        enterprise_annuity=rec.enterprise_annuity,
        housing_fund=rec.housing_fund,
        other_deductions=rec.other_deductions,
        tax=rec.tax,
        auto_tax=payload.auto_tax or False,
    )
    rec.tax = calc["tax"]
    setattr(rec, field, value)
    await rec.save()
    return to_out(rec)


@router.delete("/{record_id}")
async def delete_salary(record_id: int, user=Depends(get_current_user)):
    # 先查询记录是否存在并属于当前用户
    rec = await SalaryRecord.filter(id=record_id, person__user_id=user.id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    # 直接删除记录
    await rec.delete()
    return {"ok": True}