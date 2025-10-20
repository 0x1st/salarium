from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from decimal import Decimal

from ..models import SalaryRecord, Person
from ..schemas.stats import (
    MonthlyStats, YearlyStats, FamilySummary, 
    PersonCumulativeInsurance, BenefitStats, IncomeComposition
)
from ..utils.auth import get_current_user
from ..services.payroll import compute_payroll


router = APIRouter()


@router.get("/monthly", response_model=List[MonthlyStats])
async def monthly_stats(
    user= Depends(get_current_user),
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
    recs = await q.all()
    result: List[MonthlyStats] = []
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_salary=r.performance_salary,
            high_temp_allowance=r.high_temp_allowance,
            low_temp_allowance=r.low_temp_allowance,
            computer_allowance=r.computer_allowance,
            meal_allowance=r.meal_allowance,
            mid_autumn_benefit=r.mid_autumn_benefit,
            dragon_boat_benefit=r.dragon_boat_benefit,
            spring_festival_benefit=r.spring_festival_benefit,
            other_income=r.other_income,
            pension_insurance=r.pension_insurance,
            medical_insurance=r.medical_insurance,
            unemployment_insurance=r.unemployment_insurance,
            critical_illness_insurance=r.critical_illness_insurance,
            enterprise_annuity=r.enterprise_annuity,
            housing_fund=r.housing_fund,
            other_deductions=r.other_deductions,
            tax=r.tax,
        )
        allowances_total = r.high_temp_allowance + r.low_temp_allowance + r.computer_allowance
        insurance_total = (r.pension_insurance + r.medical_insurance + r.unemployment_insurance +
                          r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund)
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
                allowances_total=(r.high_temp_allowance + r.low_temp_allowance + r.meal_allowance),
                bonuses_total=(r.mid_autumn_benefit + r.dragon_boat_benefit + r.spring_festival_benefit + r.other_income),
                insurance_total=(r.pension_insurance + r.medical_insurance + r.unemployment_insurance + r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund),
                tax=calc["tax"],
                gross_income=calc["gross_income"],
                net_income=calc["net_income"],
                actual_take_home=calc["actual_take_home"],
                non_cash_benefits=calc["non_cash_benefits"],
            )
        )
    return result


@router.get("/yearly", response_model=List[YearlyStats])
async def yearly_stats(user= Depends(get_current_user), person_id: Optional[int] = Query(default=None), year: int = Query(...)):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = {p.id for p in persons}
    if person_id and person_id not in person_ids:
        raise HTTPException(status_code=404, detail="人员不存在")
    if person_id:
        person_ids = {person_id}
    recs = await SalaryRecord.filter(person_id__in=list(person_ids), year=year).all()
    stats_map = {}
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_salary=r.performance_salary,
            high_temp_allowance=r.high_temp_allowance,
            low_temp_allowance=r.low_temp_allowance,
            computer_allowance=r.computer_allowance,
            meal_allowance=r.meal_allowance,
            mid_autumn_benefit=r.mid_autumn_benefit,
            dragon_boat_benefit=r.dragon_boat_benefit,
            spring_festival_benefit=r.spring_festival_benefit,
            other_income=r.other_income,
            pension_insurance=r.pension_insurance,
            medical_insurance=r.medical_insurance,
            unemployment_insurance=r.unemployment_insurance,
            critical_illness_insurance=r.critical_illness_insurance,
            enterprise_annuity=r.enterprise_annuity,
            housing_fund=r.housing_fund,
            other_deductions=r.other_deductions,
            tax=r.tax,
        )
        allowances_total = r.high_temp_allowance + r.low_temp_allowance + r.computer_allowance
        insurance_total = (r.pension_insurance + r.medical_insurance + r.unemployment_insurance +
                          r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund)
        allowances_total = r.high_temp_allowance + r.low_temp_allowance + r.meal_allowance
        bonuses_total = r.mid_autumn_benefit + r.dragon_boat_benefit + r.spring_festival_benefit + r.other_income
        insurance_total = r.pension_insurance + r.medical_insurance + r.unemployment_insurance + r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund
        
        s = stats_map.get(r.person_id, {
            "months": 0, "gross": 0.0, "net": 0.0, "insurance": 0.0, "tax": 0.0, "allowances": 0.0, "bonuses": 0.0,
            "actual_take_home": 0.0, "non_cash_benefits": 0.0
        })
        s["months"] += 1
        s["gross"] += calc["gross_income"]
        s["net"] += calc["net_income"]
        s["insurance"] += insurance_total
        s["tax"] += calc["tax"]
        s["allowances"] += allowances_total
        s["bonuses"] += 0.0
        s["actual_take_home"] += calc["actual_take_home"]
        s["non_cash_benefits"] += calc["non_cash_benefits"]
        s["bonuses"] += bonuses_total
        stats_map[r.person_id] = s
    result: List[YearlyStats] = []
    for pid, s in stats_map.items():
        avg_net = s["net"] / s["months"] if s["months"] else 0.0
        result.append(YearlyStats(
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
        ))
    return result


@router.get("/family", response_model=FamilySummary)
async def family_summary(user= Depends(get_current_user), year: int = Query(...)):
    persons = await Person.filter(user_id=user.id).all()
    person_ids = [p.id for p in persons]
    recs = await SalaryRecord.filter(person_id__in=person_ids, year=year).all()
    totals = {pid: 0.0 for pid in person_ids}
    insurance_total = 0.0
    tax_total = 0.0
    total_gross = 0.0
    total_net = 0.0
    for r in recs:
        calc = compute_payroll(
            base_salary=r.base_salary,
            performance_salary=r.performance_salary,
            high_temp_allowance=r.high_temp_allowance,
            low_temp_allowance=r.low_temp_allowance,
            computer_allowance=r.computer_allowance,
            meal_allowance=r.meal_allowance,
            mid_autumn_benefit=r.mid_autumn_benefit,
            dragon_boat_benefit=r.dragon_boat_benefit,
            spring_festival_benefit=r.spring_festival_benefit,
            other_income=r.other_income,
            pension_insurance=r.pension_insurance,
            medical_insurance=r.medical_insurance,
            unemployment_insurance=r.unemployment_insurance,
            critical_illness_insurance=r.critical_illness_insurance,
            enterprise_annuity=r.enterprise_annuity,
            housing_fund=r.housing_fund,
            other_deductions=r.other_deductions,
            tax=r.tax,
        )
        insurance_calc = (r.pension_insurance + r.medical_insurance + r.unemployment_insurance +
                         r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund)
        totals[r.person_id] += calc["net_income"]
        insurance_total += insurance_calc
        record_insurance_total = r.pension_insurance + r.medical_insurance + r.unemployment_insurance + r.critical_illness_insurance + r.enterprise_annuity + r.housing_fund
        
        totals[r.person_id] += calc["net_income"]
        insurance_total += record_insurance_total
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
        pension_total = Decimal(str(person.pension_history)) + Decimal(str(pension_system))
        medical_total = Decimal(str(person.medical_history)) + Decimal(str(medical_system))
        housing_fund_total = Decimal(str(person.housing_fund_history)) + Decimal(str(housing_fund_system))
        
        result.append(PersonCumulativeInsurance(
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
        ))
    
    return result


@router.get("/benefits", response_model=List[BenefitStats])
async def benefit_stats(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
):
    """Get non-cash benefit statistics"""
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    
    recs = await q.all()
    result: List[BenefitStats] = []
    
    for r in recs:
        total_benefits = (r.meal_allowance + r.mid_autumn_benefit + 
                         r.dragon_boat_benefit + r.spring_festival_benefit)
        result.append(BenefitStats(
            year=r.year,
            month=r.month,
            person_id=r.person_id,
            meal_allowance=r.meal_allowance,
            mid_autumn_benefit=r.mid_autumn_benefit,
            dragon_boat_benefit=r.dragon_boat_benefit,
            spring_festival_benefit=r.spring_festival_benefit,
            total_benefits=total_benefits,
        ))
    
    return result


@router.get("/income-composition", response_model=List[IncomeComposition])
async def income_composition(
    user=Depends(get_current_user),
    person_id: Optional[int] = Query(default=None),
    year: Optional[int] = Query(default=None),
    month: Optional[int] = Query(default=None),
):
    """Get income composition with percentages"""
    q = SalaryRecord.filter(person__user_id=user.id)
    if person_id:
        q = q.filter(person_id=person_id)
    if year:
        q = q.filter(year=year)
    if month:
        q = q.filter(month=month)
    
    recs = await q.all()
    result: List[IncomeComposition] = []
    
    for r in recs:
        allowances = r.high_temp_allowance + r.low_temp_allowance + r.computer_allowance
        non_cash_benefits = r.meal_allowance + r.mid_autumn_benefit + r.dragon_boat_benefit + r.spring_festival_benefit
        total_income = (r.base_salary + r.performance_salary + allowances + 
                       non_cash_benefits + r.other_income)
        
        # Calculate percentages (avoid division by zero)
        if total_income > 0:
            base_salary_percent = (r.base_salary / total_income) * 100
            performance_percent = (r.performance_salary / total_income) * 100
            allowances_percent = (allowances / total_income) * 100
            benefits_percent = (non_cash_benefits / total_income) * 100
            other_percent = (r.other_income / total_income) * 100
        else:
            base_salary_percent = 0.0
            performance_percent = 0.0
            allowances_percent = 0.0
            benefits_percent = 0.0
            other_percent = 0.0
        
        result.append(IncomeComposition(
            person_id=r.person_id,
            year=r.year,
            month=r.month,
            base_salary=r.base_salary,
            performance_salary=r.performance_salary,
            high_temp_allowance=r.high_temp_allowance,
            low_temp_allowance=r.low_temp_allowance,
            computer_allowance=r.computer_allowance,
            other_income=r.other_income,
            non_cash_benefits=non_cash_benefits,
            total_income=total_income,
            base_salary_percent=base_salary_percent,
            performance_percent=performance_percent,
            allowances_percent=allowances_percent,
            benefits_percent=benefits_percent,
            other_percent=other_percent,
        ))
    
    return result