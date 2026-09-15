# Trusted Information Intelligence

> **What changed. Why it changed. Who it affects. What to do. And where the evidence comes from.**

An evidence-centered information intelligence platform that transforms fragmented public information into **context-aware, actionable, and verifiable answers**.

The initial focus is on helping Ethiopian import/export businesses understand regulatory and procedural information without requiring them to navigate dozens of disconnected documents, websites, announcements, and secondary sources.

---

## The Problem

Important public information often exists, but simply being available does not make it useful.

A business owner may need to know:

* What documents are required to import a product?
* Did a requirement recently change?
* When does the new requirement take effect?
* Does the change actually affect my business?
* What do I need to do differently?
* Why was the change introduced?
* Which source proves this?
* Is the information current?
* What should I do if different sources appear to contradict each other?

Today, answering these questions can require searching across government websites, legal documents, portals, announcements, PDFs, news reports, and informal sources.

The problem is therefore not simply **lack of information**.

It is the lack of a reliable chain connecting:

```text
Information
    ↓
Source
    ↓
Claim
    ↓
Change
    ↓
Impact
    ↓
Action
    ↓
Evidence
```

---

## Our Approach

Trusted Information Intelligence is designed around an **evidence-centered information architecture**.

Instead of treating the LLM as the source of truth, the platform separates:

* **facts and provenance** → structured database
* **document evidence** → preserved source material
* **retrieval** → SQL, keyword, and semantic search
* **reasoning and explanation** → LLM
* **user context** → business profile
* **trust assessment** → evidence validation

The core principle is:

> **The LLM interprets and explains information. It does not manufacture the information.**

---

# Core User Experience

The platform is designed around three ways a user can interact with information.

### 1. Proactive

The platform identifies changes relevant to the user's profile.

Example:

> ⚠️ **A new import requirement may affect your clothing business.**

The user can immediately see what changed, when it takes effect, and what action may be required.

### 2. Exploratory

Users can ask questions naturally:

> "I'm importing clothes from China next month. What do I need?"

The system interprets the user's intent instead of requiring the user to know the exact terminology used in a government document.

### 3. Verification

Users can inspect the evidence behind an answer.

For every important claim, the platform can expose:

```text
Claim
 ↓
Evidence
 ↓
Article / Section
 ↓
Document
 ↓
Document Version
 ↓
Source Institution
```

This allows users to verify important information themselves.

---

# Example User Journey

A clothing importer creates a business profile:

```text
Business type: Importer
Location: Addis Ababa
Product: Clothing
Origin: China
```

The dashboard then identifies relevant information.

### Dashboard

```text
2 changes may affect your business

🔴 Import requirement changed
   Effective September 20

🟡 Customs procedure updated
   Effective October 1
```

The user selects the first change.

### Change Detail

```text
WHAT CHANGED?

Before:
Requirement A

Now:
Requirement B

Effective:
September 20, 2026


WHY DID IT CHANGE?

Officially stated rationale:
...

Evidence level:
✓ Officially stated


DOES THIS AFFECT YOU?

Yes.

Your profile indicates that you import
finished garments from China.


WHAT SHOULD YOU DO?

1. Obtain ...
2. Submit ...
3. Complete ...


EVIDENCE

Ministry of ...
Regulation No. ...
Article 7 · Page 14

[View original document]
```

The goal is to turn complicated information into a decision a person can actually act on.

---

# Natural Language Without "RAG-First" UX

Traditional RAG systems often depend heavily on the wording of a user's question.

That creates a poor user experience:

```text
User question
      ↓
Embedding
      ↓
Vector similarity
      ↓
Top-k chunks
      ↓
LLM
```

A user may know exactly what they want but phrase it differently from the language used in the source documents.

This platform instead uses **query understanding and query planning**.

```text
Natural language
      ↓
Query understanding
      ↓
Intent extraction
      ↓
Entity extraction
      ↓
User context
      ↓
Query planning
      ↓
Structured + semantic retrieval
      ↓
Evidence validation
      ↓
LLM synthesis
```

For example:

> "I'm trying to bring shirts from China next month. What papers do I need?"

can become:

```json
{
  "intent": "IMPORT_REQUIREMENTS",
  "business_type": "IMPORTER",
  "product": "CLOTHING",
  "origin": "CHINA",
  "location": "ADDIS_ABABA",
  "time_context": "NEXT_MONTH"
}
```

This allows the system to use structured database queries where possible and semantic retrieval only where useful.

---

# Architecture

```text
                         USER
                           │
                           ▼
                ┌─────────────────────┐
                │ Web / User Interface │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Query Understanding │
                │                     │
                │ Intent              │
                │ Entities            │
                │ Time                │
                │ User Context        │
                └──────────┬──────────┘
                           │
                           ▼
                    Query Planner
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
            SQL        Keyword        Vector
         Retrieval    Retrieval      Retrieval
              │            │            │
              └────────────┼────────────┘
                           ▼
                  Evidence Ranking
                           │
                           ▼
                  Evidence Validation
                           │
                           ▼
                         LLM
                           │
                           ▼
              ┌────────────────────────┐
              │ Structured Response    │
              │                        │
              │ Answer                 │
              │ What changed           │
              │ Why                    │
              │ Impact                 │
              │ Actions                │
              │ Warnings               │
              │ Evidence               │
              └────────────────────────┘
```

---

# Evidence-Centered Knowledge Model

The system does not treat an entire PDF as a single piece of knowledge.

Instead:

```text
Source
  │
  ▼
Document
  │
  ▼
Document Version
  │
  ▼
Section / Article
  │
  ▼
Claim
  │
  ├──────────────► Entity
  │
  ├──────────────► Requirement
  │
  └──────────────► Evidence
                       │
                       ▼
                 Policy Change
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Impact                Action
```

This structure allows the platform to answer questions such as:

* What does the regulation say?
* Which article says it?
* Which version introduced it?
* What changed from the previous version?
* Who is affected?
* What action is required?
* What evidence supports the answer?

---

# Source Hierarchy

Not all information sources should have equal authority.

The platform therefore assigns sources different trust levels.

### Tier 1 — Primary authoritative sources

Examples:

* Government ministries
* Government agencies
* Official proclamations
* Regulations
* Directives
* Official procedural documents

These are the primary sources used to establish facts.

### Tier 2 — Official aggregators

Examples:

* Government portals
* Official service platforms
* Government legal repositories

### Tier 3 — Institutional sources

Examples:

* Chambers of commerce
* Professional institutions
* Recognized organizations

### Tier 4 — Secondary sources

Examples:

* News organizations
* Professional publications
* Industry analysis

### Tier 5 — Public signals

Examples:

* Social media
* Telegram
* Public discussions

Lower-tier sources may help **discover information or identify potential conflicts**, but they should not automatically override authoritative sources.

---

# Trust and Evidence

The system should never pretend that an answer is certain when the evidence does not support it.

Possible answer states include:

```text
SUPPORTED
PARTIALLY_SUPPORTED
CONFLICTING
OUTDATED
INSUFFICIENT_EVIDENCE
```

For explanations of why a policy changed, the platform distinguishes between:

### Officially stated rationale

The source explicitly explains why the change was introduced.

### Supporting official context

Other authoritative sources provide context but do not explicitly state the reason.

### AI interpretation

The explanation is an inference made from available evidence.

### Unknown

No reliable rationale was found.

The system must never turn an inference into an official statement.

---

# Policy Change Detection

A central feature of the platform is understanding **change**, not merely retrieving documents.

The system compares document versions and identifies changes such as:

* Added requirements
* Removed requirements
* Modified requirements
* New fees
* Changed fees
* Changed deadlines
* Changed eligibility
* Changed penalties
* Changed procedures
* Changed responsible institutions
* Changed effective dates

Conceptually:

```text
OLD VERSION
     │
     │ compare
     ▼
NEW VERSION
     │
     ▼
CHANGE DETECTION
     │
     ├── What changed?
     ├── Why?
     ├── Who is affected?
     ├── When does it apply?
     └── What should they do?
```

---

# Business Context

Information becomes much more useful when the system knows who is asking.

A business profile may contain:

```json
{
  "business_type": "IMPORTER",
  "location": "Addis Ababa",
  "products": [
    "clothing"
  ],
  "origins": [
    "China"
  ]
}
```

This allows the platform to distinguish:

> "A regulation exists."

from:

> **"This regulation affects your business because you import finished garments."**

The architecture is intentionally domain-independent.

The initial domain is import/export, but the same knowledge model can eventually support:

* Construction
* Agriculture
* Healthcare
* Employment
* Education
* Business registration
* Public services
* Environmental regulation
* Other civic information

---

# Technology Stack

## Backend

* **Python**
* **FastAPI**
* **PostgreSQL**
* **SQLAlchemy / SQLModel**
* **Alembic**
* **Pydantic**

## Retrieval

* PostgreSQL structured queries
* Keyword retrieval
* **pgvector** for semantic retrieval where appropriate

## AI

The LLM is responsible for:

* Query understanding
* Intent extraction
* Entity extraction
* Natural-language synthesis
* Evidence-grounded explanation

The LLM is **not** the source of truth.

## Frontend

The frontend will provide:

* Business profile
* Personalized dashboard
* Policy-change cards
* Change details
* Evidence inspection
* Natural-language questions

## Infrastructure

* Docker
* PostgreSQL
* Environment-based configuration
* Automated testing
* Deployment-ready API

---

# Database Model

The initial data model is centered around provenance.

```text
sources
   │
   └── documents
          │
          └── document_versions
                  │
                  └── sections
                         │
                         └── claims
                                │
                   ┌────────────┼─────────────┐
                   ▼            ▼             ▼
                evidence     entities     changes
                                               │
                                               ▼
                                            actions
```

Core entities include:

| Entity              | Purpose                                                    |
| ------------------- | ---------------------------------------------------------- |
| `sources`           | Organizations and authoritative information sources        |
| `documents`         | Legal, regulatory, procedural, and informational documents |
| `document_versions` | Different versions of a document                           |
| `sections`          | Articles, sections, and page-level document structure      |
| `claims`            | Atomic pieces of information extracted from sources        |
| `evidence`          | Source-backed support for claims                           |
| `entities`          | Products, institutions, business types, locations, etc.    |
| `policy_changes`    | Relationships between old and new claims                   |
| `actions`           | Actions associated with changes or requirements            |
| `business_profiles` | User/business context                                      |

---

# Original Documents and Provenance

Original documents are preserved as immutable source material.

The system stores structured information in PostgreSQL while retaining the original source document separately.

```text
Original Document
       │
       ├──────────────► Object/File Storage
       │
       └──────────────► Extraction
                              │
                              ▼
                         PostgreSQL
```

This is important because the platform should be able to show users the actual evidence behind an answer.

A typical provenance chain is:

```text
Answer
  ↓
Claim
  ↓
Evidence
  ↓
Article / Section
  ↓
Document Version
  ↓
Document
  ↓
Source Institution
```

---

# Data Ingestion

The initial version will use a carefully curated set of authoritative documents rather than attempting to crawl the entire internet.

The initial knowledge base will prioritize:

* High-quality primary sources
* Current documents
* Relevant historical versions
* Explicit document metadata
* Page and article references
* Clearly structured claims
* Evidence relationships

The goal is **quality and traceability**, not maximum document count.

---

# Security and Trust Principles

The platform is designed around several principles:

### 1. Evidence over confidence

A confident LLM response is not evidence.

### 2. Primary sources over secondary sources

Secondary information may provide context but should not silently replace authoritative sources.

### 3. Explicit uncertainty

When evidence is insufficient, the system should say so.

### 4. Version awareness

A correct statement from an outdated document can still produce an incorrect answer.

### 5. No fabricated citations

The system must never generate a citation that does not correspond to actual stored evidence.

### 6. Explainable answers

Users should be able to understand why the system reached its conclusion.

---

# Project Structure

The planned backend structure is:

```text
trusted-information/
│
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── ai/
│   └── data/
│
├── documents/
│
├── scripts/
│
├── tests/
│
├── alembic/
│
├── .env.example
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

The exact structure may evolve as implementation progresses.

---

# Development Roadmap

## Phase 0 — Scope Freeze

Define and freeze:

* Core user journey
* Initial domain
* Database model
* API boundaries
* Evidence model
* AI responsibilities

**Status:** Completed

---

## Phase 1 — Platform Foundation

Build:

* FastAPI application
* PostgreSQL
* Database models
* Alembic migrations
* Configuration
* Basic API structure
* Testing foundation

**Status:** In progress

---

## Phase 2 — Knowledge Layer

Build:

* Source management
* Document management
* Document versions
* Sections
* Claims
* Evidence
* Entities
* Initial curated dataset

**Status:** Planned

---

## Phase 3 — Provenance Engine

Build the chain:

```text
Claim
 ↓
Evidence
 ↓
Section
 ↓
Document
 ↓
Source
```

Users should be able to inspect the origin of important information.

**Status:** Planned

---

## Phase 4 — Intelligence Engine

Build:

* Query understanding
* Intent extraction
* Entity extraction
* Query planning
* Structured retrieval
* Semantic retrieval
* Evidence ranking
* Evidence validation
* LLM synthesis

**Status:** Planned

---

## Phase 5 — Policy Change Engine

Build:

* Document comparison
* Claim comparison
* Change detection
* Change classification
* Rationale relationships
* Effective dates
* Impact relationships

**Status:** Planned

---

## Phase 6 — Business Intelligence

Build:

* Business profiles
* Relevance matching
* Affected-business detection
* Personalized impact analysis
* Recommended actions

**Status:** Planned

---

## Phase 7 — User Experience & Deployment

Build:

* Dashboard
* Change interface
* Evidence viewer
* Natural-language interface
* Deployment
* Demo
* Documentation
* Final testing

**Status:** Planned

---

# What This Project Is Not

This project is **not** intended to be:

### ❌ A generic chatbot

The goal is not to create another interface around an LLM.

### ❌ A simple PDF chatbot

Documents are structured into claims, evidence, entities, versions, and relationships.

### ❌ A pure RAG application

Semantic retrieval is only one component of the retrieval system.

### ❌ A replacement for government authorities

The platform helps users discover, understand, and verify information. It does not become the legal authority.

### ❌ A system that invents explanations

When the official reason for a change is unknown, the system must say so.

---

# Design Philosophy

The platform follows five principles:

```text
1. Understand the user
2. Retrieve the right information
3. Verify the evidence
4. Explain the result
5. Show the source
```

Or more simply:

> **Don't just answer the question. Show the user why the answer should be trusted.**

---

# Initial Target User

The initial demonstration user is:

```text
Business:
Clothing importer

Location:
Addis Ababa, Ethiopia

Origin:
China

Products:
Finished garments
```

The initial product will therefore focus on answering questions around:

* Import requirements
* Documentation
* Procedures
* Regulatory changes
* Effective dates
* Fees and requirements
* Business impact
* Official rationale
* Evidence and provenance

The underlying architecture is intended to generalize beyond this initial use case.

---

# Long-Term Vision

The initial system focuses on regulatory intelligence for businesses.

The same infrastructure can eventually become a broader **trusted information layer for civic and economic life**.

Potential future applications include:

```text
Government Service Navigator
          │
          ├── What service do I need?
          ├── Who provides it?
          ├── What documents are required?
          └── What is the procedure?

Public Policy Intelligence
          │
          ├── What changed?
          ├── Why?
          ├── Who is affected?
          └── What evidence supports this?

Journalist / Research Intelligence
          │
          ├── Source discovery
          ├── Contradiction detection
          ├── Historical comparison
          └── Evidence tracing
```

The long-term objective is to make reliable information not only **available**, but **understandable, contextual, actionable, and verifiable**.

---

# Current Status

🚧 **Active development**

The architecture and product direction have been defined. Implementation is beginning with the platform foundation and core data model.

The project intentionally prioritizes:

* Evidence quality
* Provenance
* User experience
* Explainability
* Correctness
* Practical usefulness

over unnecessary infrastructure complexity.

---

# Hackathon Context

This project is being developed for the **OSF × Andela "Information You Can Trust" Hackathon**.

The project is aligned with the hackathon's focus on making reliable information about civic life and opportunity more visible, accessible, and actionable.

The implementation is designed around the principle that **trust is not created by an AI model claiming to be confident; it is created by making the evidence behind important information inspectable.**

---

# License

License to be determined.
