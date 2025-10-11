from typing import Dict, Optional
from pydantic import BaseModel


class SalaryTemplateCreate(BaseModel):
    """
    Schema for creating a new salary template
    """
    name: str
    description: Optional[str] = None
    allowances_template: Optional[Dict[str, float]] = None
    bonuses_template: Optional[Dict[str, float]] = None
    deductions_template: Optional[Dict[str, float]] = None
    is_default: bool = False
    is_active: bool = True


class SalaryTemplateUpdate(BaseModel):
    """
    Schema for updating an existing salary template
    """
    name: Optional[str] = None
    description: Optional[str] = None
    allowances_template: Optional[Dict[str, float]] = None
    bonuses_template: Optional[Dict[str, float]] = None
    deductions_template: Optional[Dict[str, float]] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class SalaryTemplateOut(BaseModel):
    """
    Schema for salary template output
    """
    id: int
    name: str
    description: Optional[str] = None
    allowances_template: Optional[Dict[str, float]] = None
    bonuses_template: Optional[Dict[str, float]] = None
    deductions_template: Optional[Dict[str, float]] = None
    is_default: bool
    is_active: bool
    created_at: str
    updated_at: str


class CategoryStatsOut(BaseModel):
    """
    Schema for category statistics output
    """
    category_name: str
    category_type: str  # "allowances", "bonuses", "deductions"
    total_amount: float
    average_amount: float
    usage_count: int
    usage_percentage: float