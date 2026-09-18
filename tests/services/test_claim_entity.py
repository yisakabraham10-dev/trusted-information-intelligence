import pytest
from uuid import uuid4

from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.claim import Claim
from src.models.claim_entity import ClaimEntity
from src.models.entity import Entity
from src.models.section import Section
from src.services.claim_entity import ClaimEntityService


def test_attach_entity_creates_entity_and_claim_link():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.flush()

        claim = Claim(
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Imported goods must be removed within 45 days.",
        )

        db.add(claim)
        db.commit()

        service = ClaimEntityService()

        link = service.attach_entity(
            db,
            claim_id=claim.id,
            entity_type="BUSINESS_TYPE",
            name="importer",
            relation_type="ACTOR",
        )

        db.commit()

        assert link.claim_id == claim.id
        assert link.relation_type == "ACTOR"

        entity = db.scalar(select(Entity))

        assert entity is not None
        assert entity.entity_type == "BUSINESS_TYPE"
        assert entity.name == "IMPORTER"

        stored_link = db.scalar(select(ClaimEntity))

        assert stored_link is not None
        assert stored_link.claim_id == claim.id
        assert stored_link.entity_id == entity.id


def test_attach_entity_reuses_existing_entity():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.flush()

        claim_one = Claim(
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Importer must remove goods.",
        )

        claim_two = Claim(
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Importer must complete removal.",
        )

        db.add_all([claim_one, claim_two])
        db.commit()

        service = ClaimEntityService()

        first_link = service.attach_entity(
            db,
            claim_id=claim_one.id,
            entity_type="BUSINESS_TYPE",
            name="importer",
            relation_type="ACTOR",
        )

        second_link = service.attach_entity(
            db,
            claim_id=claim_two.id,
            entity_type="BUSINESS_TYPE",
            name="Importer",
            relation_type="ACTOR",
        )

        db.commit()

        assert first_link.entity_id == second_link.entity_id

        entities = db.scalars(select(Entity)).all()
        links = db.scalars(select(ClaimEntity)).all()

        assert len(entities) == 1
        assert len(links) == 2


def test_attach_same_entity_relationship_is_idempotent():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.flush()

        claim = Claim(
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Importer must remove goods.",
        )

        db.add(claim)
        db.commit()

        service = ClaimEntityService()

        first = service.attach_entity(
            db,
            claim_id=claim.id,
            entity_type="BUSINESS_TYPE",
            name="importer",
            relation_type="ACTOR",
        )

        second = service.attach_entity(
            db,
            claim_id=claim.id,
            entity_type="BUSINESS_TYPE",
            name="importer",
            relation_type="ACTOR",
        )

        db.commit()

        assert first.claim_id == second.claim_id
        assert first.entity_id == second.entity_id

        links = db.scalars(select(ClaimEntity)).all()

        assert len(links) == 1


def test_conflicting_relationship_type_is_rejected():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        section = Section(
            document_version_id=uuid4(),
            section_number="51(1)",
            title=None,
            page_start=3,
            page_end=3,
            raw_text="Imported goods must be removed within 45 days.",
        )

        db.add(section)
        db.flush()

        claim = Claim(
            section_id=section.id,
            claim_type="REQUIREMENT",
            text="Importer must remove goods.",
        )

        db.add(claim)
        db.commit()

        service = ClaimEntityService()

        service.attach_entity(
            db,
            claim_id=claim.id,
            entity_type="BUSINESS_TYPE",
            name="importer",
            relation_type="ACTOR",
        )

        with pytest.raises(ValueError, match="different relation type"):
            service.attach_entity(
                db,
                claim_id=claim.id,
                entity_type="BUSINESS_TYPE",
                name="importer",
                relation_type="OBJECT",
            )