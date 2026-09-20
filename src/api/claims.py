from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.models.claim import Claim
from src.schemas.claims import ClaimResponse


router = APIRouter(
    prefix="/claims",
    tags=["claims"],
)


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim(
    claim_id: UUID,
    db: Session = Depends(get_db),
):
    claim = db.scalar(
        select(Claim).where(Claim.id == claim_id)
    )

    if claim is None:
        raise HTTPException(
            status_code=404,
            detail="Claim not found.",
        )

    return claim
