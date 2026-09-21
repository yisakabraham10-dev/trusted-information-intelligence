export type TrustState =
  | "CONFIRMED"
  | "REQUIRES_REVIEW"
  | "SUPPORTED"
  | "UNSUPPORTED"
  | "UNKNOWN"
  | "APPLIES"
  | "DOES_NOT_APPLY";

export type ChangeKind =
  | "MODIFIED"
  | "ADDED"
  | "REMOVED"
  | "REQUIRES_REVIEW";

export interface EvidenceDetail {
  id: string;
  page: number | null;
  quote: string;
  confidence: string | null;
  relation_type: string;
  strength: number | null;
}

export interface SourceDetail {
  id: string;
  name: string;
  authority_tier: string;
  base_url: string | null;
  institution_type: string | null;
}

export interface DocumentDetail {
  id: string;
  title: string;
  document_type: string;
  url: string | null;
  version_id: string;
  version_label: string | null;
  publication_date: string | null;
  effective_date: string | null;
  source: SourceDetail;
}

export interface SectionDetail {
  id: string;
  section_number: string | null;
  title: string | null;
  page_start: number | null;
  page_end: number | null;
  document: DocumentDetail;
}

export interface ClaimDetail {
  id: string;
  claim_type: string;
  text: string;
  normalized_text: string | null;
  effective_from: string | null;
  effective_to: string | null;
  status: string;
  section: SectionDetail;
  evidence: EvidenceDetail[];
}

export interface CorrespondenceDetail {
  id: string;
  relationship_type: string;
  confidence: number | null;
  method: string;
  status: string;
}

export interface PolicyChangeDetail {
  id: string;
  change_type: string;
  summary: string;
  effective_date: string | null;
  reason_claim: ClaimDetail | null;
  status: string;
  detected_at: string;
  old_claim: ClaimDetail | null;
  new_claim: ClaimDetail | null;
  correspondence: CorrespondenceDetail | null;
}

export interface PolicyChange {
  id: string;
  change_type: string;
  summary: string;
  effective_date: string | null;
  reason_claim_id: string | null;
  status: string;
  detected_at: string;
}

export interface BusinessProfileEntity {
  entity_type: string;
  name: string;
  relation_type: string;
}

export interface BusinessProfileSource {
  id: string;
  name: string;
  authority_tier: string;
  institution_type: string | null;
  base_url: string | null;
}

export interface BusinessProfile {
  id: string;
  name: string;
  description: string | null;
  status: string;
  entities: BusinessProfileEntity[];
  tracked_sources: BusinessProfileSource[];
}

export interface CorrespondenceResponse {
  relationship_type: string;
  confidence: number | null;
  method: string;
  changes: string[];
}

export interface ChangeDetectionResponse {
  change_type: string;
  summary: string;
}

export interface PolicyChangePersistenceResponse {
  policy_change_id: string;
  change_type: string;
}

export interface CompareRegulatoryVersionsResponse {
  old_claim_id: string;
  new_claim_id: string;
  correspondence: CorrespondenceResponse | null;
  detection: ChangeDetectionResponse | null;
  policy_change: PolicyChangePersistenceResponse | null;
}
