import uuid

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.business_profile import BusinessProfile
from src.models.business_profile_entity import BusinessProfileEntity
from src.models.business_profile_source import BusinessProfileSource
from src.models.entity import Entity
from src.models.source import Source


@pytest.fixture
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_get_business_profile_returns_profile_with_entities_and_sources(
    client,
    db,
):
    profile = BusinessProfile(
        name="Sea Coffee Importer",
        description=None,
        status="ACTIVE",
    )
    db.add(profile)
    db.flush()

    activity = Entity(
        entity_type="ACTIVITY",
        name="Import",
        description=None,
    )
    transport_mode = Entity(
        entity_type="TRANSPORT_MODE",
        name="Sea",
        description=None,
    )
    db.add_all([activity, transport_mode])
    db.flush()

    db.add_all(
        [
            BusinessProfileEntity(
                business_profile_id=profile.id,
                entity_id=activity.id,
                relation_type="ACTIVITY",
            ),
            BusinessProfileEntity(
                business_profile_id=profile.id,
                entity_id=transport_mode.id,
                relation_type="TRANSPORT_MODE",
            ),
        ]
    )

    source = Source(
        name="Ethiopian Customs Commission",
        authority_tier="PRIMARY",
        base_url="https://example.gov.et",
        institution_type="GOVERNMENT",
        description=None,
        is_active=True,
    )
    db.add(source)
    db.flush()

    db.add(
        BusinessProfileSource(
            business_profile_id=profile.id,
            source_id=source.id,
        )
    )

    db.commit()

    response = client.get(
        f"/business-profiles/{profile.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(profile.id)
    assert data["name"] == "Sea Coffee Importer"
    assert data["status"] == "ACTIVE"

    assert {
        (
            entity["entity_type"],
            entity["name"],
            entity["relation_type"],
        )
        for entity in data["entities"]
    } == {
        ("ACTIVITY", "Import", "ACTIVITY"),
        ("TRANSPORT_MODE", "Sea", "TRANSPORT_MODE"),
    }

    assert data["tracked_sources"] == [
        {
            "id": str(source.id),
            "name": "Ethiopian Customs Commission",
            "authority_tier": "PRIMARY",
            "institution_type": "GOVERNMENT",
            "base_url": "https://example.gov.et",
        }
    ]


def test_get_business_profile_returns_empty_relationships(
    client,
    db,
):
    profile = BusinessProfile(
        name="Empty Profile",
        description="No tracked entities or sources.",
        status="ACTIVE",
    )

    db.add(profile)
    db.commit()

    response = client.get(
        f"/business-profiles/{profile.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(profile.id)
    assert data["name"] == "Empty Profile"
    assert data["description"] == (
        "No tracked entities or sources."
    )
    assert data["entities"] == []
    assert data["tracked_sources"] == []


def test_get_business_profile_returns_404_when_profile_does_not_exist(
    client,
):
    profile_id = uuid.uuid4()

    response = client.get(
        f"/business-profiles/{profile_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Business profile not found."
    }
