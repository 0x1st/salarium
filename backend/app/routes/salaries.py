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
        performance_percent=rec.performance_percent,
        performance_fixed=rec.performance_fixed,
        allowances=rec.allowances,
        bonuses=rec.bonuses,
        deductions=rec.deductions,
        ins_pension=rec.ins_pension,
        ins_medical=rec.ins_medical,
        ins_unemployment=rec.ins_unemployment,
        ins_injury=rec.ins_injury,
        ins_maternity=rec.ins_maternity,
        housing_fund=rec.housing_fund,
        tax=rec.tax,
        auto_tax=False,  # 输出遵循记录中的 tax 值；如需自动税，在创建/更新时写入
    )
    return SalaryOut(
        id=rec.id,
        year=rec.year,
        month=rec.month,
        base_salary=rec.base_salary,
        performance=data["performance"],
        allowances_total=data["allowances_total"],
        bonuses_total=data["bonuses_total"],
        deductions_total=data["deductions_total"],
        insurance_total=data["insurance_total"],
        tax=data["tax"],
        gross_income=data["gross_income"],
        net_income=data["net_income"],
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
        performance_percent=payload.performance_percent,
        performance_fixed=payload.performance_fixed,
        allowances=payload.allowances,
        bonuses=payload.bonuses,
        deductions=payload.deductions,
        ins_pension=payload.ins_pension,
        ins_medical=payload.ins_medical,
        ins_unemployment=payload.ins_unemployment,
        ins_injury=payload.ins_injury,
        ins_maternity=payload.ins_maternity,
        housing_fund=payload.housing_fund,
        tax=payload.tax,
        auto_tax=payload.auto_tax,
    )
    rec = await SalaryRecord.create(
        person_id=person_id,
        year=payload.year,
        month=payload.month,
        base_salary=payload.base_salary,
        performance_percent=payload.performance_percent,
        performance_fixed=payload.performance_fixed,
        allowances=payload.allowances,
        bonuses=payload.bonuses,
        deductions=payload.deductions,
        ins_pension=payload.ins_pension,
        ins_medical=payload.ins_medical,
        ins_unemployment=payload.ins_unemployment,
        ins_injury=payload.ins_injury,
        ins_maternity=payload.ins_maternity,
        housing_fund=payload.housing_fund,
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
        setattr(rec, field, value)
    await rec.save()
    # 重新计算税（如 auto_tax 为 True 则覆盖 tax）
    calc = compute_payroll(
        base_salary=rec.base_salary,
        performance_percent=rec.performance_percent,
        performance_fixed=rec.performance_fixed,
        allowances=rec.allowances,
        bonuses=rec.bonuses,
        deductions=rec.deductions,
        ins_pension=rec.ins_pension,
        ins_medical=rec.ins_medical,
        ins_unemployment=rec.ins_unemployment,
        ins_injury=rec.ins_injury,
        ins_maternity=rec.ins_maternity,
        housing_fund=rec.housing_fund,
        tax=rec.tax,
        auto_tax=payload.auto_tax or False,
    )
    rec.tax = calc["tax"]
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