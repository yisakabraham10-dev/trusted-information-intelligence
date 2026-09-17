import uuid

from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("claims.id"),
        primary_key=True,
    )

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id"),
        primary_key=True,
    )

    relation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    strength: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )