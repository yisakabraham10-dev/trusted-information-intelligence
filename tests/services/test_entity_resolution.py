import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.entity import Entity
from src.services.entity_resolution import EntityResolutionService


def test_resolve_creates_entity():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = EntityResolutionService()

        entity = service.resolve(
            db,
            entity_type="BUSINESS_TYPE",
            name="importer",
        )

        db.commit()

        assert entity.id is not None
        assert entity.entity_type == "BUSINESS_TYPE"
        assert entity.name == "IMPORTER"


def test_resolve_reuses_existing_entity():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = EntityResolutionService()

        first = service.resolve(
            db,
            entity_type="BUSINESS_TYPE",
            name="importer",
        )

        db.commit()

        second = service.resolve(
            db,
            entity_type="BUSINESS_TYPE",
            name="Importer",
        )

        assert first.id == second.id

        entities = db.query(Entity).all()

        assert len(entities) == 1


def test_resolve_normalizes_whitespace():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = EntityResolutionService()

        entity = service.resolve(
            db,
            entity_type="BUSINESS_TYPE",
            name="  imported   goods  ",
        )

        assert entity.name == "IMPORTED GOODS"


def test_resolve_keeps_entity_types_distinct():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = EntityResolutionService()

        business_type = service.resolve(
            db,
            entity_type="BUSINESS_TYPE",
            name="coffee",
        )

        product = service.resolve(
            db,
            entity_type="PRODUCT",
            name="coffee",
        )

        assert business_type.id != product.id


def test_empty_name_is_rejected():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = EntityResolutionService()

        with pytest.raises(
            ValueError,
            match="Entity name cannot be empty",
        ):
            service.resolve(
                db,
                entity_type="BUSINESS_TYPE",
                name="   ",
            )