import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class BusinessProfileEntity(Base):
    __tablename__ = "business_profile_entities"

    business_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        primary_key=True,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id"),
        primary_key=True,
    )

    relation_type: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )