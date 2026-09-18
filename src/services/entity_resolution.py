from sqlalchemy.orm import Session

from src.models.entity import Entity


class EntityResolutionService:
    """
    Resolve extracted entity references to canonical Entity records.

    Resolution is intentionally deterministic:
    1. Normalize the supplied name.
    2. Look for an existing entity with the same type and normalized name.
    3. Return the existing entity when found.
    4. Otherwise create a new canonical entity.

    This service does not perform:
    - LLM-based entity extraction
    - embeddings
    - fuzzy matching
    - semantic inference
    """

    @staticmethod
    def normalize_name(name: str) -> str:
        normalized = " ".join(name.strip().split())

        if not normalized:
            raise ValueError("Entity name cannot be empty.")

        return normalized.upper()

    def resolve(
        self,
        db: Session,
        *,
        entity_type: str,
        name: str,
        description: str | None = None,
    ) -> Entity:
        normalized_name = self.normalize_name(name)

        entity = (
            db.query(Entity)
            .filter(
                Entity.entity_type == entity_type,
                Entity.name == normalized_name,
            )
            .one_or_none()
        )

        if entity is not None:
            return entity

        entity = Entity(
            entity_type=entity_type,
            name=normalized_name,
            description=description,
        )

        db.add(entity)
        db.flush()

        return entity