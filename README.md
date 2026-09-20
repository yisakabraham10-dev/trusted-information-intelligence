# Trusted Information Intelligence

**Evidence-centered regulatory intelligence for Ethiopia.**

Trusted Information Intelligence is a regulatory information platform designed to transform fragmented government publications and regulatory documents into traceable, structured, version-aware knowledge.

Instead of treating regulatory information as a collection of documents or a generic RAG knowledge base, the system models the underlying relationships between:

```text
Sources
   ↓
Documents
   ↓
Document Versions
   ↓
Sections / Articles
   ↓
Claims
   ↓
Evidence
   ↓
Entities
   ↓
Claim Correspondence
   ↓
Policy Changes
   ↓
Business Applicability
   ↓
Business Actions
```

The central design principle is:

> **AI proposes. Evidence supports. Deterministic logic compares. Humans resolve uncertainty.**

---

# Why This Exists

Businesses in Ethiopia often encounter regulatory information through fragmented channels:

* Government websites
* Proclamations
* Directives
* Customs publications
* Institutional announcements
* Telegram
* Social media
* News reports
* Informal explanations

The difficult question is therefore not simply:

> "What does the law say?"

It is:

> **"What changed, when did it change, who does it affect, why did it change, what should I do, and what evidence proves it?"**

A normal document search system can retrieve relevant text.

A generic RAG system can generate an answer.

Neither necessarily provides a reliable representation of regulatory change over time.

Trusted Information Intelligence is designed around that problem.

---

# Core Objectives

The platform aims to answer five questions for every important regulatory change.

## 1. What changed?

Identify the semantic difference between the previous and current versions of a regulatory requirement.

## 2. When did it change?

Track publication dates, effective dates, document versions, and temporal validity.

## 3. Why did it change?

Associate a change with explicit reasons stated in source material where available.

## 4. Who is affected?

Resolve the entities and conditions associated with a claim and evaluate them against a business profile.

## 5. What should they do?

Translate applicable regulatory changes into actionable business implications.

Every important answer should remain connected to its underlying evidence.

---

# The Trust Model

The system deliberately separates generation from authority.

```text
                    ┌─────────────────────┐
                    │   Official Sources  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Document Ingestion  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Evidence Extraction │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Claim Construction  │
                    └──────────┬──────────┘
                               ↓
              ┌────────────────┴────────────────┐
              ↓                                 ↓
       Entity Resolution              Claim Correspondence
              │                                 │
              └────────────────┬────────────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Change Detection    │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Policy Change       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Applicability       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Business Action     │
                    └─────────────────────┘
```

The LLM is **not** the final authority.

It may propose:

* Claims
* Entities
* Relationships
* Candidate correspondences
* Explanations

But authoritative conclusions must ultimately be grounded in stored evidence and validated by deterministic logic or human review.

---

# Uncertainty Model

The system is explicitly designed to fail toward uncertainty rather than fabricated certainty.

Important states include:

```text
Extraction
    EXTRACTED
    EXTRACTION_UNCERTAIN

Evidence
    SUPPORTED
    UNSUPPORTED
    EVIDENCE_UNCERTAIN

Entity Resolution
    RESOLVED
    UNRESOLVED

Claim Correspondence
    MATCHED
    UNRELATED
    CORRESPONDENCE_UNCERTAIN

Applicability
    APPLIES
    DOES_NOT_APPLY
    UNKNOWN

Overall
    CONFIRMED
    REQUIRES_REVIEW
```

The core rule is:

```text
Certain + evidenced
        ↓
      Proceed

Uncertain
        ↓
   Review / Stop

Unsupported
        ↓
      Reject

Missing information
        ↓
      UNKNOWN
```

This is particularly important for regulatory information because a confident but unsupported conclusion can be more harmful than an explicit uncertainty.

---

# Architecture

## High-Level Architecture

```text
                    External Regulatory Sources
                              │
                              ▼
                     ┌─────────────────┐
                     │ Source /        │
                     │ Document        │
                     │ Ingestion       │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Regulatory      │
                     │ Structure       │
                     │ Parser          │
                     └────────┬────────┘
                              │
                              ▼
                        DocumentVersion
                              │
                              ▼
                           Sections
                              │
                              ▼
                           Evidence
                              │
                              ▼
                            Claims
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          Entities      ClaimEntity      ClaimEvidence
              │
              ▼
       Claim Correspondence
              │
              ▼
        Change Detection
              │
              ▼
         Policy Changes
              │
              ▼
      Business Applicability
              │
              ▼
          Business API
              │
              ▼
          User Interface
```

The relational database remains the authoritative structured representation.

---

# Evidence-Centered Knowledge Model

The system intentionally does not represent a regulation as one giant block of text.

Instead, it decomposes regulatory information into increasingly structured layers.

```text
Source
   ↓
Document
   ↓
DocumentVersion
   ↓
Section
   ↓
Evidence
   ↓
Claim
   ↓
Entity / Relationships
   ↓
Correspondence
   ↓
PolicyChange
```

Each layer preserves the connection to the layer below it.

---

# Sources

A `Source` represents an institution or authoritative origin.

Examples include:

* Ethiopian Customs Commission
* National Bank of Ethiopia
* Ethiopian Food and Drug Authority
* Ministry of Trade
* Ethiopian Coffee and Tea Authority

A source contains authority and institutional metadata.

```text
Source
├── name
├── authority_tier
├── base_url
├── institution_type
├── description
└── is_active
```

This allows the system to distinguish primary regulatory evidence from secondary reporting.

Sources are also used for business-level monitoring.

A business can track one or more authoritative sources:

```text
BusinessProfile
       │
       │ tracks
       ▼
BusinessProfileSource
       │
       ▼
Source
```

The association is intentionally modeled as a separate relationship rather than embedding source-specific logic into business profiles.

---

# Documents

A `Document` represents a logical regulatory document.

For example:

```text
Customs Proclamation
```

A document can have multiple versions.

```text
Document
    │
    ├── Version 2014
    │
    ├── Version 2020
    │
    └── Version 2026
```

This distinction is critical because regulatory intelligence is fundamentally temporal.

---

# Document Versions

A `DocumentVersion` represents a particular published version of a document.

Important metadata includes:

```text
DocumentVersion
├── publication_date
├── effective_date
├── content_hash
├── storage_path
├── status
└── supersedes_version_id
```

The content hash provides an immutable identity for the retrieved document.

The `supersedes_version_id` relationship allows versions to form a temporal chain.

This makes it possible to compare a current provision with the provision that preceded it rather than comparing arbitrary text fragments.

---

# Sections and Articles

Regulatory documents are structured into sections and articles.

A section contains information such as:

```text
Section
├── section_number
├── title
├── page_start
├── page_end
├── raw_text
└── parent_section_id
```

This preserves the original legal structure while allowing the system to reason about individual provisions.

For example:

```text
Article 51
├── 51(1)
├── 51(2)
├── 51(7)
└── 51(8)
```

The original section remains available as evidence.

---

# Evidence

Evidence is one of the most important invariants in the system.

A claim should not become authoritative merely because an AI model generated it.

The provenance chain is:

```text
PolicyChange
    ↓
ClaimCorrespondence
    ↓
Claim
    ↓
ClaimEvidence
    ↓
Evidence
    ↓
Section
    ↓
DocumentVersion
    ↓
Document
    ↓
Source
```

An evidence record contains information such as:

```text
Evidence
├── section_id
├── page
├── quote
├── confidence
└── created_at
```

This allows the system to answer:

> "Where exactly did this claim come from?"

rather than simply producing an unsupported generated answer.

## Evidence Invariant

The claim pipeline requires supporting evidence.

Conceptually:

```text
No evidence
     ↓
No authoritative claim
```

Evidence must belong to the relevant section and therefore remains connected to the source document and document version.

---

# Claims

A claim is a structured representation of an assertion made by a regulatory source.

For example:

> Goods imported by sea or land must be removed from temporary customs storage within 45 days.

Rather than treating this only as text, the system can represent the underlying semantics:

```text
Actor
    ↓
Customs-regulated importer / owner

Modality
    ↓
REQUIRED

Action
    ↓
Remove

Object
    ↓
Goods

Deadline
    ↓
45 days
```

The current claim representation retains:

```text
Claim
├── section_id
├── claim_type
├── text
├── normalized_text
├── effective_from
├── effective_to
└── status
```

The raw claim text is retained.

The normalized representation exists to support comparison and matching.

---

# Claim Types

Claims are not forced into a single universal structure.

Different regulatory statements have different semantics.

Current structural concepts include:

```text
Requirement
├── actor
├── modality
├── action
├── object
├── deadline
└── exceptions

Fee
├── subject
├── attribute
└── value

Definition
├── term
└── definition

Applicability
├── subject
└── condition

Exception
├── modifies_claim
└── condition

Penalty
├── violation
└── consequence
```

This gives the system a structured semantic layer without forcing every regulatory statement into an artificial schema.

---

# Entities

Regulations refer to many real-world entities:

* Organizations
* Industries
* Products
* Activities
* Jurisdictions
* Transport modes
* Business types

These are represented separately through canonical `Entity` records.

```text
Entity
├── entity_type
├── name
└── description
```

Entity names are normalized and uniquely constrained by:

```text
(entity_type, name)
```

This allows different claims to reference the same canonical entity.

---

# Entity Resolution

Entity resolution is deliberately deterministic at the current stage.

The current process is:

```text
Raw entity name
       ↓
Normalize whitespace
       ↓
Normalize case
       ↓
Search by type + normalized name
       ↓
Existing entity?
    /        \
  yes         no
  ↓            ↓
reuse       create
```

The current system intentionally does not silently perform:

* Fuzzy matching
* Embeddings
* LLM semantic matching

This is important because incorrectly merging two legal entities can be worse than failing to merge them.

More advanced resolution can later operate as a proposal-and-review process.

---

# Claim ↔ Entity Relationships

A `ClaimEntity` relationship connects claims to canonical entities.

For example:

```text
Claim
  │
  └── SUBJECT_OF → Importer
```

This creates a reusable entity layer that supports applicability evaluation.

---

# Structured Claim Semantics

For structured requirements, the system compares semantic fields instead of simply comparing strings.

For example:

```text
Old:
Goods must be removed within 60 days.

New:
Goods must be removed within 45 days.
```

The textual representation changed.

More importantly, the structured field changed:

```text
deadline:
    60 days
        ↓
    45 days
```

This allows the system to explain the actual regulatory difference.

---

# Primitive Comparison

Primitive values are compared using explicit semantics.

Supported comparison concepts include:

```text
SAME
VALUE_CHANGED
UNIT_CHANGED
DIMENSION_CHANGED
PRESENCE_CHANGED
UNKNOWN
```

For example:

```text
60 days → 45 days
```

is a value change.

Likewise:

```text
2 kg → 2000 g
```

can be recognized as equivalent when the units are safely convertible.

The system deliberately avoids unsafe assumptions such as:

```text
1 month == 30 days
```

because calendar durations are not necessarily fixed durations.

---

# Claim Correspondence

One of the central concepts in the architecture is the separation between:

> **"Are these claims about the same underlying rule?"**

and:

> **"How did the rule change?"**

These are not the same question.

`ClaimCorrespondence` answers the first.

`PolicyChange` answers the second.

## Version-Specific Claims

A claim is a version-specific assertion.

For example:

```text
2014 Claim
"Goods must be removed within 60 days."

2026 Claim
"Goods must be removed within 45 days."
```

These are separate claims.

## Correspondence

The system can establish:

```text
2014 Claim
     │
     │ MODIFIED
     ▼
2026 Claim
```

The correspondence records information such as:

```text
relationship_type
confidence
method
status
```

This establishes semantic continuity across versions.

---

# Why PolicyChange Is Separate

A policy change should not be inferred merely from similar text.

Conceptually:

```text
Claim A
   │
   │ correspondence
   ▼
Claim B
   │
   ├── temporal relationship
   ├── structured comparison
   └── evidence
          ↓
     PolicyChange
```

This separation makes the system easier to audit.

A correspondence can exist without necessarily representing a substantive policy change.

---

# Deterministic Change Detection

Once correspondence exists, `ChangeDetector` classifies the relationship.

Current change categories include:

```text
ADDED
REMOVED
MODIFIED
SAME
REQUIRES_REVIEW
```

For a modification, the system can retain structured change descriptions.

Example:

```text
60 days → 45 days
```

becomes:

```text
MODIFIED

deadline:
    60 days → 45 days
```

This is significantly more useful than:

> "The regulation changed."

---

# Policy Change Persistence

A `PolicyChange` retains the relationships needed to reconstruct why the system considers a change to exist.

Conceptually:

```text
PolicyChange
      │
      ├── old claim
      ├── new claim
      └── correspondence
```

The persistence layer is transaction-aware.

Successful operations are committed by the appropriate transaction boundary, while failures roll back related persistence rather than leaving partial change records.

---

# Business Profiles

Regulatory information becomes useful when the system understands the business to which it applies.

The business model is deliberately generic.

Instead of hard-coding rules such as:

```text
if business == coffee_exporter:
```

the system represents business characteristics through relationships to canonical entities.

For example:

```text
Coffee Exporter

BUSINESS_TYPE → EXPORTER
INDUSTRY     → COFFEE
PRODUCT      → COFFEE
DIRECTION    → EXPORT
TRANSPORT    → SEA
```

This allows the same regulatory platform to support:

* Coffee exporters
* Garment importers
* Pharmaceutical distributors
* Electronics importers
* Manufacturing companies

without hard-coding each business type into application logic.

---

# Business Source Tracking

A business profile can track the authoritative sources relevant to it.

```text
BusinessProfile
       │
       ├── BusinessProfileEntity
       │          ↓
       │       Entity
       │
       └── BusinessProfileSource
                  ↓
                Source
```

For example:

```text
Coffee Importer
       │
       ├── Ethiopian Customs Commission
       ├── Ministry of Trade
       └── National Bank of Ethiopia
```

The association is many-to-many:

* One business can track multiple sources.
* One source can be tracked by multiple businesses.
* The same business/source relationship is idempotent.

This provides the foundation for source-specific regulatory intelligence without introducing institution-specific business logic.

---

# Applicability

The current applicability layer evaluates regulatory conditions against a business profile.

The conceptual model is:

```text
PolicyChange
      +
BusinessProfile
      ↓
ApplicabilityService
      ↓
┌───────────────┬────────────────┬───────────┐
│    APPLIES    │ DOES_NOT_APPLY │  UNKNOWN  │
└───────────────┴────────────────┴───────────┘
```

A critical rule is:

> **Missing information should produce `UNKNOWN`, not `DOES_NOT_APPLY`.**

This prevents the system from confidently telling a business that a regulation does not apply simply because its profile is incomplete.

Applicability is currently deterministic rather than LLM-driven.

---

# Real Regulatory Demonstration

The current test suite contains a real regulatory change based on:

**Customs Proclamation (Further Amendment) Proclamation No. 1425/2026**

The system processes the actual PDF through the ingestion pipeline.

The demonstration focuses on Article 51(1).

The earlier provision required relevant sea/land imported goods to be removed within:

```text
60 days
```

The 2026 amendment changes this to:

```text
45 days
```

The system represents this as:

```text
2014 Claim
    │
    │ MODIFIED
    │
    ▼
2026 Claim

deadline:
    60 days → 45 days
```

The resulting `PolicyChange` retains the relationship between the old and new claims and their underlying evidence.

This demonstrates a complete vertical slice through:

```text
PDF
 ↓
Document
 ↓
DocumentVersion
 ↓
Section
 ↓
Evidence
 ↓
Claim
 ↓
ClaimCorrespondence
 ↓
Change Detection
 ↓
PolicyChange
 ↓
Business Applicability
```

---

# Human-in-the-Loop Intelligence

The system is designed around uncertainty rather than pretending every AI output is correct.

The intended workflow is:

```text
AI Proposal
     ↓
Deterministic Validation
     ↓
Confidence / Ambiguity
     ↓
 ┌───────────────┐
 │               │
Certain       Uncertain
 │               │
 ↓               ↓
Accept       Human Review
                 │
                 ↓
             Confirmed
```

Potential review categories include:

* Claim extraction
* Entity resolution
* Claim correspondence
* Applicability

The important principle is:

> **Uncertainty should become a reviewable state, not an invisible hallucination.**

---

# Role of the LLM

LLMs are useful in this system, but they should not become the database of truth.

They are well suited for:

### Claim extraction

Converting regulatory prose into candidate structured claims.

### Entity extraction

Identifying organizations, products, industries, activities, and other entities.

### Candidate correspondence

Identifying claims that may describe the same underlying rule across versions.

### Explanation

Generating human-readable summaries from already validated structured changes.

They should not independently decide:

> "This is definitely the law."

The evidence model remains authoritative.

---

# Amharic and Multilingual Evidence

Ethiopian regulatory information may be published in multiple languages, including Amharic and English.

The system therefore treats language as a representation of the underlying regulatory provision rather than creating separate competing claims simply because the language differs.

The intended approach is:

```text
Original Regulatory Source
        │
        ├── Amharic representation
        │
        └── English representation
                    │
                    ▼
             Same provision
                    │
                    ▼
             Canonical claim
```

The original language remains part of the evidence and provenance chain.

The system should not blindly translate an entire document before extracting its legal structure.

Instead, language-aware extraction should preserve the original evidence while producing a common structured representation where possible.

---

# Document Submission and Human Review

The long-term ingestion boundary is designed to allow human-curated official documents.

A candidate document can follow:

```text
Source Curator
      ↓
Upload PDF
      ↓
Document Submission
      ↓
PENDING_REVIEW
      ↓
Human Preview
      ↓
 ┌────┴────┐
 ▼         ▼
ACCEPT    REJECT
 │
 ▼
Ingestion Pipeline
```

A candidate document is not treated as authoritative merely because it was uploaded.

Potential submission states include:

```text
UPLOADED
PENDING_REVIEW
ACCEPTED
REJECTED
INGESTING
INGESTED
```

This creates a clear trust boundary between unverified input and the authoritative regulatory knowledge layer.

---

# Automated Ingestion

Automated source monitoring is intended as a future extension of the same trust architecture.

The planned flow is:

```text
Official Website
       ↓
Source Connector
       ↓
Document Discovery
       ↓
Document Download
       ↓
Content Hash
       ↓
Candidate Document
       ↓
Human / Validation Boundary
       ↓
DocumentVersion
       ↓
Structure Parser
       ↓
Evidence
       ↓
Claim Extraction
```

A crawler should discover and retrieve documents.

It should **not** independently decide legal semantics.

Potential future source connectors include:

* Ethiopian Customs Commission
* Ministry of Trade
* National Bank of Ethiopia
* Ethiopian Food and Drug Authority
* Ethiopian Coffee and Tea Authority
* Other regulatory institutions

---

# Why This Is Not Just RAG

Traditional RAG generally follows:

```text
Question
   ↓
Retrieve chunks
   ↓
LLM
   ↓
Answer
```

Trusted Information Intelligence instead aims for:

```text
Source
   ↓
Version
   ↓
Section
   ↓
Evidence
   ↓
Claim
   ↓
Correspondence
   ↓
Deterministic Comparison
   ↓
Policy Change
   ↓
Applicability
   ↓
Answer
```

Retrieval can still be used as a supporting mechanism.

It is not the underlying knowledge model.

This distinction matters because regulatory intelligence requires:

* Versioning
* Provenance
* Semantic comparison
* Evidence
* Applicability
* Uncertainty handling

rather than merely finding text that resembles a question.

---

# Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Pydantic Settings

## Document Processing

* pypdf

## AI / Extraction

* LLM-assisted structured extraction
* Structured validation
* Deterministic post-processing

## Testing

* pytest
* HTTPX

## Development

* Ruff
* Docker / Podman Compose
* PostgreSQL

---

# Repository Structure

```text
trusted-information-intelligence/
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── src/
│   ├── models/
│   │   ├── source.py
│   │   ├── document.py
│   │   ├── document_version.py
│   │   ├── section.py
│   │   ├── claim.py
│   │   ├── evidence.py
│   │   ├── claim_evidence.py
│   │   ├── entity.py
│   │   ├── claim_entity.py
│   │   ├── claim_correspondence.py
│   │   ├── policy_change.py
│   │   ├── policy_change_claim.py
│   │   ├── policy_change_correspondence.py
│   │   ├── business_profile.py
│   │   ├── business_profile_entity.py
│   │   └── business_profile_source.py
│   │
│   ├── services/
│   │   ├── document_ingestion.py
│   │   ├── document_persistence.py
│   │   ├── regulatory_structure.py
│   │   ├── claim_creation.py
│   │   ├── claim_structure.py
│   │   ├── entity_resolution.py
│   │   ├── claim_entity.py
│   │   ├── primitive_comparison.py
│   │   ├── requirement_comparison.py
│   │   ├── claim_correspondence.py
│   │   ├── change_detector.py
│   │   ├── policy_change.py
│   │   ├── applicability.py
│   │   └── BusinessProfileEntity.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── dependencies.py
│   │   └── session.py
│   │
│   ├── config.py
│   ├── main.py
│   └── __init__.py
│
├── tests/
│   ├── fixtures/
│   └── services/
│
├── docker-compose.yml
├── alembic.ini
├── pyproject.toml
├── .env.example
└── README.md
```

---

# Running Locally

## Requirements

* Python 3.12+
* PostgreSQL
* Docker or Podman
* Git

## Install

```bash
git clone https://github.com/yisakabraham10-dev/trusted-information-intelligence.git

cd trusted-information-intelligence

python -m venv .venv

source .venv/bin/activate

pip install -e ".[dev]"
```

## Environment

Copy the example environment:

```bash
cp .env.example .env
```

Configure the PostgreSQL connection as required.

## Start PostgreSQL

Using Podman Compose:

```bash
podman-compose up -d
```

or Docker Compose:

```bash
docker compose up -d
```

## Run migrations

```bash
alembic upgrade head
```

## Start the API

```bash
uvicorn src.main:app --reload
```

The current API exposes the initial health endpoints:

```text
GET /health
GET /health/db
```

The domain and persistence layers currently provide substantially more functionality than the initial HTTP API surface. API exposure is the current development stage.

---

# Testing

Run the full suite:

```bash
pytest -q
```

Current baseline:

```text
136 passed
```

The test suite covers the core regulatory intelligence pipeline, including:

* Document ingestion
* Regulatory structure parsing
* Document persistence
* Evidence-backed claim creation
* Entity resolution
* Claim/entity relationships
* Entity uniqueness
* Primitive comparisons
* Structured requirement comparisons
* Claim correspondence
* Evidence integrity
* Change detection
* Policy-change persistence
* Transaction rollback behavior
* Provenance
* Business profiles
* Business/entity relationships
* Business/source relationships
* Institution tracking
* Applicability
* Real Customs regulatory-change integration

The goal is not merely high test coverage.

The goal is to protect **domain invariants**.

Examples:

```text
A claim requires supporting evidence.

An entity is canonical within its type/name identity.

A correspondence connects specific claims.

A policy change references the claims establishing the change.

A business can track multiple authoritative sources.

The same business/source relationship is idempotent.

Missing applicability information produces UNKNOWN.

An uncertain comparison should not silently become a confirmed fact.
```

---

# Database Migrations

Database schema changes are managed through Alembic.

The migration history represents the evolution of the regulatory intelligence model.

For example, the institution-tracking feature introduced:

```text
business_profile_sources
```

with:

```text
business_profile_id → business_profiles.id
source_id           → sources.id
```

and a uniqueness constraint over:

```text
(business_profile_id, source_id)
```

Schema changes should be introduced through migrations rather than modifying the database manually.

---

# Development Philosophy

This project follows several principles.

## 1. Evidence before explanation

The system should know where a statement came from before it explains that statement.

## 2. Version before comparison

Never compare regulatory text without knowing which versions the claims came from.

## 3. Structure before semantics

Where possible, compare structured fields rather than relying solely on string similarity.

## 4. Deterministic logic before probabilistic inference

Use deterministic rules for things that can be determined reliably.

Use AI for things that genuinely require interpretation.

## 5. Uncertainty is a first-class state

If the system does not know, it should say so.

## 6. Human review resolves ambiguity

Humans should resolve important uncertain cases rather than allowing a model to silently guess.

## 7. Preserve the original evidence

Generated representations should never replace the underlying regulatory document.

## 8. Keep domain logic independent from interfaces

The regulatory intelligence domain should not depend on FastAPI, HTML, or other presentation layers.

API routes should orchestrate application behavior rather than becoming a second location for business logic.

---

# What Is Currently Implemented

## Regulatory Knowledge Layer

* [x] FastAPI application
* [x] PostgreSQL persistence
* [x] Alembic migrations
* [x] Source model
* [x] Document model
* [x] Document versioning
* [x] PDF ingestion
* [x] Regulatory section parsing
* [x] Evidence persistence
* [x] Evidence-backed claims
* [x] Entity model
* [x] Deterministic entity resolution
* [x] Claim/entity relationships
* [x] Entity uniqueness constraint
* [x] Structured requirement semantics
* [x] Primitive comparison
* [x] Requirement comparison
* [x] Claim correspondence
* [x] Evidence integrity
* [x] Deterministic change detection
* [x] Policy change persistence
* [x] Transaction handling
* [x] Provenance chain

## Business Intelligence Layer

* [x] Business profiles
* [x] Business/entity relationships
* [x] Business/source relationships
* [x] Multiple tracked sources per business
* [x] Idempotent source tracking
* [x] Applicability evaluation
* [x] `APPLIES` / `DOES_NOT_APPLY` / `UNKNOWN` states

## AI / Extraction

* [x] Structured LLM-assisted claim extraction
* [x] Evidence-aware extraction
* [x] Structured claim validation
* [x] Uncertainty-aware extraction boundaries

## Demonstration

* [x] Real Customs Proclamation integration
* [x] Article 51(1) demonstration
* [x] 60-day → 45-day regulatory change
* [x] Claim correspondence
* [x] Deterministic change detection
* [x] PolicyChange persistence
* [x] Business applicability path

## API

* [x] FastAPI application
* [x] Database dependency
* [x] Health endpoint
* [x] Database health endpoint
* [ ] Business profile endpoints
* [ ] Source tracking endpoints
* [ ] Regulatory change endpoints
* [ ] Evidence/provenance endpoints
* [ ] Document endpoints

---

# Current Development Stage

The core domain/backend layer is implemented and tested.

The current architecture can already represent:

```text
Official Source
      ↓
Document
      ↓
Document Version
      ↓
Section
      ↓
Evidence
      ↓
Claim
      ↓
Entity
      ↓
Claim Correspondence
      ↓
Change Detection
      ↓
PolicyChange
      ↓
Business Profile
      ↓
Applicability
```

The current test baseline is:

```text
136 passed
```

The next major stage is **API/application-layer exposure**.

The API should expose the existing domain capabilities without moving regulatory business logic into FastAPI routes.

After that, the project can progress toward a user-facing regulatory intelligence interface.

---

# Planned Development

## API / Application Layer

* Business profile endpoints
* Source tracking endpoints
* Regulatory change endpoints
* Evidence and provenance endpoints
* Document endpoints
* API-level error handling
* Pydantic request/response schemas
* Application-layer transaction orchestration

## Human Review

* Document submission
* PDF preview
* Candidate document review
* Claim review
* Entity resolution review
* Correspondence review
* Applicability review

## Source Monitoring

* Official-source crawlers
* Document discovery
* Automated version detection
* Scheduled ingestion
* Content hashing
* Candidate document pipeline

## Business Intelligence

* Business-specific regulatory dashboards
* Regulatory alerts
* Action generation
* Source-specific monitoring

## Interface

* Regulatory change dashboard
* Evidence viewer
* Claim comparison UI
* Business profile UI
* Human review interface

These features should build on the existing evidence-centered domain rather than bypassing it.

---

# Longer-Term Direction

The eventual system can evolve toward:

```text
                 ┌───────────────────┐
                 │ Official Sources  │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Automated Monitor │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Regulatory Graph  │
                 │   (Relational)    │
                 └─────────┬─────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
        Changes        Entities       Evidence
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                  Business Profiles
                           │
                           ▼
                     Applicability
                           │
                           ▼
                       Actions
```

The database remains relational.

Graph-like relationships are represented explicitly through relational models rather than requiring a separate graph database for the initial system.

---

# What This Project Is Not

## A generic chatbot

The goal is not simply to put a chat interface over a language model.

## A document dump

Documents are inputs to a structured knowledge system.

## A naive RAG application

Retrieval can support the system, but it is not treated as the fundamental representation of regulatory knowledge.

## An AI legal authority

The system does not replace legal professionals or government authorities.

## A system that hides uncertainty

Uncertainty should be visible and reviewable.

## A system that invents regulatory conclusions

Important claims must remain connected to evidence.

---

# Current Status

**Status: Active development**

The core evidence, claim, correspondence, change-detection, policy-change, business-profile, source-tracking, and applicability layers are implemented and covered by automated tests.

The current system can demonstrate a complete regulatory-change workflow using a real Ethiopian customs proclamation:

```text
Real PDF
   ↓
Ingestion
   ↓
Regulatory Structure
   ↓
Evidence
   ↓
Claim
   ↓
Entity
   ↓
Claim Correspondence
   ↓
Deterministic Comparison
   ↓
Policy Change
   ↓
Business Applicability
```

The current implementation has reached the point where the next major engineering task is no longer building the underlying regulatory model.

It is exposing that model through a clean application/API boundary and then building the user-facing intelligence interface.

The longer-term automated workflow is:

```text
Official Source
      ↓
Source Monitor
      ↓
Candidate Document
      ↓
Validation / Human Review
      ↓
Document Version
      ↓
LLM Proposal
      ↓
Deterministic Validation
      ↓
Confirmed Claim
      ↓
Correspondence
      ↓
Policy Change
      ↓
Business Applicability
      ↓
Business Action
```

---

# Design Principle

Ultimately, Trusted Information Intelligence is built around one idea:

> **A useful answer is not merely an answer that sounds correct. It is an answer whose reasoning can be traced back to evidence, whose temporal context is known, whose changes can be explained, and whose uncertainty is explicit.**
