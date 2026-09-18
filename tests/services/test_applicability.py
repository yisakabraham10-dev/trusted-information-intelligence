from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.db.base import Base
from src.models.business_profile import BusinessProfile
from src.services.applicability import (
    ApplicabilityCondition,
    ApplicabilityService,
    ApplicabilityStatus,
)
from src.services.BusinessProfileEntity import BusinessProfileService


def create_database():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_applicability_applies_when_condition_matches():
    engine = create_database()

    with Session(engine) as db:
        profile_service = BusinessProfileService()
        applicability = ApplicabilityService()

        profile = profile_service.create(
            db,
            name="Sea Coffee Importer",
        )

        profile_service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="ACTIVITY",
            name="Import",
            relation_type="ACTIVITY",
        )

        profile_service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="TRANSPORT_MODE",
            name="Sea",
            relation_type="TRANSPORT_MODE",
        )

        result = applicability.evaluate(
            db,
            business_profile_id=profile.id,
            conditions=(
                ApplicabilityCondition(
                    relation_type="ACTIVITY",
                    entity_type="ACTIVITY",
                    entity_names=("Import",),
                ),
                ApplicabilityCondition(
                    relation_type="TRANSPORT_MODE",
                    entity_type="TRANSPORT_MODE",
                    entity_names=("Sea", "Land"),
                ),
            ),
        )

        assert result.status == ApplicabilityStatus.APPLIES
        assert len(result.matched_conditions) == 2
        assert not result.unmatched_conditions


def test_applicability_does_not_apply_when_known_condition_conflicts():
    engine = create_database()

    with Session(engine) as db:
        profile_service = BusinessProfileService()
        applicability = ApplicabilityService()

        profile = profile_service.create(
            db,
            name="Air Coffee Importer",
        )

        profile_service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="ACTIVITY",
            name="Import",
            relation_type="ACTIVITY",
        )

        profile_service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="TRANSPORT_MODE",
            name="Air",
            relation_type="TRANSPORT_MODE",
        )

        result = applicability.evaluate(
            db,
            business_profile_id=profile.id,
            conditions=(
                ApplicabilityCondition(
                    relation_type="ACTIVITY",
                    entity_type="ACTIVITY",
                    entity_names=("Import",),
                ),
                ApplicabilityCondition(
                    relation_type="TRANSPORT_MODE",
                    entity_type="TRANSPORT_MODE",
                    entity_names=("Sea", "Land"),
                ),
            ),
        )

        assert result.status == ApplicabilityStatus.DOES_NOT_APPLY


def test_applicability_is_unknown_when_required_information_is_missing():
    engine = create_database()

    with Session(engine) as db:
        profile_service = BusinessProfileService()
        applicability = ApplicabilityService()

        profile = profile_service.create(
            db,
            name="Unspecified Importer",
        )

        profile_service.attach_entity(
            db,
            business_profile_id=profile.id,
            entity_type="ACTIVITY",
            name="Import",
            relation_type="ACTIVITY",
        )

        result = applicability.evaluate(
            db,
            business_profile_id=profile.id,
            conditions=(
                ApplicabilityCondition(
                    relation_type="ACTIVITY",
                    entity_type="ACTIVITY",
                    entity_names=("Import",),
                ),
                ApplicabilityCondition(
                    relation_type="TRANSPORT_MODE",
                    entity_type="TRANSPORT_MODE",
                    entity_names=("Sea", "Land"),
                ),
            ),
        )

        assert result.status == ApplicabilityStatus.UNKNOWN


def test_applicability_is_unknown_without_conditions():
    engine = create_database()

    with Session(engine) as db:
        profile_service = BusinessProfileService()
        applicability = ApplicabilityService()

        profile = profile_service.create(
            db,
            name="Coffee Exporter",
        )

        result = applicability.evaluate(
            db,
            business_profile_id=profile.id,
            conditions=(),
        )

        assert result.status == ApplicabilityStatus.UNKNOWN