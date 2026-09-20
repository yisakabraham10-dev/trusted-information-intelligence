import uuid

import pytest
from fastapi.testclient import TestClient

from src.db.dependencies import get_db
from src.db.session import SessionLocal
from src.main import app
from src.models.policy_change import PolicyChange


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


def test_get_policy_change_returns_policy_change(client, db):
    policy_change = PolicyChange(
        change_type="MODIFIED",
        summary="An existing claim was modified: deadline changed from 60 days to 45 days.",
        effective_date=None,
        reason_claim_id=None,
    )

    db.add(policy_change)
    db.commit()

    response = client.get(
        f"/policy-changes/{policy_change.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(policy_change.id)
    assert data["change_type"] == "MODIFIED"
    assert data["summary"] == (
        "An existing claim was modified: "
        "deadline changed from 60 days to 45 days."
    )
    assert data["effective_date"] is None
    assert data["reason_claim_id"] is None
    assert data["status"] == "ACTIVE"


def test_get_policy_change_returns_404_when_policy_change_does_not_exist(
    client,
):
    policy_change_id = uuid.uuid4()

    response = client.get(
        f"/policy-changes/{policy_change_id}"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Policy change not found."
    }
