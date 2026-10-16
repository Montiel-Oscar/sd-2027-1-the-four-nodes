from uuid import UUID
from app.pets.models import Pet

def create_pet_for_owner(session, owner_id: UUID, *, name: str, species: str, traits: str):
    """Crea una mascota pero NO hace commit (Oscar lo usa integrado en su reporte)."""
    pet = Pet(
        owner_id=owner_id,
        name=name,
        species=species,
        traits=traits
    )
    session.add(pet)
    session.flush()
    return pet

def get_pet_for_owner(session, owner_id: UUID, pet_id: UUID):
    """Devuelve la mascota solo si pertenece al dueño especificado."""
    return session.query(Pet).filter(Pet.id == pet_id, Pet.owner_id == owner_id).first()

def list_pets_for_owner(session, owner_id: UUID):
    """Lista todas las mascotas de un dueño."""
    return session.query(Pet).filter(Pet.owner_id == owner_id).all()
