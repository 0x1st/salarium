from typing import List
from fastapi import APIRouter, Depends

from ..models import SalaryRecord
from ..schemas.salary_template import CategoryStatsOut
from ..utils.auth import get_current_user


router = APIRouter()

INCOME_CATEGORIES = [
    ('基本工资', 'base_salary'),
    ('绩效工资', 'performance_salary'),
    ('高温补贴', 'high_temp_allowance'),
    ('低温补贴', 'low_temp_allowance'),
    ('餐补', 'meal_allowance'),
    ('中秋福利', 'mid_autumn_benefit'),
    ('端午福利', 'dragon_boat_benefit'),
    ('春节福利', 'spring_festival_benefit'),
    ('其他收入', 'other_income'),
]

DEDUCTION_CATEGORIES = [
    ('养老保险', 'pension_insurance'),
    ('医疗保险', 'medical_insurance'),
    ('失业保险', 'unemployment_insurance'),
    ('大病互助保险', 'critical_illness_insurance'),
    ('企业年金', 'enterprise_annuity'),
    ('住房公积金', 'housing_fund'),
    ('其他扣除', 'other_deductions'),
]


@router.get("/categories", response_model=List[CategoryStatsOut])
async def get_category_statistics(user=Depends(get_current_user)):
    """
    Get statistics for all fixed categories (income and deductions)
    """
    records = await SalaryRecord.filter(person__user_id=user.id).all()
    total_records = len(records)
    
    result = []
    
    for category_name, field_name in INCOME_CATEGORIES:
        total_amount = sum(getattr(record, field_name, 0) for record in records)
        usage_count = sum(1 for record in records if getattr(record, field_name, 0) > 0)
        average_amount = total_amount / usage_count if usage_count > 0 else 0
        usage_percentage = (usage_count / total_records * 100) if total_records > 0 else 0
        
        result.append(CategoryStatsOut(
            category_name=category_name,
            category_type='income',
            total_amount=total_amount,
            average_amount=average_amount,
            usage_count=usage_count,
            usage_percentage=usage_percentage
        ))
    
    for category_name, field_name in DEDUCTION_CATEGORIES:
        total_amount = sum(getattr(record, field_name, 0) for record in records)
        usage_count = sum(1 for record in records if getattr(record, field_name, 0) > 0)
        average_amount = total_amount / usage_count if usage_count > 0 else 0
        usage_percentage = (usage_count / total_records * 100) if total_records > 0 else 0
        
        result.append(CategoryStatsOut(
            category_name=category_name,
            category_type='deduction',
            total_amount=total_amount,
            average_amount=average_amount,
            usage_count=usage_count,
            usage_percentage=usage_percentage
        ))
    
    result.sort(key=lambda x: x.total_amount, reverse=True)
    
    return result


@router.get("/categories/summary")
async def get_category_summary(user=Depends(get_current_user)):
    """
    Get summary statistics for category types
    """
    records = await SalaryRecord.filter(person__user_id=user.id).all()
    
    income_total = 0.0
    deduction_total = 0.0
    
    for record in records:
        for _, field_name in INCOME_CATEGORIES:
            income_total += getattr(record, field_name, 0)
        
        for _, field_name in DEDUCTION_CATEGORIES:
            deduction_total += getattr(record, field_name, 0)
    
    return {
        'income': {
            'total': income_total,
            'categories_count': len(INCOME_CATEGORIES)
        },
        'deductions': {
            'total': deduction_total,
            'categories_count': len(DEDUCTION_CATEGORIES)
        }
    }