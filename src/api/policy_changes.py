from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.models.policy_change import PolicyChange
from src.schemas.policy_changes import PolicyChangeResponse

router = APIRouter(
    prefix="/policy-changes",
    tags=["policy-changes"],
)


@router.get(
    "/{policy_change_id}",
    response_model=PolicyChangeResponse,
)
def get_policy_change(
    policy_change_id: UUID,
    db: Session = Depends(get_db),
):
    policy_change = db.scalar(
        select(PolicyChange).where(
            PolicyChange.id == policy_change_id
        )
    )

    if policy_change is None:
        raise HTTPException(
            status_code=404,
            detail="Policy change not found.",
        )

    return policy_change
