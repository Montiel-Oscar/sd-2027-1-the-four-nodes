from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import get_actor_id
from app.pets.service import create_pet_for_owner, get_pet_for_owner, list_pets_for_owner
from pydantic import BaseModel

router = APIRouter(prefix="/api/mascotas", tags=["Mascotas"])

class PetCreate(BaseModel):
    name: str
    species: str
    traits: str

class PetResponse(BaseModel):
    id: UUID
    name: str
    species: str
    traits: str

    class Config:
        from_attributes = True

@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(
    pet_in: PetCreate,
    db: Session = Depends(get_db),
    actor_id: UUID = Depends(get_actor_id)
):
    pet = create_pet_for_owner(
        db,
        actor_id,
        name=pet_in.name,
        species=pet_in.species,
        traits=pet_in.traits
    )
    db.commit()
    db.refresh(pet)
    return pet

@router.get("", response_model=List[PetResponse])
def list_pets(
    db: Session = Depends(get_db),
    actor_id: UUID = Depends(get_actor_id)
):
    return list_pets_for_owner(db, actor_id)

@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: UUID,
    db: Session = Depends(get_db),
    actor_id: UUID = Depends(get_actor_id)
):
    pet = get_pet_for_owner(db, actor_id, pet_id)
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return pet
