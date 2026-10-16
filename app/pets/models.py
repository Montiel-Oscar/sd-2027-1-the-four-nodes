import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base

class Pet(Base):
    __tablename__ = "pets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    traits = Column(String, nullable=False)
