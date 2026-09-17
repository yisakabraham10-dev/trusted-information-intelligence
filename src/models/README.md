# Models

The `models` package defines the **persistent domain model** of Trusted Information Intelligence.

Models describe what the system knows and preserve that knowledge in the database.

They should not contain the application's higher-level reasoning algorithms. Domain reasoning belongs in `src/services`.

---

# Core Principle

The database is the system's source of truth.

The system deliberately separates:

```text
Source information
        ↓
Evidence
        ↓
Claims
        ↓
Derived relationships
        ↓
Policy changes
```

Generated interpretations and automated decisions must not overwrite the underlying source information.

Historical regulatory information must be preserved.

---

# Domain Model

The current domain can be understood as:

```text
Source
  ↓
Document
  ↓
DocumentVersion
  ↓
Section
  ├── Claim
  │     ├── ClaimEvidence ── Evidence
  │     ├── ClaimEntity ─── Entity
  │     └── ClaimCorrespondence
  │
  └── Evidence

ClaimCorrespondence
        ↓
PolicyChange
   ├── PolicyChangeClaim
   └── PolicyChangeCorrespondence
```

The model layer therefore contains both:

1. **Source-backed information**
2. **Derived domain relationships**

The distinction between the two must remain explicit.

---

# Source and Document Hierarchy

## Source

Represents an institution or origin from which information is obtained.

Examples include:

```text
Ethiopian Customs Commission
Ministry of Trade and Regional Integration
Ministry of Revenue
National Bank of Ethiopia
```

A source establishes provenance.

```text
Source
   ↓
Document
```

---

## Document

Represents a logical document published by a source.

A document may have multiple versions over time.

```text
Document
   ├── Version 1
   ├── Version 2
   └── Version 3
```

The document itself represents the persistent identity of the publication, while versions represent changes to its contents.

---

## DocumentVersion

Represents a particular version of a document.

Versions must not be overwritten when a newer version becomes available.

A version contains information such as:

```text
publication date
effective date
storage location
content hash
status
superseded version
```

The `content_hash` helps identify the exact underlying document content.

This allows the system to preserve the historical state of regulatory information.

---

# Section

A `Section` represents a meaningful structural portion of a document version.

Examples:

```text
Article 4
Section 2
Schedule I
Chapter III
Paragraph 7
```

Sections provide structure between the document and individual claims.

They also provide a precise location for evidence.

```text
DocumentVersion
       ↓
    Section
       ↓
   Claim / Evidence
```

---

# Claim

A `Claim` represents an **atomic assertion extracted from a source**.

The original claim text is preserved.

A claim currently contains:

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

The important distinction is:

```text
Claim ≠ Evidence
```

A claim represents what the system has identified as an assertion.

Evidence represents the source material supporting that assertion.

---

# Claim Semantics

Claims may also have a semantic interpretation used by the service layer.

For example:

```text
"Importers must submit Form X within 30 days."
```

may be interpreted as:

```text
actor       → importer
modality    → REQUIRED
action      → submit
object      → Form X
constraints → within 30 days
```

This semantic representation is **derived information**.

It does not replace the original claim text.

Not every regulatory claim is naturally action-oriented. Definitions, fees, applicability rules, tables, exceptions, and other forms of regulatory language may require different semantic representations.

Therefore semantic structure should not be treated as a rigid requirement that every claim must satisfy.

---

# Evidence

An `Evidence` record represents a source passage supporting or otherwise documenting a claim.

Current information includes:

```text
section_id
page
quote
confidence
```

A typical evidence record may identify:

```text
Document
   ↓
DocumentVersion
   ↓
Section
   ↓
Page
   ↓
Exact quote
```

The goal is to make important claims independently traceable to their source.

---

# ClaimEvidence

`ClaimEvidence` is the association between a claim and evidence.

It currently contains:

```text
claim_id
evidence_id
relation_type
strength
```

Claim and evidence are many-to-many.

One claim may have multiple supporting or contradictory pieces of evidence.

One evidence passage may also be relevant to multiple claims.

The distinction between:

```text
Evidence.confidence
```

and:

```text
ClaimEvidence.strength
```

must be preserved.

They answer different questions.

---

# Entity

An `Entity` represents a meaningful domain object referred to by claims.

Examples may include:

```text
Importer
Cotton T-Shirt
Form X
Customs Duty
Ethiopian Customs Commission
Country of Origin
```

Entities allow claims to be connected through shared concepts rather than only through their textual wording.

---

# ClaimEntity

`ClaimEntity` associates claims with entities.

It currently contains:

```text
claim_id
entity_id
relation_type
```

Claim and entity are many-to-many.

For example:

```text
Claim
"Importers must pay customs duty on cotton T-shirts."

        ↕
   ClaimEntity

        ↕
Entity: Cotton T-Shirt
Entity: Importer
Entity: Customs Duty
```

The exact meaning of an entity's relationship to a claim is represented by `relation_type`.

---

# ClaimCorrespondence

`ClaimCorrespondence` represents a relationship between two claims that may describe the same underlying rule across different versions or documents.

This is an important distinction:

> **Claim identity is not determined by text alone.**

Two claims can use different wording while referring to the same underlying regulatory rule.

Conversely, similar wording does not necessarily mean that two claims represent the same rule.

The model therefore stores correspondence explicitly.

Current fields include:

```text
claim_a_id
claim_b_id
relationship_type
confidence
method
status
created_at
```

The pair is deliberately represented as:

```text
claim_a
claim_b
```

rather than:

```text
old_claim
new_claim
```

because correspondence is not inherently restricted to consecutive versions.

---

## Correspondence Types

The current conceptual pairwise relationships are:

```text
SAME
MODIFIED
UNRELATED
POSSIBLE_CONFLICT
```

Additional relationships such as:

```text
SPLIT
MERGED
```

may require evaluating multiple claims together rather than evaluating one pair independently.

`ADDED` and `REMOVED` are change concepts rather than correspondence relationships because they involve a claim existing on only one side.

---

# PolicyChange

`PolicyChange` represents a detected change in a regulatory rule.

It is built **on top of claim correspondence**.

Conceptually:

```text
Claim A
   ↓
ClaimCorrespondence
   ↓
PolicyChange
   ↓
Claim B
```

A policy change may involve multiple correspondences.

For example, one old claim may become two new claims, or multiple old claims may be consolidated into one new claim.

Therefore `PolicyChange` does not directly assume a single claim-to-claim relationship.

Current information includes:

```text
change_type
summary
effective_date
reason_claim_id
status
detected_at
```

---

# PolicyChangeClaim

`PolicyChangeClaim` associates claims with a policy change.

It contains:

```text
policy_change_id
claim_id
role
```

The role identifies how the claim participates in the change.

Current roles include:

```text
OLD
NEW
```

This allows one policy change to contain multiple old and new claims.

For example:

```text
PolicyChange
    │
    ├── OLD → Claim A
    ├── OLD → Claim B
    └── NEW → Claim C
```

This structure supports changes that are more complicated than one-to-one replacements.

---

# PolicyChangeCorrespondence

`PolicyChangeCorrespondence` connects a policy change to the claim correspondences that support it.

It contains:

```text
policy_change_id
correspondence_id
```

The relationship is:

```text
PolicyChange
      ↓
PolicyChangeCorrespondence
      ↓
ClaimCorrespondence
      ↓
Claims
```

This preserves the reasoning chain behind a detected change.

A policy change therefore does not merely say:

> "Something changed."

It can retain the claim-level relationships used to establish that change.

---

# Official Rationale

A policy change may have an official reason stated by the issuing institution.

The current design represents this through:

```text
reason_claim_id
```

rather than storing an unsupported generated explanation.

The rationale therefore follows the same provenance model:

```text
PolicyChange
      ↓
reason_claim_id
      ↓
Claim
      ↓
Evidence
      ↓
Official source
```

If no explicit official rationale exists, the field may remain `NULL`.

The system should distinguish:

```text
Official rationale
```

from:

```text
AI interpretation
```

An AI-generated explanation must not be presented as an official government reason.

---

# Historical Integrity

Regulatory information is temporal.

The database should preserve:

```text
Version 1
   ↓
Version 2
   ↓
Version 3
```

rather than replacing Version 1 with Version 3.

This enables the system to answer:

```text
What was the rule before?
What is the rule now?
When did it change?
What evidence supports each version?
```

Historical claims should therefore coexist with current claims.

Contradictory claims may also legitimately coexist when they originate from different documents, versions, or institutions.

A contradiction in the database does not automatically mean that one record should be deleted.

---

# Model vs Service Layer

The boundary is:

```text
┌───────────────────────────┐
│        MODEL LAYER        │
│                           │
│ What the system knows     │
│ and preserves             │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       SERVICE LAYER       │
│                           │
│ What the system infers,   │
│ evaluates, or decides     │
└───────────────────────────┘
```

Models should represent domain state.

Services should perform operations such as:

```text
semantic extraction
candidate generation
correspondence evaluation
change detection
human-review decisions
```

The model layer should not become a collection of hidden reasoning algorithms.

---

# Persistence and Provenance

The intended provenance chain is:

```text
Answer
  ↓
PolicyChange / Claim
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

This chain is central to the project.

The system should be able to move from a generated answer back to the underlying official evidence.

---

# Current Model Files

```text
src/models/
├── __init__.py
├── source.py
├── document.py
├── document_version.py
├── section.py
├── claim.py
├── evidence.py
├── claim_evidence.py
├── entity.py
├── claim_entity.py
├── claim_correspondence.py
├── policy_change.py
├── policy_change_claim.py
└── policy_change_correspondence.py
```

Additional domain models may be introduced later when the product requires them.

A new model should only be added when it represents a distinct persistent domain concept.

---

# Architectural Rule

Before adding a model, ask:

> **What distinct piece of persistent domain knowledge does this represent?**

Before adding a service, ask:

> **What reasoning or operation does this perform over the domain?**

Avoid creating models merely to hold temporary computation.

Avoid creating services merely to wrap simple database operations.

The goal is a domain model that is:

```text
explicit
traceable
historically accurate
evidence-centered
extensible
```

while keeping interpretation and decision-making in the service layer.
