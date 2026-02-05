from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models import Person
from ..schemas.person import PersonCreate, PersonUpdate, PersonOut
from ..utils.auth import get_current_user


router = APIRouter()


@router.get("/", response_model=List[PersonOut])
async def list_persons(user=Depends(get_current_user)):
    persons = await Person.filter(user_id=user.id).all()
    return [PersonOut(
        id=p.id, 
        name=p.name, 
        note=p.note,
        pension_history=p.pension_history,
        medical_history=p.medical_history,
        housing_fund_history=p.housing_fund_history
    ) for p in persons]


@router.post("/", response_model=PersonOut)
async def create_person(payload: PersonCreate, user=Depends(get_current_user)):
    p = await Person.create(
        name=payload.name, 
        note=payload.note, 
        user_id=user.id,
        pension_history=payload.pension_history,
        medical_history=payload.medical_history,
        housing_fund_history=payload.housing_fund_history
    )
    return PersonOut(
        id=p.id, 
        name=p.name, 
        note=p.note,
        pension_history=p.pension_history,
        medical_history=p.medical_history,
        housing_fund_history=p.housing_fund_history
    )


@router.put("/{person_id}", response_model=PersonOut)
async def update_person(person_id: int, payload: PersonUpdate, user=Depends(get_current_user)):
    p = await Person.filter(id=person_id, user_id=user.id).first()
    if not p:
        raise HTTPException(status_code=404, detail="人员不存在")
    if payload.name is not None:
        p.name = payload.name
    if payload.note is not None:
        p.note = payload.note
    if payload.pension_history is not None:
        p.pension_history = payload.pension_history
    if payload.medical_history is not None:
        p.medical_history = payload.medical_history
    if payload.housing_fund_history is not None:
        p.housing_fund_history = payload.housing_fund_history
    await p.save()
    return PersonOut(
        id=p.id, 
        name=p.name, 
        note=p.note,
        pension_history=p.pension_history,
        medical_history=p.medical_history,
        housing_fund_history=p.housing_fund_history
    )


@router.delete("/{person_id}")
async def delete_person(person_id: int, user=Depends(get_current_user)):
    deleted = await Person.filter(id=person_id, user_id=user.id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="人员不存在")
    return {"ok": True}