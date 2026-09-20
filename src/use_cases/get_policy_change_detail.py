import uuid
from dataclasses import dataclass
from datetime import datetime
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.exceptions import NotFoundError
from src.models.claim import Claim
from src.models.claim_correspondence import ClaimCorrespondence
from src.models.claim_evidence import ClaimEvidence
from src.models.document import Document
from src.models.document_version import DocumentVersion
from src.models.evidence import Evidence
from src.models.policy_change import PolicyChange
from src.models.policy_change_claim import PolicyChangeClaim
from src.models.policy_change_correspondence import (
    PolicyChangeCorrespondence,
)
from src.models.section import Section
from src.models.source import Source


@dataclass(frozen=True)
class EvidenceDetail:
    id: uuid.UUID
    page: int | None
    quote: str
    confidence: str | None
    relation_type: str
    strength: float | None


@dataclass(frozen=True)
class SourceDetail:
    id: uuid.UUID
    name: str
    authority_tier: str
    base_url: str | None
    institution_type: str | None


@dataclass(frozen=True)
class DocumentDetail:
    id: uuid.UUID
    title: str
    document_type: str
    url: str | None
    version_id: uuid.UUID
    version_label: str | None
    publication_date: datetime | None
    effective_date: datetime | None
    source: SourceDetail


@dataclass(frozen=True)
class SectionDetail:
    id: uuid.UUID
    section_number: str | None
    title: str | None
    page_start: int | None
    page_end: int | None
    document: DocumentDetail


@dataclass(frozen=True)
class ClaimDetail:
    id: uuid.UUID
    claim_type: str
    text: str
    normalized_text: str | None
    effective_from: datetime | None
    effective_to: datetime | None
    status: str
    section: SectionDetail
    evidence: tuple[EvidenceDetail, ...]


@dataclass(frozen=True)
class CorrespondenceDetail:
    id: uuid.UUID
    relationship_type: str
    confidence: float | None
    method: str
    status: str


@dataclass(frozen=True)
class PolicyChangeDetailResult:
    id: uuid.UUID
    change_type: str
    summary: str
    effective_date: datetime | None
    reason_claim: ClaimDetail | None
    status: str
    detected_at: datetime
    old_claim: ClaimDetail | None
    new_claim: ClaimDetail | None
    correspondence: CorrespondenceDetail | None


class GetPolicyChangeDetail:
    def execute(
        self,
        session: Session,
        *,
        policy_change_id: uuid.UUID,
    ) -> PolicyChangeDetailResult:
        policy_change = session.scalar(
            select(PolicyChange).where(
                PolicyChange.id == policy_change_id
            )
        )

        if policy_change is None:
            raise NotFoundError(
                f"Policy change not found: {policy_change_id}"
            )

        claim_links = session.scalars(
            select(PolicyChangeClaim).where(
                PolicyChangeClaim.policy_change_id
                == policy_change.id
            )
        ).all()

        old_claim = None
        new_claim = None

        for link in claim_links:
            claim = session.scalar(
                select(Claim).where(
                    Claim.id == link.claim_id
                )
            )

            if claim is None:
                continue

            if link.role == "OLD":
                old_claim = claim
            elif link.role == "NEW":
                new_claim = claim

        correspondence = self._get_correspondence(
            session,
            policy_change.id,
        )

        return PolicyChangeDetailResult(
            id=policy_change.id,
            change_type=policy_change.change_type,
            summary=policy_change.summary,
            effective_date=policy_change.effective_date,
            reason_claim=self._get_claim_detail(
                session,
                policy_change.reason_claim_id,
            ),
            status=policy_change.status,
            detected_at=policy_change.detected_at,
            old_claim=self._get_claim_detail(
                session,
                old_claim.id if old_claim else None,
            ),
            new_claim=self._get_claim_detail(
                session,
                new_claim.id if new_claim else None,
            ),
            correspondence=correspondence,
        )

    @staticmethod
    def _get_correspondence(
        session: Session,
        policy_change_id: uuid.UUID,
    ) -> CorrespondenceDetail | None:
        link = session.scalar(
            select(PolicyChangeCorrespondence).where(
                PolicyChangeCorrespondence.policy_change_id
                == policy_change_id
            )
        )

        if link is None:
            return None

        correspondence = session.scalar(
            select(ClaimCorrespondence).where(
                ClaimCorrespondence.id
                == link.correspondence_id
            )
        )

        if correspondence is None:
            return None

        return CorrespondenceDetail(
            id=correspondence.id,
            relationship_type=correspondence.relationship_type,
            confidence=correspondence.confidence,
            method=correspondence.method,
            status=correspondence.status,
        )

    @classmethod
    def _get_claim_detail(
        cls,
        session: Session,
        claim_id: uuid.UUID | None,
    ) -> ClaimDetail | None:
        if claim_id is None:
            return None

        claim = session.scalar(
            select(Claim).where(Claim.id == claim_id)
        )

        if claim is None:
            return None

        section = session.scalar(
            select(Section).where(
                Section.id == claim.section_id
            )
        )

        if section is None:
            return None

        document_version = session.scalar(
            select(DocumentVersion).where(
                DocumentVersion.id
                == section.document_version_id
            )
        )

        if document_version is None:
            return None

        document = session.scalar(
            select(Document).where(
                Document.id == document_version.document_id
            )
        )

        if document is None:
            return None

        source = session.scalar(
            select(Source).where(
                Source.id == document.source_id
            )
        )

        if source is None:
            return None

        return ClaimDetail(
            id=claim.id,
            claim_type=claim.claim_type,
            text=claim.text,
            normalized_text=claim.normalized_text,
            effective_from=claim.effective_from,
            effective_to=claim.effective_to,
            status=claim.status,
            section=SectionDetail(
                id=section.id,
                section_number=section.section_number,
                title=section.title,
                page_start=section.page_start,
                page_end=section.page_end,
                document=DocumentDetail(
                    id=document.id,
                    title=document.title,
                    document_type=document.document_type,
                    url=document.url,
                    version_id=document_version.id,
                    version_label=document_version.version_label,
                    publication_date=(
                        document_version.publication_date
                    ),
                    effective_date=(
                        document_version.effective_date
                    ),
                    source=SourceDetail(
                        id=source.id,
                        name=source.name,
                        authority_tier=source.authority_tier,
                        base_url=source.base_url,
                        institution_type=(
                            source.institution_type
                        ),
                    ),
                ),
            ),
            evidence=tuple(
                cls._get_evidence(
                    session,
                    claim.id,
                )
            ),
        )

    @staticmethod
    def _get_evidence(
        session: Session,
        claim_id: uuid.UUID,
    ) -> list[EvidenceDetail]:
        rows = session.execute(
            select(
                Evidence,
                ClaimEvidence.relation_type,
                ClaimEvidence.strength,
            )
            .join(
                ClaimEvidence,
                ClaimEvidence.evidence_id == Evidence.id,
            )
            .where(
                ClaimEvidence.claim_id == claim_id,
            )
        ).all()

        return [
            EvidenceDetail(
                id=evidence.id,
                page=evidence.page,
                quote=evidence.quote,
                confidence=evidence.confidence,
                relation_type=relation_type,
                strength=strength,
            )
            for evidence, relation_type, strength in rows
        ]
