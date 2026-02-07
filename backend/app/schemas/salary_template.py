from typing import Optional, Dict
from pydantic import BaseModel


class SalaryTemplateUpsert(BaseModel):
    base_salary: float = 0.0
    performance_salary: float = 0.0
    pension_insurance: float = 0.0
    medical_insurance: float = 0.0
    unemployment_insurance: float = 0.0
    critical_illness_insurance: float = 0.0
    enterprise_annuity: float = 0.0
    housing_fund: float = 0.0
    tax: float = 0.0
    note: Optional[str] = None
    custom_fields: Optional[Dict[str, float]] = None


class SalaryTemplateOut(BaseModel):
    person_id: int
    base_salary: float
    performance_salary: float
    pension_insurance: float
    medical_insurance: float
    unemployment_insurance: float
    critical_illness_insurance: float
    enterprise_annuity: float
    housing_fund: float
    tax: float
    note: Optional[str] = None
    custom_fields: Dict[str, float] = {}
