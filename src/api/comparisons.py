from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.domain.exceptions import InvalidStateError, NotFoundError
from src.schemas.comparisons import (
    ChangeDetectionResponse,
    CompareRegulatoryVersionsResponse,
    CorrespondenceResponse,
    PolicyChangePersistenceResponse,
)
from src.use_cases.compare_regulatory_versions import (
    CompareRegulatoryVersions,
)


router = APIRouter(
    prefix="/claims",
    tags=["comparisons"],
)


@router.post(
    "/{old_claim_id}/compare/{new_claim_id}",
    response_model=CompareRegulatoryVersionsResponse,
)
def compare_claims(
    old_claim_id: UUID,
    new_claim_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        result = CompareRegulatoryVersions().execute(
            db,
            old_claim_id=old_claim_id,
            new_claim_id=new_claim_id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except InvalidStateError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    correspondence = None

    if result.correspondence is not None:
        correspondence = CorrespondenceResponse(
            relationship_type=(
                result.correspondence.relationship_type
            ),
            confidence=result.correspondence.confidence,
            method=result.correspondence.method,
            changes=list(result.correspondence.changes),
        )

    detection = None

    if result.detection is not None:
        detection = ChangeDetectionResponse(
            change_type=result.detection.change_type,
            summary=result.detection.summary,
        )

    policy_change = None

    if result.policy_change is not None:
        policy_change = PolicyChangePersistenceResponse(
            policy_change_id=result.policy_change.policy_change_id,
            change_type=result.policy_change.change_type,
        )

    return CompareRegulatoryVersionsResponse(
        old_claim_id=result.old_claim_id,
        new_claim_id=result.new_claim_id,
        correspondence=correspondence,
        detection=detection,
        policy_change=policy_change,
    )
