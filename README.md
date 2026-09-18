Trusted Information Intelligence

Evidence-centered regulatory intelligence for Ethiopia.

Trusted Information Intelligence is a regulatory information platform designed to transform fragmented government publications and regulatory documents into traceable, structured, version-aware knowledge.

Instead of treating regulatory information as a collection of documents or a generic RAG knowledge base, the system models the underlying relationships between:

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
Actions

The central design principle is:

AI proposes. Evidence supports. Deterministic logic compares. Humans resolve uncertainty.

Why this exists

Businesses in Ethiopia often encounter regulatory information through fragmented channels:

government websites
proclamations
directives
customs publications
institutional announcements
Telegram
social media
news reports
informal explanations

The difficult question is therefore not simply:

"What does the law say?"

It is:

"What changed, when did it change, who does it affect, why did it change, what should I do, and what evidence proves it?"

A normal document search system can retrieve relevant text.

A generic RAG system can generate an answer.

Neither necessarily provides a reliable representation of regulatory change over time.

Trusted Information Intelligence is designed around that problem.

Core Objectives

The platform aims to answer five questions for every important regulatory change:

1. What changed?

Identify the semantic difference between the previous and current versions of a regulatory requirement.

2. When did it change?

Track publication dates, effective dates, document versions, and temporal validity.

3. Why did it change?

Associate a change with explicit reasons stated in the source material where available.

4. Who is affected?

Resolve the entities and conditions associated with a claim and evaluate them against a business profile.

5. What should they do?

Translate applicable regulatory changes into actionable business implications.

Every important answer should remain connected to its underlying evidence.

The Trust Model

The system deliberately separates generation from authority.

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

The LLM is not the final authority.

It may propose:

claims
entities
relationships
candidate correspondences
explanations

But authoritative conclusions must ultimately be grounded in stored evidence and validated by deterministic logic or human review.

Architecture
High-level architecture
                    External Regulatory Sources
                              │
                              ▼
                     ┌─────────────────┐
                     │ Source Connectors│
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
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
                ┌─────────────┴─────────────┐
                ▼                           ▼
        DocumentVersion               Sections
                                            │
                                            ▼
                                         Evidence
                                            │
                                            ▼
                                          Claims
                                            │
                       ┌────────────────────┼────────────────────┐
                       ▼                    ▼                    ▼
                    Entities          ClaimEntity       ClaimEvidence
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
Evidence-Centered Knowledge Model

The system intentionally does not represent a regulation as one giant block of text.

Instead, it decomposes regulatory information into increasingly structured layers.

Source

A Source represents an institution or authoritative origin.

Examples include:

Ethiopian Customs Commission
National Bank of Ethiopia
Ethiopian Food and Drug Authority
Ministry of Trade
Ethiopian Coffee and Tea Authority

A source has an authority tier and institutional metadata.

Source
├── name
├── authority_tier
├── base_url
├── institution_type
└── is_active

This allows the system to distinguish primary regulatory evidence from secondary reporting.

Documents

A Document represents a logical regulatory document.

For example:

Customs Proclamation

A document can have multiple versions.

Document
    │
    ├── Version 2014
    │
    ├── Version 2020
    │
    └── Version 2026

This distinction is critical because regulatory intelligence is fundamentally temporal.

Document Versions

A DocumentVersion represents a particular published version of a document.

Important metadata includes:

DocumentVersion
├── publication_date
├── effective_date
├── content_hash
├── storage_path
├── status
└── supersedes_version_id

The content hash provides an immutable identity for the retrieved document.

The supersedes_version_id relationship allows versions to form a temporal chain.

Sections and Articles

Regulatory documents are structured into sections and articles.

A section contains:

Section
├── section_number
├── title
├── page_start
├── page_end
├── raw_text
└── parent_section_id

This preserves the original legal structure while allowing the system to reason about individual provisions.

For example:

Article 51
├── 51(1)
├── 51(2)
├── 51(7)
└── 51(8)

The original section remains available as evidence.

Claims

A claim is a structured representation of an assertion made by a regulatory source.

For example:

Goods imported by sea or land must be removed from temporary customs storage within 45 days.

Rather than treating this only as text, the system can represent the underlying semantics:

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

The current Claim model stores:

Claim
├── section_id
├── claim_type
├── text
├── normalized_text
├── effective_from
├── effective_to
└── status

The raw claim text is retained.

The normalized representation exists to support comparison and matching.

Claim Types

Claims are not forced into a single universal structure.

Different regulatory statements have different semantics.

Current structural concepts include:

Requirement
actor
modality
action
object
deadline
exceptions
Fee
subject
attribute
value
Definition
term
definition
Applicability
subject
condition
Exception
modifies_claim
condition
Penalty
violation
consequence

This gives the system a structured semantic layer without forcing every regulatory statement into an artificial schema.

Evidence

A claim cannot exist without supporting evidence.

This is one of the most important invariants in the system.

Claim
   │
   └── ClaimEvidence
            │
            ▼
         Evidence
            │
            ▼
        Section
            │
            ▼
     DocumentVersion
            │
            ▼
          Source

An evidence record contains:

Evidence
├── section_id
├── page
├── quote
├── confidence
└── created_at

This allows the system to answer:

"Where exactly did this claim come from?"

rather than simply producing an unsupported generated answer.

Claim → Evidence Invariant

The claim creation service enforces:

No evidence
     ↓
No claim

A claim must reference evidence belonging to the relevant section.

This prevents unsupported generated knowledge from silently entering the authoritative knowledge layer.

Entities

Regulations refer to many real-world entities:

organizations
industries
products
activities
jurisdictions
transport modes
business types

These are represented separately through canonical Entity records.

Entity
├── entity_type
├── name
└── description

Entity names are normalized and uniquely constrained by:

(entity_type, name)

This allows different claims to reference the same canonical entity.

Entity Resolution

Entity resolution is deliberately deterministic at the current stage.

The current process is:

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

The current system intentionally does not silently perform:

fuzzy matching
embeddings
LLM semantic matching

This is important because incorrectly merging two legal entities can be worse than failing to merge them.

More advanced resolution can later operate as a proposal-and-review process.

Claim ↔ Entity Relationships

A ClaimEntity relationship connects claims to canonical entities.

For example:

Claim
  │
  └── SUBJECT_OF → Importer

This creates a reusable entity layer that can later support applicability evaluation.

Structured Claim Semantics

For structured requirements, the system compares semantic fields instead of simply comparing strings.

For example:

Old
Goods must be removed within 60 days.
New
Goods must be removed within 45 days.

The textual representation changed.

More importantly, the structured field changed:

deadline:
    60 days
        ↓
    45 days

This allows the system to explain the actual regulatory difference.

Primitive Comparison

Primitive values are compared using explicit semantics.

Supported comparison concepts include:

SAME
VALUE_CHANGED
UNIT_CHANGED
DIMENSION_CHANGED
PRESENCE_CHANGED
UNKNOWN

For example:

60 days → 45 days

is a value change.

Likewise:

2 kg → 2000 g

can be recognized as equivalent when the units are safely convertible.

The system deliberately refuses unsafe conversions such as blindly treating:

1 month == 30 days

because calendar durations are not necessarily fixed durations.

Claim Correspondence

One of the central concepts in the architecture is the separation between:

"Are these claims about the same underlying rule?"

and:

"How did the rule change?"

These are not the same question.

ClaimCorrespondence answers the first.

PolicyChange answers the second.

Claim

A claim is a version-specific assertion.

2014 Claim
"Goods must be removed within 60 days."

and

2026 Claim
"Goods must be removed within 45 days."

are separate claims.

Correspondence

The system can establish:

2014 Claim
     │
     │ MODIFIED
     ▼
2026 Claim

The correspondence contains:

relationship_type
confidence
method
status

This relationship establishes semantic continuity across versions.

Why PolicyChange Is Separate

A policy change should not be inferred merely from similar text.

Conceptually:

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

This separation makes the system easier to audit.

A correspondence can exist without necessarily representing a substantive policy change.

Deterministic Change Detection

Once correspondence exists, ChangeDetector classifies the relationship.

Current change categories include:

ADDED
REMOVED
MODIFIED
SAME

For a modification, the system can also retain structured change descriptions.

Example:

60 days → 45 days

becomes:

MODIFIED

deadline:
    60 days → 45 days

This is significantly more useful than:

"The regulation changed."
Real Regulatory Demonstration

The current test suite contains a real regulatory change based on:

Proclamation No. 1425/2026 — Customs Proclamation (Further Amendment) Proclamation

The system processes the actual PDF through the ingestion pipeline.

The demonstration focuses on Article 51(1).

The earlier provision required relevant sea/land imported goods to be removed within:

60 days

The 2026 amendment changes this to:

45 days

The system represents this as:

2014 Claim
    │
    │ MODIFIED
    │
    ▼
2026 Claim

deadline:
    60 days → 45 days

The resulting PolicyChange retains the relationship between the old and new claims and their underlying evidence.

This is a complete vertical slice through:

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

That vertical slice is currently covered by an integration test.

Human-in-the-Loop Intelligence

The system is designed around uncertainty rather than pretending every AI output is correct.

The intended workflow is:

AI Proposal
     ↓
Deterministic Validation
     ↓
Confidence / Ambiguity
     ↓
 ┌───────────────┐
 │               │
High confidence  Uncertain
 │               │
 ↓               ↓
Accept       Human Review
                 │
                 ↓
             Confirmed

Potential review categories include:

CLAIM_EXTRACTION
ENTITY_RESOLUTION
CLAIM_CORRESPONDENCE
APPLICABILITY

The important principle is:

Uncertainty should become a reviewable state, not an invisible hallucination.

Role of the LLM

LLMs are useful in this system, but they should not become the database of truth.

They are well suited for:

Claim extraction

Converting regulatory prose into candidate structured claims.

Entity extraction

Identifying organizations, products, industries, activities, and other entities.

Candidate correspondence

Identifying claims that may describe the same underlying rule across versions.

Explanation

Generating human-readable summaries from already validated structured changes.

They should not independently decide:

"This is definitely the law."

The evidence model remains authoritative.

Automated Ingestion

The planned ingestion architecture is:

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
DocumentVersion
       ↓
Structure Parser
       ↓
Evidence
       ↓
Claim Extraction

The system can eventually monitor sources periodically for new publications.

A generic connector boundary allows additional institutions to be added without rewriting the regulatory knowledge model.

Potential future connectors include:

Customs
Ministry of Trade
National Bank of Ethiopia
EFDA
Ethiopian Coffee and Tea Authority
other regulatory institutions
Business Profiles

Regulatory information becomes useful when the system understands the business to which it applies.

The intended model is deliberately generic.

Instead of:

if business == coffee_exporter:

the system represents business characteristics as relationships to canonical entities.

For example:

Coffee Exporter

BUSINESS_TYPE → EXPORTER
INDUSTRY     → COFFEE
PRODUCT      → COFFEE
DIRECTION    → EXPORT
TRANSPORT    → SEA

This allows the same regulatory platform to support:

Coffee exporter
Garment importer
Pharmaceutical distributor
Electronics importer
Manufacturing company

without hard-coding each business type into application logic.

Applicability

The intended evaluation model is:

PolicyChange
      +
BusinessProfile
      ↓
ApplicabilityService
      ↓
┌───────────────┬────────────────┬───────────┐
│   AFFECTED    │ NOT_AFFECTED   │  UNKNOWN  │
└───────────────┴────────────────┴───────────┘

A critical rule is:

Missing information should produce UNKNOWN, not NOT_AFFECTED.

This prevents the system from confidently telling a business that a regulation does not apply simply because its profile is incomplete.

Why This Is Not Just RAG

Traditional RAG generally follows:

Question
   ↓
Retrieve chunks
   ↓
LLM
   ↓
Answer

Trusted Information Intelligence instead aims for:

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

Retrieval can still be used as a supporting mechanism.

It is not the underlying knowledge model.

This distinction matters because regulatory intelligence requires versioning, provenance, semantic comparison, and uncertainty handling, not merely finding text that resembles a question.

Technology Stack
Backend
Python
FastAPI
SQLAlchemy
PostgreSQL
Alembic
Pydantic Settings
Document Processing
pypdf
Testing
pytest
HTTPX
Development
Ruff
Docker/Podman Compose
PostgreSQL
Repository Structure
trusted-information-intelligence/
│
├── alembic/
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
│   │   └── policy_change_correspondence.py
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
│   │   └── policy_change.py
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
Running Locally
Requirements
Python 3.12+
PostgreSQL
Docker or Podman
Git
Install
git clone https://github.com/yisakabraham10-dev/trusted-information-intelligence.git

cd trusted-information-intelligence

python -m venv .venv

source .venv/bin/activate

pip install -e ".[dev]"
Environment

Copy the example environment:

cp .env.example .env

Configure the PostgreSQL connection as required.

Start PostgreSQL

Using Compose:

podman-compose up -d

or:

docker compose up -d
Run migrations
alembic upgrade head
Start the API
uvicorn src.main:app --reload

The API currently exposes:

GET /health
GET /health/db
Testing

Run the full suite:

pytest -q

The current implementation is covered by a growing test suite spanning:

document ingestion
regulatory structure parsing
document persistence
evidence-backed claim creation
entity resolution
claim/entity relationships
primitive comparisons
requirement comparisons
claim correspondence
change detection
policy-change persistence
real Customs regulatory-change integration

The goal is not merely high test coverage.

The goal is to protect domain invariants.

Examples:

A claim requires evidence.

An entity is canonical within its type/name identity.

A correspondence connects specific claims.

A policy change references the claims that establish the change.

An uncertain comparison should not silently become a confirmed fact.
Development Philosophy

This project follows several principles.

1. Evidence before explanation

The system should know where a statement came from before it explains that statement.

2. Version before comparison

Never compare regulatory text without knowing which versions the claims came from.

3. Structure before semantics

Where possible, compare structured fields rather than relying solely on string similarity.

4. Deterministic logic before probabilistic inference

Use deterministic rules for things that can be determined reliably.

Use AI for things that genuinely require interpretation.

5. Uncertainty is a first-class state

If the system does not know, it should say so.

6. Human review resolves ambiguity

Humans should resolve important uncertain cases rather than allowing the model to silently guess.

7. Preserve the original evidence

Generated representations should never replace the underlying regulatory document.

What Is Currently Implemented
Implemented
 FastAPI application
 PostgreSQL persistence
 Alembic migrations
 Source model
 Document model
 Document versioning
 PDF ingestion
 Regulatory section parsing
 Evidence persistence
 Evidence-backed claims
 Entity model
 Deterministic entity resolution
 Claim/entity relationships
 Entity uniqueness constraint
 Structured requirement semantics
 Primitive comparison
 Requirement comparison
 Claim correspondence
 Deterministic change detection
 Policy change persistence
 Real Customs Proclamation integration test
 60-day → 45-day change detection
Next
Automated intelligence
 LLM-assisted claim extraction
 Entity extraction
 Candidate entity resolution
 Candidate claim correspondence
 Confidence scoring
 Review queue
Source monitoring
 Official-source crawlers
 Document discovery
 Automated version detection
 Scheduled ingestion
Business intelligence
 Business profiles
 Business/entity relationships
 Applicability evaluation
 Action generation
 Regulatory alerts
Interface
 Regulatory change dashboard
 Evidence viewer
 Claim comparison UI
 Business profile UI
 Human review interface
Longer-Term Direction

The eventual system can evolve toward:

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

The database remains relational.

Graph-like relationships are represented explicitly through relational models rather than requiring a separate graph database for the initial system.

What This Project Is Not

Trusted Information Intelligence is not intended to be:

A generic chatbot

The goal is not simply to put a chat interface over a language model.

A document dump

Documents are inputs to a structured knowledge system.

A naive RAG application

Retrieval is not treated as the fundamental representation of regulatory knowledge.

An AI legal authority

The system does not replace legal professionals or government authorities.

A system that hides uncertainty

Uncertainty should be visible and reviewable.

A system that invents regulatory conclusions

Important claims must remain connected to evidence.

Current Status

Status: Active development

The foundational evidence and change-detection pipeline is implemented.

The current system can already demonstrate a complete regulatory-change workflow using a real Ethiopian customs proclamation:

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

The next major stage is moving from a manually constructed demonstration toward an automated intelligence pipeline:

Official Source
      ↓
Crawler
      ↓
Document Version
      ↓
LLM Proposal
      ↓
Deterministic Validation
      ↓
Human Review
      ↓
Confirmed Claim
      ↓
Correspondence
      ↓
Policy Change
      ↓
Business Applicability
Design Principle

Ultimately, Trusted Information Intelligence is built around one idea:

A useful answer is not merely an answer that sounds correct. It is an answer whose reasoning can be traced back to evidence, whose temporal context is known, whose changes can be explained, and whose uncertainty is explicit.