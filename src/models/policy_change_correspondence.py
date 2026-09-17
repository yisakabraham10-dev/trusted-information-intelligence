import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class PolicyChangeCorrespondence(Base):
    __tablename__ = "policy_change_correspondences"

    policy_change_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_changes.id"),
        primary_key=True,
    )

    correspondence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claim_correspondences.id"),
        primary_key=True,
    )