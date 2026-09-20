from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.domain.exceptions import NotFoundError
from src.models.policy_change import PolicyChange
from src.schemas.policy_changes import (
    ClaimDetailResponse,
    CorrespondenceDetailResponse,
    DocumentDetailResponse,
    EvidenceDetailResponse,
    PolicyChangeDetailResponse,
    PolicyChangeResponse,
    SectionDetailResponse,
    SourceDetailResponse,
)
from src.use_cases.get_policy_change_detail import (
    GetPolicyChangeDetail,
)


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


@router.get(
    "/{policy_change_id}/detail",
    response_model=PolicyChangeDetailResponse,
)
def get_policy_change_detail(
    policy_change_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        result = GetPolicyChangeDetail().execute(
            db,
            policy_change_id=policy_change_id,
        )
    except NotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail="Policy change not found.",
        ) from exc

    return PolicyChangeDetailResponse(
        id=result.id,
        change_type=result.change_type,
        summary=result.summary,
        effective_date=result.effective_date,
        reason_claim=(
            _claim_detail_response(result.reason_claim)
            if result.reason_claim is not None
            else None
        ),
        status=result.status,
        detected_at=result.detected_at,
        old_claim=(
            _claim_detail_response(result.old_claim)
            if result.old_claim is not None
            else None
        ),
        new_claim=(
            _claim_detail_response(result.new_claim)
            if result.new_claim is not None
            else None
        ),
        correspondence=(
            CorrespondenceDetailResponse(
                id=result.correspondence.id,
                relationship_type=(
                    result.correspondence.relationship_type
                ),
                confidence=result.correspondence.confidence,
                method=result.correspondence.method,
                status=result.correspondence.status,
            )
            if result.correspondence is not None
            else None
        ),
    )


def _claim_detail_response(claim):
    return ClaimDetailResponse(
        id=claim.id,
        claim_type=claim.claim_type,
        text=claim.text,
        normalized_text=claim.normalized_text,
        effective_from=claim.effective_from,
        effective_to=claim.effective_to,
        status=claim.status,
        section=SectionDetailResponse(
            id=claim.section.id,
            section_number=claim.section.section_number,
            title=claim.section.title,
            page_start=claim.section.page_start,
            page_end=claim.section.page_end,
            document=DocumentDetailResponse(
                id=claim.section.document.id,
                title=claim.section.document.title,
                document_type=claim.section.document.document_type,
                url=claim.section.document.url,
                version_id=claim.section.document.version_id,
                version_label=(
                    claim.section.document.version_label
                ),
                publication_date=(
                    claim.section.document.publication_date
                ),
                effective_date=(
                    claim.section.document.effective_date
                ),
                source=SourceDetailResponse(
                    id=claim.section.document.source.id,
                    name=claim.section.document.source.name,
                    authority_tier=(
                        claim.section.document.source.authority_tier
                    ),
                    base_url=(
                        claim.section.document.source.base_url
                    ),
                    institution_type=(
                        claim.section.document.source.institution_type
                    ),
                ),
            ),
        ),
        evidence=[
            EvidenceDetailResponse(
                id=evidence.id,
                page=evidence.page,
                quote=evidence.quote,
                confidence=evidence.confidence,
                relation_type=evidence.relation_type,
                strength=evidence.strength,
            )
            for evidence in claim.evidence
        ],
    )
