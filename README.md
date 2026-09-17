# Trusted Information Intelligence

> **What changed. Why did it change. Who does it affect. What should they do. And where is the evidence?**

Trusted Information Intelligence is an evidence-centered information platform designed to transform fragmented public information into **context-aware, actionable, and verifiable information**.

The initial focus is Ethiopian businesses, particularly importers and exporters who need to understand changes in laws, regulations, requirements, procedures, deadlines, and government decisions.

The system is designed around one principle:

> **The database is the source of truth. AI explains and reasons over evidence; it does not manufacture facts.**

---

## Problem

Important information affecting businesses and citizens is often distributed across:

* Government websites
* Proclamations and regulations
* Directives
* Official announcements
* Institutional documents
* PDFs
* Public notices
* Official portals

The information may exist, but finding out **what changed, whether it applies to you, what you need to do, and which official document proves it** can still be difficult.

Social media and messaging platforms may make information easier to discover, but they are signals rather than authoritative sources.

Trusted Information Intelligence aims to bridge that gap.

Instead of simply answering:

> "What does this document say?"

the system should answer:

> "This changed, it affects your business because of X, here is what you should do, and here is the exact evidence supporting that conclusion."

---

# Core Questions

Every important piece of information should help answer:

1. **What changed?**
2. **When did it change?**
3. **Why did it change?**
4. **Who is affected?**
5. **What should they do?**
6. **What official evidence supports this?**

When the available evidence does not answer one of these questions, the system should explicitly say so rather than invent an answer.

---

# Product Vision

The intended user experience is:

```text
Business Profile
      ↓
Relevant Information
      ↓
What Changed?
      ↓
Does It Affect Me?
      ↓
Why Did It Change?
      ↓
What Should I Do?
      ↓
Official Evidence
```

For example:

```text
Ethiopian clothing importer
        ↓
New import requirement detected
        ↓
Product = Clothing
Origin = China
Business type = Importer
        ↓
Requirement applies
        ↓
Explain the change
        ↓
Provide required action
        ↓
Show exact official source and evidence
```

---

# Trust Model

The platform distinguishes between **facts, evidence, and interpretation**.

It should never silently turn an inference into an official fact.

## Evidence Levels

| Level                         | Meaning                                         |
| ----------------------------- | ----------------------------------------------- |
| `OFFICIALLY_STATED_RATIONALE` | The official source explicitly gives the reason |
| `SUPPORTING_OFFICIAL_CONTEXT` | Other official information provides context     |
| `AI_INTERPRETATION`           | The system is interpreting available evidence   |
| `UNKNOWN`                     | There is insufficient evidence                  |

## Trust Status

| Status                  | Meaning                                             |
| ----------------------- | --------------------------------------------------- |
| `SUPPORTED`             | Evidence adequately supports the claim              |
| `PARTIALLY_SUPPORTED`   | Evidence supports only part of the claim            |
| `CONFLICTING`           | Relevant sources disagree                           |
| `OUTDATED`              | The information has been superseded                 |
| `INSUFFICIENT_EVIDENCE` | There is not enough evidence to establish the claim |

The system should prefer:

> **"There is insufficient evidence."**

over an unsupported answer.

---

# Architecture

The core architecture is:

```text
ORIGINAL SOURCE
      ↓
DOCUMENT
      ↓
DOCUMENT VERSION
      ↓
DOCUMENT STRUCTURE
      ↓
CLAIMS + EVIDENCE
      ↓
ENTITIES + RELATIONSHIPS
      ↓
POLICY CHANGES
      ↓
ACTIONS
      ↓
RETRIEVAL / QUERY ENGINE
      ↓
LLM REASONING
      ↓
ANSWER + EVIDENCE
```

The system is intentionally **not designed as a PDF → LLM → answer pipeline**.

Instead:

```text
Source
  ↓
Structured Knowledge
  ↓
Evidence Retrieval
  ↓
Validation
  ↓
Reasoning
  ↓
Answer
```

---

# Current Database Model

The current database foundation consists of:

```text
sources
   ↓
documents
   ↓
document_versions
   ↓
sections
   ↓
claims
   ↕
claim_evidence
   ↕
evidence

claims
   ↕
claim_entities
   ↕
entities
```

## Sources

Represents an information source or institution.

Examples:

* Government ministry
* Government agency
* Official legal repository
* Official business portal

Important properties include:

* Authority tier
* Institution type
* Base URL
* Description
* Active status

---

## Documents

Represents an individual document or information resource belonging to a source.

Examples:

* Proclamation
* Regulation
* Directive
* Official announcement
* Government guidance document

A document can have multiple versions.

---

## Document Versions

A document should not simply be overwritten when it changes.

Each version stores information such as:

* Publication date
* Effective date
* Version label
* Retrieval time
* Storage path
* Content hash
* Current/outdated status
* Previous version

This allows the system to preserve historical information.

Conceptually:

```text
Document
   │
   ├── Version 1
   │
   ├── Version 2
   │
   └── Version 3
```

---

## Sections

Documents are broken into structured sections.

A section can contain:

* Section number
* Title
* Parent section
* Page range
* Raw text

This provides precise locations for claims and evidence.

---

## Claims

A claim is a **discrete, checkable assertion** extracted from a source.

A claim does not automatically mean that the system believes the statement is true.

It represents what a source says.

Examples:

```text
"Importers must submit X."

"The requirement becomes effective on Y."

"The authority responsible for this process is Z."
```

Claims can have:

* Claim type
* Text
* Normalized text
* Effective dates
* Status
* Source section

---

## Evidence

Evidence represents a specific piece of source material that can support, contradict, or provide context for a claim.

Evidence contains:

* Source section
* Page
* Exact quote
* Evidence quality/confidence

Evidence intentionally does **not** contain a `claim_id`.

This allows one piece of evidence to support multiple claims.

---

## Claim ↔ Evidence

`claim_evidence` represents the relationship between claims and evidence.

```text
Claim
  │
  ├── SUPPORTS → Evidence
  ├── CONTRADICTS → Evidence
  └── CONTEXT → Evidence
```

The relationship also contains a strength value describing how strongly that evidence establishes the claim.

This is a many-to-many relationship:

```text
Claim A ───── Evidence 1
Claim B ───── Evidence 1
Claim B ───── Evidence 2
Claim C ───── Evidence 2
```

This structure allows the platform to represent real-world evidence relationships without duplicating source material.

---

## Entities

Entities represent important real-world objects mentioned by claims.

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

Rather than immediately creating separate tables for every entity category, the current design uses a generalized entity model.

---

## Claim ↔ Entity

`claim_entities` connects claims to entities.

For example:

```text
Claim:
"Importers of clothing from China must satisfy requirement X."

        │
        ├── AFFECTS → Clothing
        ├── APPLIES_TO → Importer
        └── ORIGIN → China
```

This relationship allows structured queries such as:

> Find claims affecting clothing importers from China.

---

# Planned Data Model

The database will eventually expand to include:

```text
sources
documents
document_versions
sections

claims
evidence
claim_evidence

entities
claim_entities

policy_changes
actions

business_profiles
business_profile_entities
```

Additional specialized structures may be introduced when the product requirements justify them.

---

# Policy Changes

A major purpose of the system is identifying **what changed**.

Instead of simply storing the newest document, the system will compare versions.

Conceptually:

```text
OLD VERSION
     ↓
OLD CLAIMS
     ↓
COMPARISON
     ↓
NEW CLAIMS
     ↓
NEW VERSION
```

A policy change may represent:

* Added requirement
* Removed requirement
* Modified requirement
* Changed fee
* Changed deadline
* Changed eligibility
* Changed responsible institution
* Changed procedure
* Changed penalty
* Changed effective date

The system should preserve both the old and new claims rather than overwriting history.

---

# Why Did It Change?

The platform will distinguish between:

### Official rationale

The government explicitly states why a change was made.

### Supporting official context

Other official material helps explain the context.

### AI interpretation

The system infers a possible explanation from available evidence.

### Unknown

There is insufficient evidence to establish the reason.

The system must never present an AI-generated explanation as an official government reason.

---

# Actions

Policy information is only useful if it can become actionable.

The planned `actions` model will connect a policy change to concrete steps.

For example:

```text
Policy Change
     ↓
Action 1: Obtain document X
Action 2: Submit application Y
Action 3: Complete procedure Z
     ↓
Deadline
```

Actions should distinguish between:

* Officially required actions
* Recommended actions
* AI-generated interpretations or recommendations

---

# Business Profiles

The platform will eventually allow information to be evaluated against a business profile.

Example:

```json
{
  "business_type": "IMPORTER",
  "location": "Addis Ababa",
  "products": ["clothing"],
  "origin": ["China"]
}
```

The profile can then be connected to relevant entities.

Instead of asking:

> "What changed?"

the user can ask:

> "What changed that affects my business?"

---

# Retrieval Architecture

The system is designed around **Evidence-Centered Knowledge Retrieval** rather than RAG-first architecture.

The planned query pipeline is:

```text
USER QUESTION
     ↓
QUERY UNDERSTANDING
     ├── Intent
     ├── Entities
     ├── Time
     └── User Context
     ↓
QUERY PLANNER
     ├── SQL
     ├── Keyword Search
     └── Vector Search
     ↓
EVIDENCE RANKING
     ↓
EVIDENCE VALIDATION
     ↓
LLM REASONING
     ↓
ANSWER + EVIDENCE
```

Structured retrieval should be preferred for things such as:

* Requirements
* Fees
* Deadlines
* Eligibility
* Institutions
* Effective dates
* Products
* Affected business types
* Policy changes

Semantic/vector retrieval can support more nuanced questions where exact structured fields are insufficient.

---

# Role of AI

AI is a reasoning and interpretation layer.

It should help with:

* Document extraction
* Claim extraction
* Entity extraction
* Change detection
* Contradiction detection
* Query understanding
* Evidence ranking
* Natural-language explanations
* Action summarization

AI should **not** be treated as the database of truth.

The intended flow is:

```text
Evidence
   ↓
Validation
   ↓
AI reasoning
   ↓
Explanation
```

not:

```text
AI
 ↓
Make up answer
 ↓
Find citation afterward
```

---

# Source Hierarchy

The platform prioritizes sources according to authority.

```text
Tier 1 — Primary authoritative sources
Tier 2 — Official aggregators
Tier 3 — Institutional sources
Tier 4 — Secondary sources
Tier 5 — Public signals
```

Official government documents should be preferred whenever available.

Social media, Telegram channels, news reports, and other public signals can help identify information that should be investigated, but they should not automatically become authoritative evidence.

---

# Planned MVP

The first usable MVP will focus on a narrow vertical rather than attempting to model every Ethiopian regulation.

### Initial target

**Ethiopian import/export businesses**

with an initial demonstration around:

**Clothing importers**

The MVP should demonstrate:

```text
Business Profile
      ↓
Relevant Regulation
      ↓
Detected Change
      ↓
Affected Business
      ↓
Explanation
      ↓
Action
      ↓
Official Evidence
```

---

# Development Roadmap

## Phase 1 — Knowledge Foundation

* [x] Project structure
* [x] FastAPI application
* [x] PostgreSQL
* [x] SQLAlchemy
* [x] Alembic
* [x] Source model
* [x] Document model
* [x] Document version model
* [x] Section model
* [x] Claim model
* [x] Evidence model
* [x] Claim/evidence relationship
* [x] Entity model
* [x] Claim/entity relationship

## Phase 2 — Regulatory Knowledge

* [ ] Policy change model
* [ ] Action model
* [ ] Claim relationship/supersession model
* [ ] Contradiction representation
* [ ] Temporal version handling
* [ ] Source authority hierarchy
* [ ] Initial official sources
* [ ] Initial Ethiopian regulatory documents

## Phase 3 — Ingestion

* [ ] Document acquisition
* [ ] PDF storage
* [ ] Text extraction
* [ ] Section extraction
* [ ] Metadata extraction
* [ ] Claim extraction
* [ ] Evidence generation
* [ ] Entity extraction
* [ ] Content hashing
* [ ] Document version detection

## Phase 4 — Intelligence

* [ ] Document comparison
* [ ] Change detection
* [ ] Contradiction detection
* [ ] Affected-entity detection
* [ ] Action generation
* [ ] Evidence ranking
* [ ] Query understanding
* [ ] Retrieval engine
* [ ] LLM reasoning layer

## Phase 5 — User Application

* [ ] Business profiles
* [ ] Business/entity matching
* [ ] Regulatory change feed
* [ ] Evidence-backed answers
* [ ] Source navigation
* [ ] "What changed?" interface
* [ ] "Does this affect me?" interface
* [ ] Action recommendations
* [ ] Outdated information warnings
* [ ] Conflict warnings

## Phase 6 — Hackathon Demo

* [ ] Populate real official documents
* [ ] Complete one end-to-end business scenario
* [ ] Polish API
* [ ] Build demonstration UI
* [ ] Create README
* [ ] Create pitch deck
* [ ] Record demo video
* [ ] Final testing
* [ ] Public GitHub repository

---

# Engineering Principles

### 1. Evidence before explanation

Every important answer should be traceable to evidence.

### 2. Preserve history

Never destroy previous regulatory information when new information arrives.

### 3. Separate facts from interpretation

The system should clearly distinguish source statements from AI interpretation.

### 4. Prefer structured retrieval

Use the database to answer structured questions before relying on semantic search.

### 5. No fabricated rationale

If an official source does not state why something changed, the system must not invent a reason.

### 6. Contradictions should be represented

Conflicting information should be preserved and surfaced rather than silently overwritten.

### 7. Narrow first, generalize later

The MVP should solve one concrete information problem extremely well before expanding into other domains.

---

# Technology

Current stack:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic Settings
* Podman / podman-compose

Planned technologies may include:

* PDF/document extraction
* Vector search / `pgvector`
* LLM APIs
* Background processing
* Object/file storage
* Frontend application

Technology choices will be introduced only when they solve a demonstrated requirement.

---

# Development Philosophy

Trusted Information Intelligence is being developed incrementally.

Each database feature follows:

```text
MODEL
  ↓
MIGRATION
  ↓
INSPECTION
  ↓
DATABASE MIGRATION
  ↓
VERIFICATION
  ↓
GIT CHECKPOINT
  ↓
NEXT FEATURE
```

This keeps the schema understandable and makes every architectural decision traceable.

---

# Status

**Current stage: Knowledge foundation**

The database schema is actively being developed. The current implementation contains the foundational structures for sources, documents, versions, sections, claims, evidence, entities, and their relationships.

The next stage is to connect this foundation to **policy changes, actions, document ingestion, and evidence-centered retrieval**.

---

## Core Idea

> **Trusted Information Intelligence does not try to replace authoritative information. It makes authoritative information understandable, connected, traceable, and actionable.**
