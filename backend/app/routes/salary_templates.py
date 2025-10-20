from typing import List
from fastapi import APIRouter, HTTPException, Depends

from ..models import SalaryTemplate
from ..schemas.salary_template import SalaryTemplateCreate, SalaryTemplateUpdate, SalaryTemplateOut
from ..utils.auth import get_current_user


router = APIRouter()


@router.get("/", response_model=List[SalaryTemplateOut])
async def list_templates(user=Depends(get_current_user)):
    """
    Get all active salary templates for the current user
    """
    templates = await SalaryTemplate.filter(user_id=user.id, is_active=True).order_by("-created_at")
    return [await template_to_out(template) for template in templates]


@router.get("/default", response_model=SalaryTemplateOut)
async def get_default_template(user=Depends(get_current_user)):
    """
    Get the default salary template for the current user
    """
    template = await SalaryTemplate.filter(user_id=user.id, is_default=True, is_active=True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Default template not found")
    return await template_to_out(template)


@router.get("/{template_id}", response_model=SalaryTemplateOut)
async def get_template(template_id: int, user=Depends(get_current_user)):
    """
    Get a specific salary template by ID (owned by current user)
    """
    template = await SalaryTemplate.filter(id=template_id, user_id=user.id, is_active=True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return await template_to_out(template)


@router.post("/", response_model=SalaryTemplateOut)
async def create_template(template_data: SalaryTemplateCreate, user=Depends(get_current_user)):
    """
    Create a new salary template for the current user
    """
    # If this is set as default, unset other defaults for this user
    if template_data.is_default:
        await SalaryTemplate.filter(user_id=user.id, is_default=True).update(is_default=False)
    
    template = await SalaryTemplate.create(user_id=user.id, **template_data.dict())
    return await template_to_out(template)


@router.put("/{template_id}", response_model=SalaryTemplateOut)
async def update_template(
    template_id: int, 
    template_data: SalaryTemplateUpdate, 
    user=Depends(get_current_user)
):
    """
    Update an existing salary template (owned by current user)
    """
    template = await SalaryTemplate.filter(id=template_id, user_id=user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # If this is set as default, unset other defaults for this user
    if template_data.is_default:
        await SalaryTemplate.filter(user_id=user.id, is_default=True).exclude(id=template.id).update(is_default=False)
    
    update_data = template_data.dict(exclude_unset=True)
    await template.update_from_dict(update_data)
    await template.save()
    
    return await template_to_out(template)


@router.delete("/{template_id}")
async def delete_template(template_id: int, user=Depends(get_current_user)):
    """
    Soft delete a salary template (set is_active to False) for current user
    """
    template = await SalaryTemplate.filter(id=template_id, user_id=user.id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default template")
    
    template.is_active = False
    await template.save()
    
    return {"message": "Template deleted successfully"}


async def template_to_out(template: SalaryTemplate) -> SalaryTemplateOut:
    """
    Convert SalaryTemplate model to SalaryTemplateOut schema
    """
    return SalaryTemplateOut(
        id=template.id,
        name=template.name,
        description=template.description,
        allowances_template=template.allowances_template,
        bonuses_template=template.bonuses_template,
        deductions_template=template.deductions_template,
        is_default=template.is_default,
        is_active=template.is_active,
        created_at=template.created_at.isoformat(),
        updated_at=template.updated_at.isoformat()
    )
