"""Contrato público de los reportes de extravío."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class PetDetails(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    species: str = Field(min_length=1, max_length=60)
    traits: str = Field(min_length=1, max_length=500)

    @field_validator("name", "species", "traits")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío")
        return value


class MissingPetInput(BaseModel):
    pet_id: UUID | None = None
    pet: PetDetails | None = None
    seen_at: datetime
    municipality: str = Field(min_length=1, max_length=120)
    neighborhood: str = Field(min_length=1, max_length=120)
    landmark: str = Field(min_length=1, max_length=250)
    public_phone: str | None = Field(default=None, max_length=32)
    show_phone: bool = False

    @field_validator("municipality", "neighborhood", "landmark")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacío")
        return value

    @field_validator("public_phone")
    @classmethod
    def clean_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @field_validator("seen_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("seen_at debe incluir zona horaria")
        return value

    @model_validator(mode="after")
    def check_pet_and_contact(self) -> "MissingPetInput":
        if (self.pet_id is None) == (self.pet is None):
            raise ValueError("Envía pet_id o pet, exactamente uno")
        if self.show_phone and not self.public_phone:
            raise ValueError("Envía public_phone si show_phone es verdadero")
        return self


class MissingPetPublic(BaseModel):
    id: UUID
    public_url: str
    pet: PetDetails
    seen_at: datetime
    municipality: str
    neighborhood: str
    landmark: str
    public_phone: str | None
    created_at: datetime
