from fastapi import APIRouter, Depends, HTTPException

from ..models import Person, SalaryTemplate
from ..schemas.salary_template import SalaryTemplateUpsert, SalaryTemplateOut
from ..utils.auth import get_current_user


router = APIRouter()


def _to_out(person_id: int, tmpl: SalaryTemplate) -> SalaryTemplateOut:
    return SalaryTemplateOut(
        person_id=person_id,
        base_salary=tmpl.base_salary,
        performance_salary=tmpl.performance_salary,
        pension_insurance=tmpl.pension_insurance,
        medical_insurance=tmpl.medical_insurance,
        unemployment_insurance=tmpl.unemployment_insurance,
        critical_illness_insurance=tmpl.critical_illness_insurance,
        enterprise_annuity=tmpl.enterprise_annuity,
        housing_fund=tmpl.housing_fund,
        tax=tmpl.tax,
        note=tmpl.note,
        custom_fields=tmpl.custom_fields or {},
    )


@router.get("/{person_id}", response_model=SalaryTemplateOut)
async def get_template(person_id: int, user=Depends(get_current_user)):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    tmpl = await SalaryTemplate.filter(person_id=person_id).first()
    if not tmpl:
        raise HTTPException(status_code=404, detail="模板不存在")
    return _to_out(person_id, tmpl)


@router.put("/{person_id}", response_model=SalaryTemplateOut)
async def upsert_template(
    person_id: int, payload: SalaryTemplateUpsert, user=Depends(get_current_user)
):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")

    tmpl = await SalaryTemplate.filter(person_id=person_id).first()
    if tmpl:
        tmpl.base_salary = payload.base_salary
        tmpl.performance_salary = payload.performance_salary
        tmpl.pension_insurance = payload.pension_insurance
        tmpl.medical_insurance = payload.medical_insurance
        tmpl.unemployment_insurance = payload.unemployment_insurance
        tmpl.critical_illness_insurance = payload.critical_illness_insurance
        tmpl.enterprise_annuity = payload.enterprise_annuity
        tmpl.housing_fund = payload.housing_fund
        tmpl.tax = payload.tax
        tmpl.note = payload.note
        tmpl.custom_fields = payload.custom_fields or {}
        await tmpl.save()
    else:
        tmpl = await SalaryTemplate.create(
            person_id=person_id,
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
            custom_fields=payload.custom_fields or {},
        )
    return _to_out(person_id, tmpl)


@router.delete("/{person_id}")
async def delete_template(person_id: int, user=Depends(get_current_user)):
    person = await Person.filter(id=person_id, user_id=user.id).first()
    if not person:
        raise HTTPException(status_code=404, detail="人员不存在")
    await SalaryTemplate.filter(person_id=person_id).delete()
    return {"ok": True}
