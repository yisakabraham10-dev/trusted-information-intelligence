import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.business_profile import BusinessProfile
from src.models.business_profile_entity import BusinessProfileEntity
from src.services.BusinessProfileEntity import BusinessProfileService


def test_create_business_profile():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        profile = service.create(
            db,
            name="  Ethiopian Coffee Exporter  ",
            description="Coffee export business",
        )

        db.commit()

        assert profile.id is not None
        assert profile.name == "Ethiopian Coffee Exporter"
        assert profile.description == "Coffee export business"
        assert profile.status == "ACTIVE"


def test_create_business_profile_rejects_empty_name():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        with pytest.raises(
            ValueError,
            match="Business profile name cannot be empty",
        ):
            service.create(
                db,
                name="   ",
            )


def test_attach_entity_resolves_canonical_entity():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        profile = service.create(
            db,
            name="Coffee Exporter",
        )

        relationship = service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="INDUSTRY",
            name="Coffee",
            relation_type="INDUSTRY",
        )

        db.commit()

        assert relationship.business_profile_id == profile.id
        assert relationship.entity_id is not None
        assert relationship.relation_type == "INDUSTRY"


def test_attach_same_entity_with_different_relationships():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        profile = service.create(
            db,
            name="Coffee Exporter",
        )

        industry = service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="PRODUCT",
            name="Coffee",
            relation_type="INDUSTRY",
        )

        product = service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="PRODUCT",
            name="Coffee",
            relation_type="PRODUCT",
        )

        db.commit()

        assert industry.entity_id == product.entity_id
        assert industry.relation_type == "INDUSTRY"
        assert product.relation_type == "PRODUCT"


def test_attach_same_relationship_is_idempotent():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        profile = service.create(
            db,
            name="Coffee Exporter",
        )

        first = service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="PRODUCT",
            name="Coffee",
            relation_type="PRODUCT",
        )

        second = service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="PRODUCT",
            name="  coffee  ",
            relation_type="PRODUCT",
        )

        db.commit()

        assert first.entity_id == second.entity_id
        assert first.business_profile_id == second.business_profile_id
        assert first.relation_type == second.relation_type


def test_business_profile_entity_is_persisted():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        service = BusinessProfileService()

        profile = service.create(
            db,
            name="Coffee Exporter",
        )

        service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="ACTIVITY",
            name="Exporting",
            relation_type="ACTIVITY",
        )

        db.commit()

        relationship = (
            db.query(BusinessProfileEntity)
            .filter(
                BusinessProfileEntity.business_profile_id == profile.id
            )
            .one()
        )

        assert relationship.relation_type == "ACTIVITY"