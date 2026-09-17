# Trusted Information Intelligence

> **What changed. Why it changed. Who it affects. What to do. And where the evidence comes from.**

Trusted Information Intelligence is an evidence-centered information intelligence platform designed to make fragmented public information — initially Ethiopian business and regulatory information — understandable, actionable, traceable, and verifiable.

The system is being built for the **OSF × Andela "Information You Can Trust" hackathon**.

The initial product focuses on Ethiopian import/export businesses, with the first demonstration centered around an Ethiopian clothing importer.

---

# 1. Problem

Government information already exists, but it is often fragmented across:

* proclamations
* regulations
* government websites
* institutional announcements
* PDFs
* portals
* official notices
* public communications

The problem is not simply "there is no information."

The problem is that a business owner may have difficulty answering:

> **What changed?**
>
> **When did it change?**
>
> **Why did it change?**
>
> **Does it affect my business?**
>
> **What do I need to do?**
>
> **What official evidence proves this?**

Social media, Telegram channels, news articles, and other public signals may help discover that something happened, but they are not automatically treated as authoritative evidence.

The platform therefore prioritizes **primary authoritative sources**.

---

# 2. Core Product Idea

The central user journey is:

```text
Ethiopian clothing importer
        ↓
Something changed
        ↓
What exactly changed?
        ↓
Why did it change?
        ↓
Does it affect me?
        ↓
What should I do?
        ↓
Show me the official evidence
```

Example business profile:

```json
{
  "business_type": "IMPORTER",
  "location": "Addis Ababa",
  "products": ["clothing"],
  "origin": ["China"]
}
```

The system should eventually be able to answer questions for this business profile using structured evidence rather than relying on an LLM to invent an answer.

---

# 3. Product Principles

## Evidence first

Every important factual answer should be traceable to evidence.

The system should prefer:

> "There is insufficient evidence"

over:

> an unsupported or hallucinated answer.

## Database as source of truth

The database stores structured knowledge and evidence.

The LLM is a reasoning and synthesis layer.

The architecture is **not**:

```text
PDF → LLM → Answer
```

Instead:

```text
SOURCE
  ↓
DOCUMENT
  ↓
DOCUMENT VERSION
  ↓
DOCUMENT STRUCTURE
  ↓
CLAIMS
  ↓
EVIDENCE
  ↓
RETRIEVAL
  ↓
REASONING
  ↓
ANSWER + CITATIONS
```

## No destructive overwriting

When a regulation changes, old information should remain available.

The system should model historical versions and changes rather than simply replacing old records.

## Contradictions should coexist

If two sources make contradictory claims, the system should not silently overwrite one.

It should preserve both claims and represent their relationship.

## Official rationale must be distinguished from interpretation

The system must never invent why a government institution changed something.

Possible rationale classifications:

```text
OFFICIALLY_STATED_RATIONALE
SUPPORTING_OFFICIAL_CONTEXT
AI_INTERPRETATION
UNKNOWN
```

If the government did not explicitly state a reason, the system should say so.

---

# 4. Retrieval Philosophy

This project is **not RAG-first**.

The preferred architecture is:

```text
USER
 ↓
QUERY UNDERSTANDING
 ├── intent
 ├── entities
 ├── time
 └── business context
 ↓
QUERY PLANNER
 ├── SQL
 ├── keyword search
 └── vector search (optional)
 ↓
EVIDENCE RANKING
 ↓
EVIDENCE VALIDATION
 ↓
LLM REASONING
 ↓
ANSWER
 +
EXACT EVIDENCE
```

Structured retrieval should be primary for things such as:

* requirements
* fees
* deadlines
* eligibility
* affected products
* affected businesses
* institutions
* effective dates
* regulatory changes

Semantic/vector retrieval can later help with:

* nuanced explanations
* rationale
* unusual questions
* contextual passages

The LLM should **interpret and explain retrieved evidence**, not determine facts independently.

---

# 5. Trust Model

The system should distinguish different kinds of uncertainty.

## Evidence confidence

`Evidence.confidence`

Represents the quality/confidence of the evidence extraction or source.

It does **not** mean that the claim is true.

## Claim-evidence strength

`ClaimEvidence.strength`

Represents how strongly a specific evidence item establishes a specific claim.

Example:

```text
Claim A
    Evidence 1 → SUPPORTS → 0.95
    Evidence 2 → CONTEXT  → 0.40
```

These concepts must not be conflated.

---

# 6. Trust Statuses

Potential answer/knowledge statuses:

```text
SUPPORTED
PARTIALLY_SUPPORTED
CONFLICTING
OUTDATED
INSUFFICIENT_EVIDENCE
```

The system should make uncertainty visible rather than hide it.

---

# 7. Source Hierarchy

Sources are conceptually organized by authority:

```text
Tier 1 — Primary authoritative
Tier 2 — Official aggregators
Tier 3 — Institutional sources
Tier 4 — Secondary sources
Tier 5 — Public signals
```

Examples of useful Ethiopian official information sources include government legal repositories, ministries, official business portals, institutional portals, and other authoritative government publications.

Public signals such as Telegram/news/social media can be useful for discovery, but should not automatically become authoritative evidence.

---

# 8. Database Architecture

Current conceptual model:

```text
sources
   ↓
documents
   ↓
document_versions
   ↓
sections
   ├── claims
   │     ↓
   │  claim_evidence
   │     ↑
   └── evidence
```

Entities are connected separately:

```text
claims
   ↓
claim_entities
   ↓
entities
```

Future relationships will include:

```text
claims
   ↓
policy_changes
   ↓
actions
```

and:

```text
business_profiles
   ↓
business_profile_entities
   ↓
entities
```

---

# 9. Current Database Models

## `sources`

Represents an information source/institution.

Current fields:

```text
id
name
authority_tier
base_url
institution_type
description
is_active
created_at
```

---

## `documents`

Represents a logical document published by a source.

Current fields:

```text
id
source_id
title
document_type
url
description
created_at
```

A document may have multiple versions.

---

## `document_versions`

Represents a particular version of a document.

Current fields:

```text
id
document_id
version_label
publication_date
effective_date
retrieved_at
storage_path
content_hash
status
supersedes_version_id
notes
```

Important design principle:

```text
Document
   ├── Version 1
   ├── Version 2
   └── Version 3
```

Versions should not overwrite one another.

`supersedes_version_id` allows version history to be represented explicitly.

---

## `sections`

Represents structured portions of a document version.

Current fields:

```text
id
document_version_id
parent_section_id
section_number
title
page_start
page_end
raw_text
created_at
```

This provides document structure and precise locations for claims/evidence.

---

## `claims`

A claim is a discrete, checkable factual assertion extracted from a source.

Important distinction:

> A claim is not automatically true simply because it exists in the database.

A claim represents what a source says.

Current fields:

```text
id
section_id
claim_type
text
normalized_text
effective_from
effective_to
status
created_at
```

Potential claim types include things such as:

```text
REQUIREMENT
FEE
DEADLINE
ELIGIBILITY
PROCEDURE
PENALTY
DEFINITION
POLICY
RATIONALE
```

The exact taxonomy can evolve as implementation progresses.

---

# 10. Evidence Model

Evidence is intentionally separate from claims.

Current structure:

```text
evidence
──────────────
id
section_id
page
quote
confidence
created_at
```

An evidence record identifies a specific passage/location in a document.

### Important design decision

`Evidence` does **not** contain `claim_id`.

This is intentional.

One evidence passage may support multiple claims:

```text
Evidence #7
    ↓
Claim #1
Claim #2
Claim #3
```

Likewise, one claim may require multiple pieces of evidence:

```text
Claim #1
    ↓
Evidence #7
Evidence #9
Evidence #12
```

Therefore Claim ↔ Evidence is many-to-many.

---

# 11. ClaimEvidence Model

`claim_evidence` represents the relationship between a claim and evidence.

Current structure:

```text
claim_id
evidence_id
relation_type
strength
```

The primary key is:

```text
(claim_id, evidence_id)
```

This prevents duplicate relationships.

`relation_type` can represent:

```text
SUPPORTS
CONTRADICTS
CONTEXT
```

`strength` represents the strength of the relationship between that evidence and that claim.

It is **not** a probability that the claim is true.

---

# 12. Entity Model

`entities` represents important real-world concepts.

Current structure:

```text
id
entity_type
name
description
created_at
```

Examples:

```text
PRODUCT
    Clothing

COUNTRY
    China

INSTITUTION
    Ministry of Trade

BUSINESS_TYPE
    Importer

REQUIREMENT
    Import License
```

The initial implementation intentionally uses one generic entity table rather than immediately creating separate tables for products, countries, institutions, etc.

This keeps the knowledge model flexible.

---

# 13. ClaimEntity Model

`claim_entities` connects claims to entities.

Current structure:

```text
claim_id
entity_id
relation_type
```

Composite primary key:

```text
(claim_id, entity_id)
```

Example:

```text
Claim:
"Importers of clothing from China must satisfy X."

        ↓

claim_entities

        ├── AFFECTS → Clothing
        ├── APPLIES_TO → Importer
        └── ORIGIN → China
```

This allows structured queries such as:

```text
Show changes affecting clothing importers from China.
```

without requiring the LLM to perform all entity reasoning from raw text.

---

# 14. Planned Database Models

These have not yet been fully implemented.

## `policy_changes`

Represents changes between old and new claims.

Conceptually:

```text
old_claim
    ↓
policy_change
    ↓
new_claim
```

Potential change types:

```text
ADDED
REMOVED
MODIFIED
```

The change record should eventually answer:

```text
What changed?
When?
What was the old requirement?
What is the new requirement?
When does it become effective?
Why did it change?
```

The rationale should reference a claim/evidence record when possible.

---

## `actions`

Represents what a user/business should do in response to a change.

Conceptually:

```text
policy_change
      ↓
    actions
```

Actions must distinguish:

```text
OFFICIAL_REQUIREMENT
RECOMMENDED_ACTION
AI_INTERPRETATION
```

The system should not present an AI recommendation as though it were a government requirement.

---

## `business_profiles`

Represents the context of the user/business.

Example:

```json
{
  "business_type": "IMPORTER",
  "location": "Addis Ababa",
  "products": ["clothing"],
  "origin": ["China"]
}
```

This enables personalized impact analysis.

---

## `business_profile_entities`

Connects business profiles to entities.

Example:

```text
Business Profile
      ↓
business_profile_entities
      ↓
PRODUCT → Clothing
COUNTRY → China
BUSINESS_TYPE → Importer
```

---

# 15. Planned End-to-End Pipeline

Eventually the system should support:

```text
OFFICIAL SOURCE
      ↓
DOCUMENT DISCOVERY
      ↓
DOCUMENT DOWNLOAD
      ↓
DOCUMENT VERSION
      ↓
PDF/TEXT EXTRACTION
      ↓
DOCUMENT STRUCTURING
      ↓
CLAIM EXTRACTION
      ↓
ENTITY EXTRACTION
      ↓
EVIDENCE CREATION
      ↓
CLAIM ↔ EVIDENCE
      ↓
CLAIM ↔ ENTITY
      ↓
OLD vs NEW COMPARISON
      ↓
POLICY CHANGE
      ↓
BUSINESS IMPACT
      ↓
ACTION
      ↓
API
      ↓
USER INTERFACE
```

---

# 16. Planned Ingestion System

The ingestion system should eventually:

1. Discover official documents.
2. Download the original document.
3. Store the original file outside PostgreSQL.
4. Calculate a content hash.
5. Create a document/version record.
6. Extract text.
7. Preserve page information.
8. Identify sections.
9. Extract atomic claims.
10. Extract entities.
11. Create evidence records.
12. Connect claims to evidence.
13. Detect whether the document is a new version.
14. Compare versions.

Original documents should not be stored as large binary blobs directly inside the relational database.

Instead, the database stores metadata such as:

```text
storage_path
content_hash
```

while the original PDF is kept in file/object storage.

---

# 17. Planned Change Detection

The system should compare claims rather than simply comparing entire PDFs.

Conceptually:

```text
OLD DOCUMENT
    ↓
OLD CLAIMS
    ↓
        COMPARE
    ↑
NEW CLAIMS
    ↑
NEW DOCUMENT
```

Possible results:

```text
ADDED
REMOVED
MODIFIED
UNCHANGED
```

Example:

```text
Old:
Importers must submit X within 30 days.

New:
Importers must submit X within 15 days.
```

This should become:

```text
MODIFIED

Old requirement:
30 days

New requirement:
15 days
```

rather than simply returning a generic PDF diff.

---

# 18. Planned Contradiction Detection

Contradictions should be represented explicitly.

For example:

```text
Claim A
"Requirement X applies to product Y."

Claim B
"Requirement X does not apply to product Y."
```

The system should preserve both and identify their relationship.

However, apparent contradictions may actually be explained by:

* different effective dates
* different jurisdictions
* different product categories
* exceptions
* newer versions
* different institutions
* different scopes

Therefore contradiction detection must consider context and time.

---

# 19. Planned Query Engine

The query engine should eventually understand:

```text
"What changed?"

"Does this affect clothing importers?"

"What do I need to do?"

"When does the new rule become effective?"

"Why was this changed?"

"Show me the official source."

"Is this information still current?"
```

Query understanding should extract:

```text
intent
entities
time
business context
```

Then the query planner chooses appropriate retrieval mechanisms.

---

# 20. Planned API

FastAPI is the backend framework.

The current application starts successfully and has:

```text
GET /health
```

which currently returns:

```json
{
  "status": "ok"
}
```

Future API areas are expected to include:

```text
/sources
/documents
/document-versions
/claims
/evidence
/entities
/changes
/actions
/business-profiles
/query
```

The exact API design should be developed after the underlying domain models are stable.

---

# 21. Technology Stack

Current stack:

```text
Python
FastAPI
PostgreSQL 17
SQLAlchemy
Alembic
psycopg
Pydantic Settings
Podman
podman-compose
pytest
httpx
ruff
```

Potential future technologies:

```text
PDF/document extraction
Object/file storage
Vector search / pgvector
LLM provider
Frontend
```

Do not add infrastructure merely because it is fashionable.

Each dependency should solve a concrete problem.

---

# 22. Repository Structure

Current/recommended structure:

```text
trusted-information/
│
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── source.py
│   │   ├── document.py
│   │   ├── document_version.py
│   │   ├── section.py
│   │   ├── claim.py
│   │   ├── evidence.py
│   │   ├── claim_evidence.py
│   │   ├── entity.py
│   │   └── claim_entity.py
│   │
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── ai/
│   └── db/
│       ├── base.py
│       ├── session.py
│       └── test_connection.py
│
├── documents/
│
├── scripts/
│
├── tests/
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── .env
├── .env.example
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

Directory-specific READMEs can later be added to:

```text
docs/
src/models/
src/services/
src/ai/
scripts/
tests/
```

if the project becomes large enough to justify them.

---

# 23. Environment

The application currently uses:

```text
DATABASE_URL
```

from `.env`.

The development PostgreSQL instance is currently exposed locally on:

```text
localhost:5433
```

with PostgreSQL running inside Podman.

`.env` is ignored by Git.

`.env.example` should contain placeholders rather than credentials.

---

# 24. Alembic Migration History

Current migration progression:

```text
Source
    ↓
bd280b5b5806
    create claims table
    ↓
1ed77c1264d9
    create evidence table
    ↓
c00f18d3f59d
    create claim evidence table
    ↓
3b436163edfa
    create entities table
    ↓
claim_entities migration
    next migration
```

At the last confirmed database checkpoint:

```text
3b436163edfa (head)
```

The `ClaimEntity` model and its migration are currently being added.

**Before continuing development, confirm the current Alembic head with:**

```bash
alembic current
```

---

# 25. Development Workflow

Every database feature should follow:

```text
BUILD
  ↓
TEST
  ↓
GENERATE MIGRATION
  ↓
INSPECT MIGRATION
  ↓
UPGRADE DATABASE
  ↓
VERIFY
  ↓
GIT DIFF
  ↓
COMMIT
  ↓
NEXT FEATURE
```

Do not blindly run autogenerated migrations.

Always inspect them.

---

# 26. Git Workflow

Git is part of the development process.

After completing each meaningful model/database feature:

```bash
git status
git diff
```

Then commit the feature.

Examples of the existing style:

```bash
git commit -m "create evidence model"
git commit -m "create claim evidence relationship"
git commit -m "create entity model"
```

Keep commits small enough that the development history explains how the system was built.

---

# 27. Current Implementation Status

## Completed

```text
[x] Repository initialized
[x] README / project concept
[x] Python project configuration
[x] Virtual environment
[x] FastAPI application
[x] /health endpoint
[x] PostgreSQL development database
[x] Podman setup
[x] SQLAlchemy configuration
[x] Database connection
[x] Alembic configuration
[x] Source model
[x] Document model
[x] DocumentVersion model
[x] Section model
[x] Claim model
[x] Evidence model
[x] ClaimEvidence model
[x] Entity model
[x] ClaimEntity model
```

## Completed migrations

```text
[x] sources
[x] documents
[x] document_versions
[x] sections
[x] claims
[x] evidence
[x] claim_evidence
[x] entities
```

## In progress / verify

```text
[ ] claim_entities migration status
```

Before proceeding, verify:

```bash
alembic current
```

---

# 28. Remaining MVP Work

The database foundation is only the beginning.

Major remaining components:

```text
[ ] Finish entity relationships
[ ] PolicyChange model
[ ] Action model
[ ] BusinessProfile model
[ ] BusinessProfileEntity model

[ ] Source ingestion
[ ] PDF/document extraction
[ ] Document storage
[ ] Section extraction
[ ] Claim extraction
[ ] Evidence extraction
[ ] Entity extraction

[ ] Version comparison
[ ] Policy change detection
[ ] Contradiction detection
[ ] Freshness/outdated detection

[ ] Retrieval/query engine
[ ] Evidence ranking
[ ] Evidence validation
[ ] LLM reasoning layer

[ ] FastAPI domain routes
[ ] Query endpoint
[ ] Business-impact endpoint

[ ] Seed real Ethiopian regulatory data
[ ] Build frontend/demo
[ ] Prepare demonstration scenario
[ ] README finalization
[ ] Pitch deck
[ ] Demo video
```

---

# 29. MVP Strategy

Do **not** attempt to ingest every Ethiopian regulation.

The hackathon MVP should demonstrate one compelling vertical.

Recommended demonstration:

```text
Ethiopian clothing importer
        ↓
Official regulatory documents
        ↓
A real change
        ↓
Structured claims
        ↓
Evidence
        ↓
Policy change
        ↓
Business impact
        ↓
Action
        ↓
Source citation
```

The system should be convincing end-to-end before it becomes broad.

---

# 30. Things We Are Deliberately NOT Building

## Not a generic chatbot

The product is not:

> "Ask our AI anything."

## Not a generic PDF chatbot

The architecture should not depend on feeding entire PDFs into an LLM.

## Not pure RAG

Retrieval is a component, not the product architecture.

## Not a replacement for government

The system organizes and explains public information.

It does not become the authoritative source itself.

## Not an automatic truth machine

The system must preserve uncertainty and conflicting evidence.

## Not a hallucinated legal adviser

The system must clearly distinguish:

```text
Official requirement
AI interpretation
Recommended action
Unknown
```

---

# 31. Critical Design Decisions Already Made

These decisions should not be casually changed by a future development session.

### Claim and Evidence are separate

```text
Claim ≠ Evidence
```

### Evidence does not contain `claim_id`

Because Claim ↔ Evidence is many-to-many.

### `ClaimEvidence` stores the relationship

```text
claim_id
evidence_id
relation_type
strength
```

### Evidence confidence ≠ claim truth

`Evidence.confidence` concerns evidence quality/extraction.

`ClaimEvidence.strength` concerns the claim-evidence relationship.

### Historical versions are preserved

Do not overwrite regulatory information when a new version arrives.

### Contradictions are preserved

Do not silently merge contradictory claims.

### Official rationale must be evidence-backed

Never fabricate why a government changed a rule.

### PostgreSQL is the source of truth

The LLM should operate over retrieved structured evidence.

---

# 32. Immediate Next Development Step

The next development session should first verify:

```bash
alembic current
git status
```

Then verify the `claim_entities` migration.

After that, continue with:

```text
PolicyChange
    ↓
Action
    ↓
BusinessProfile
    ↓
BusinessProfileEntity
```

Only after the domain model is sufficiently stable should significant ingestion/AI work begin.

---

# 33. Handoff Instructions for the Next ChatGPT Session

**IMPORTANT: This section exists specifically so development can continue in a new ChatGPT conversation.**

The next assistant should treat this README as the project's current development specification.

Do not redesign the architecture from scratch.

Do not restart completed work.

Do not replace the evidence-centered architecture with a generic RAG chatbot.

Continue from the current repository state.

First:

```bash
alembic current
git status
```

Then inspect the current repository if necessary.

The development process is:

```text
one feature
→ implement
→ inspect
→ migrate
→ verify
→ commit
→ next feature
```

The immediate domain-model sequence is:

```text
Claim
Evidence
ClaimEvidence
Entity
ClaimEntity
PolicyChange
Action
BusinessProfile
BusinessProfileEntity
```

The major architectural principle is:

> **Database is the source of truth; the LLM is the retrieval/reasoning/synthesis layer.**

The core product question is:

> **What changed, why did it change, who does it affect, what should they do, and where is the evidence?**

The first target user is:

> **An Ethiopian clothing importer.**

The first successful MVP should demonstrate:

```text
real official source
      ↓
real document
      ↓
structured claims
      ↓
evidence
      ↓
detected change
      ↓
business impact
      ↓
action
      ↓
exact source evidence
```

Do not optimize for breadth before this end-to-end path works.

---

# 34. Hackathon Context

Hackathon:

**OSF × Andela — Information You Can Trust**

Challenge theme:

> Use AI software development tools to build people-centric technology that makes reliable information about civic life and opportunity visible, accessible, and actionable.

Submission deadline:

**September 21, 2026 at 23:59 UTC**

The product should emphasize:

* trustworthy information
* evidence
* accessibility
* actionability
* transparency
* AI-assisted development
* a convincing demonstration

The final submission is expected to include:

```text
Public GitHub repository
README
Demo video
Pitch deck PDF
Written project summary
```

---

# 35. Final Mental Model

The entire system can be understood as:

```text
                    OFFICIAL INFORMATION
                            │
                            ↓
                         SOURCES
                            │
                            ↓
                        DOCUMENTS
                            │
                            ↓
                     DOCUMENT VERSIONS
                            │
                            ↓
                         SECTIONS
                            │
              ┌─────────────┴─────────────┐
              ↓                           ↓
           CLAIMS                      EVIDENCE
              │                           │
              └───────────┬───────────────┘
                          ↓
                   CLAIM ↔ EVIDENCE
                          │
                          ↓
                       ENTITIES
                          │
                          ↓
                  CLAIM ↔ ENTITY
                          │
                          ↓
                  POLICY CHANGES
                          │
                          ↓
                       ACTIONS
                          │
                          ↓
                 BUSINESS PROFILE
                          │
                          ↓
                  BUSINESS IMPACT
                          │
                          ↓
                    QUERY ENGINE
                          │
                          ↓
                         LLM
                          │
                          ↓
              ANSWER + EVIDENCE + CONTEXT
```

The fundamental goal is not merely to generate answers.

It is to create a **traceable chain from public information → structured fact → evidence → change → impact → action**.
