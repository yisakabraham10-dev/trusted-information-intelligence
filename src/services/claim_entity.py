from uuid import UUID

from sqlalchemy.orm import Session

from src.models.claim_entity import ClaimEntity
from src.services.entity_resolution import EntityResolutionService


class ClaimEntityService:
    """
    Resolve an entity reference and attach the resulting canonical
    entity to a Claim.
    """

    def __init__(
        self,
        entity_resolution: EntityResolutionService | None = None,
    ) -> None:
        self.entity_resolution = (
            entity_resolution or EntityResolutionService()
        )

    def attach_entity(
        self,
        db: Session,
        *,
        claim_id: UUID,
        entity_type: str,
        name: str,
        relation_type: str,
    ) -> ClaimEntity:
        entity = self.entity_resolution.resolve(
            db,
            entity_type=entity_type,
            name=name,
        )

        existing = (
            db.query(ClaimEntity)
            .filter(
                ClaimEntity.claim_id == claim_id,
                ClaimEntity.entity_id == entity.id,
            )
            .one_or_none()
        )

        if existing is not None:
            if existing.relation_type != relation_type:
                raise ValueError(
                    "Claim entity relationship already exists "
                    "with a different relation type."
                )

            return existing

        claim_entity = ClaimEntity(
            claim_id=claim_id,
            entity_id=entity.id,
            relation_type=relation_type,
        )

        db.add(claim_entity)
        db.flush()

        return claim_entity