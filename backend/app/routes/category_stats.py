from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from collections import defaultdict

from ..models import SalaryRecord
from ..schemas.salary_template import CategoryStatsOut
from ..utils.auth import get_current_user


router = APIRouter()


@router.get("/categories", response_model=List[CategoryStatsOut])
async def get_category_statistics(user=Depends(get_current_user)):
    """
    Get statistics for all custom categories (allowances, bonuses, deductions)
    """
    records = await SalaryRecord.filter(person__user_id=user.id).all()
    
    # Collect all categories and their usage
    category_stats = defaultdict(lambda: {
        'total_amount': 0.0,
        'usage_count': 0,
        'amounts': []
    })
    
    total_records = len(records)
    
    for record in records:
        # Process allowances
        if record.allowances:
            for category, amount in record.allowances.items():
                key = f"allowances_{category}"
                category_stats[key]['total_amount'] += amount
                category_stats[key]['usage_count'] += 1
                category_stats[key]['amounts'].append(amount)
                category_stats[key]['type'] = 'allowances'
                category_stats[key]['name'] = category
        
        # Process bonuses
        if record.bonuses:
            for category, amount in record.bonuses.items():
                key = f"bonuses_{category}"
                category_stats[key]['total_amount'] += amount
                category_stats[key]['usage_count'] += 1
                category_stats[key]['amounts'].append(amount)
                category_stats[key]['type'] = 'bonuses'
                category_stats[key]['name'] = category
        
        # Process deductions
        if record.deductions:
            for category, amount in record.deductions.items():
                key = f"deductions_{category}"
                category_stats[key]['total_amount'] += amount
                category_stats[key]['usage_count'] += 1
                category_stats[key]['amounts'].append(amount)
                category_stats[key]['type'] = 'deductions'
                category_stats[key]['name'] = category
    
    # Convert to output format
    result = []
    for key, stats in category_stats.items():
        average_amount = stats['total_amount'] / stats['usage_count'] if stats['usage_count'] > 0 else 0
        usage_percentage = (stats['usage_count'] / total_records * 100) if total_records > 0 else 0
        
        result.append(CategoryStatsOut(
            category_name=stats['name'],
            category_type=stats['type'],
            total_amount=stats['total_amount'],
            average_amount=average_amount,
            usage_count=stats['usage_count'],
            usage_percentage=usage_percentage
        ))
    
    # Sort by usage count descending
    result.sort(key=lambda x: x.usage_count, reverse=True)
    
    return result


@router.get("/categories/summary")
async def get_category_summary(user=Depends(get_current_user)):
    """
    Get summary statistics for category types
    """
    records = await SalaryRecord.filter(person__user_id=user.id).all()
    
    summary = {
        'allowances': {'total': 0.0, 'count': 0, 'categories': set()},
        'bonuses': {'total': 0.0, 'count': 0, 'categories': set()},
        'deductions': {'total': 0.0, 'count': 0, 'categories': set()}
    }
    
    for record in records:
        if record.allowances:
            for category, amount in record.allowances.items():
                summary['allowances']['total'] += amount
                summary['allowances']['count'] += 1
                summary['allowances']['categories'].add(category)
        
        if record.bonuses:
            for category, amount in record.bonuses.items():
                summary['bonuses']['total'] += amount
                summary['bonuses']['count'] += 1
                summary['bonuses']['categories'].add(category)
        
        if record.deductions:
            for category, amount in record.deductions.items():
                summary['deductions']['total'] += amount
                summary['deductions']['count'] += 1
                summary['deductions']['categories'].add(category)
    
    # Convert sets to counts
    for category_type in summary:
        summary[category_type]['unique_categories'] = len(summary[category_type]['categories'])
        del summary[category_type]['categories']
    
    return summary