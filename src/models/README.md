# Domain Models

This directory contains the core domain models of Trusted Information Intelligence.

The models represent the structured knowledge extracted from authoritative documents and the relationships between that knowledge.

## Domain Structure

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
  │     ├── ClaimEvidence → Evidence
  │     ├── ClaimEntity → Entity
  │     └── ClaimCorrespondence
  │
  └── Evidence

ClaimCorrespondence
  ↓
PolicyChange
```

## Core Concepts

### Source

Represents an institution or authoritative origin of information.

Examples include government ministries, regulatory agencies, and other official institutions.

### Document

Represents a logical document published by a source.

A document can have multiple versions over time.

### DocumentVersion

Represents a specific published version of a document.

Versions preserve historical changes and allow the system to determine what information was applicable at a particular point in time.

### Section

Represents a structured portion of a document, such as an article, subsection, chapter, or other identifiable unit.

Sections provide the location from which claims and evidence are extracted.

### Claim

Represents a discrete, checkable factual assertion made by a source.

A claim is **version-specific**. The same underlying rule may therefore be represented by different claims across different document versions.

Claims should not be treated as automatically true merely because they originate from an official source. Their provenance and supporting evidence must remain traceable.

### Evidence

Represents a specific piece of source material supporting or contradicting a claim.

Evidence points back to a section and may include a page number and source quotation.

### Entity

Represents a meaningful domain entity referenced by claims.

Examples include:

* Importers
* Products
* Government institutions
* Licenses
* Fees
* Procedures

### ClaimEvidence

Associates claims with evidence and describes the relationship between them.

### ClaimEntity

Associates claims with the entities involved in those claims.

### ClaimCorrespondence

Represents the relationship between claims across versions or documents.

Correspondence answers:

> Are these two claims describing the same underlying rule, and if so, how are they related?

Possible relationships include:

* `SAME`
* `MODIFIED`
* `SPLIT`
* `MERGED`
* `UNRELATED`
* `POSSIBLE_CONFLICT`

Claim correspondence establishes semantic continuity between version-specific claims.

### PolicyChange

Represents a meaningful change identified from the relationship between claims across versions.

A policy change is therefore built **on top of claim correspondence**, rather than determining correspondence itself.

Examples include:

* A requirement changing from 30 days to 15 days
* A new requirement being introduced
* An existing requirement being removed
* A rule being divided into multiple requirements
* Multiple previous requirements being consolidated

## Design Principles

### Evidence First

The system should preserve the chain:

```text
Policy Change
    ↓
Claim
    ↓
Evidence
    ↓
Section
    ↓
Document Version
    ↓
Document
    ↓
Source
```

Every important factual statement shown to a user should ultimately be traceable to authoritative source material.

### Version-Specific Claims

Claims belong to the document version from which they were extracted.

Do not assume that two claims with similar text have the same identity.

### Semantic Continuity Through Correspondence

Claims across versions are connected through `ClaimCorrespondence`.

This allows the system to distinguish between:

```text
same rule
modified rule
split rule
merged rule
unrelated claims
possible conflicts
```

### Domain Models vs Processing Logic

These models represent **what the system knows**.

They should not contain the algorithms used to discover or match that knowledge.

For example, claim matching logic belongs in the service layer, while `ClaimCorrespondence` stores the resulting relationship.

## Adding a New Model

Before adding a model, determine:

1. What real domain concept does it represent?
2. What information does it own?
3. What existing concept does it relate to?
4. Does it represent knowledge, evidence, or processing state?
5. Can the concept be represented by an existing model instead?

Avoid adding fields simply because they may be useful later. Prefer the smallest model that correctly represents the domain.
