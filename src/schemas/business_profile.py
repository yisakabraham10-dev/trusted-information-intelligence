from uuid import UUID

from pydantic import BaseModel


class BusinessProfileEntityResponse(BaseModel):
    entity_type: str
    name: str
    relation_type: str


class BusinessProfileSourceResponse(BaseModel):
    id: UUID
    name: str
    authority_tier: str
    institution_type: str | None
    base_url: str | None


class BusinessProfileResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    status: str
    entities: list[BusinessProfileEntityResponse]
    tracked_sources: list[BusinessProfileSourceResponse]
