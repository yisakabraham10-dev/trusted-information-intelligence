from uuid import UUID

from sqlalchemy.orm import Session

from src.models.business_profile import BusinessProfile
from src.models.business_profile_entity import BusinessProfileEntity
from src.services.entity_resolution import EntityResolutionService


class BusinessProfileService:
    """
    Manage business profiles and their relationships to canonical entities.

    The service does not commit transactions.
    The caller owns the transaction boundary.
    """

    def __init__(
        self,
        entity_resolution: EntityResolutionService | None = None,
    ) -> None:
        self.entity_resolution = (
            entity_resolution or EntityResolutionService()
        )

    def create(
        self,
        db: Session,
        *,
        name: str,
        description: str | None = None,
    ) -> BusinessProfile:
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError(
                "Business profile name cannot be empty."
            )

        profile = BusinessProfile(
            name=normalized_name,
            description=description,
        )

        db.add(profile)
        db.flush()

        return profile

    def attach_entity(
        self,
        db: Session,
        *,
        business_profile_id: UUID,
        entity_type: str,
        name: str,
        relation_type: str,
    ) -> BusinessProfileEntity:
        entity = self.entity_resolution.resolve(
            db,
            entity_type=entity_type,
            name=name,
        )

        existing = (
            db.query(BusinessProfileEntity)
            .filter(
                BusinessProfileEntity.business_profile_id
                == business_profile_id,
                BusinessProfileEntity.entity_id
                == entity.id,
                BusinessProfileEntity.relation_type
                == relation_type,
            )
            .one_or_none()
        )

        if existing is not None:
            return existing

        profile_entity = BusinessProfileEntity(
            business_profile_id=business_profile_id,
            entity_id=entity.id,
            relation_type=relation_type,
        )

        db.add(profile_entity)
        db.flush()

        return profile_entity