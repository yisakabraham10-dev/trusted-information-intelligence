from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.dependencies import get_db
from src.models.business_profile import BusinessProfile
from src.models.business_profile_entity import BusinessProfileEntity
from src.models.business_profile_source import BusinessProfileSource
from src.models.entity import Entity
from src.models.source import Source
from src.schemas.business_profile import (
    BusinessProfileEntityResponse,
    BusinessProfileResponse,
    BusinessProfileSourceResponse,
)

router = APIRouter(
    prefix="/business-profiles",
    tags=["business-profiles"],
)


@router.get(
    "/{business_profile_id}",
    response_model=BusinessProfileResponse,
)
def get_business_profile(
    business_profile_id: UUID,
    db: Session = Depends(get_db),
):
    profile = db.scalar(
        select(BusinessProfile).where(
            BusinessProfile.id == business_profile_id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Business profile not found.",
        )

    entity_rows = db.execute(
        select(
            Entity.entity_type,
            Entity.name,
            BusinessProfileEntity.relation_type,
        )
        .join(
            BusinessProfileEntity,
            BusinessProfileEntity.entity_id == Entity.id,
        )
        .where(
            BusinessProfileEntity.business_profile_id
            == profile.id
        )
    ).all()

    source_rows = db.execute(
        select(
            Source.id,
            Source.name,
            Source.authority_tier,
            Source.institution_type,
            Source.base_url,
        )
        .join(
            BusinessProfileSource,
            BusinessProfileSource.source_id == Source.id,
        )
        .where(
            BusinessProfileSource.business_profile_id
            == profile.id
        )
    ).all()

    return BusinessProfileResponse(
        id=profile.id,
        name=profile.name,
        description=profile.description,
        status=profile.status,
        entities=[
            BusinessProfileEntityResponse(
                entity_type=entity_type,
                name=name,
                relation_type=relation_type,
            )
            for entity_type, name, relation_type in entity_rows
        ],
        tracked_sources=[
            BusinessProfileSourceResponse(
                id=source_id,
                name=name,
                authority_tier=authority_tier,
                institution_type=institution_type,
                base_url=base_url,
            )
            for (
                source_id,
                name,
                authority_tier,
                institution_type,
                base_url,
            ) in source_rows
        ],
    )
