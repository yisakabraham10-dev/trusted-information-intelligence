# Services

The `services` package contains the application's **domain logic**.

Services operate on domain models and produce decisions, interpretations, or domain-level results. They do not define database schema, HTTP endpoints, or presentation logic.

The service layer is responsible for answering questions such as:

* How should a source claim be semantically represented?
* Is an interpretation sufficiently reliable to accept automatically?
* Which claims from different versions may refer to the same underlying rule?
* What relationship exists between two corresponding claims?
* Does a set of claim correspondences constitute a policy change?
* Does a policy change require human review?

The service layer is intentionally designed around **evidence, uncertainty, and human verification** rather than assuming that automated interpretation is always correct.

---

## Design Principles

### 1. The source remains authoritative

Services may interpret source material, but they must never replace the original source text.

The distinction is:

```text
Source text
    ↓
Claim
    ↓
Service interpretation
```

The interpretation is derived information.

The original claim and its supporting evidence remain the basis for what the system can substantiate.

---

### 2. Automation must be allowed to say "I don't know"

The system is semi-autonomous.

When an extraction or reasoning service cannot confidently produce a result, it should not invent one merely to complete the pipeline.

Instead:

```text
Automated processing
        ↓
 sufficient confidence?
     /          \
   yes           no
   ↓              ↓
 accept       human review
```

Human review is therefore a normal part of the system rather than an exceptional failure path.

---

### 3. Semantic structure is flexible

Regulatory language does not always describe an action-oriented rule.

For example:

```text
"Importers must submit Form X within 30 days."
```

can naturally be represented as:

```text
actor       → importer
modality    → REQUIRED
action      → submit
object      → Form X
constraints → within 30 days
```

But:

```text
"The customs duty rate for cotton T-shirts is 35%."
```

does not naturally have the same structure.

Therefore, semantic structures should be treated as **useful signals for reasoning**, not as a rigid grammar that every claim must satisfy.

A claim may contain only some semantic elements, or may require a claim-type-specific representation.

A failed semantic extraction must not cause the underlying claim or evidence to be discarded.

---

## Service Pipeline

The intended processing pipeline is:

```text
Official source
      ↓
Document extraction
      ↓
Claim extraction
      ↓
Semantic interpretation
      ↓
Human review when necessary
      ↓
Claim
      ↓
Candidate generation
      ↓
Correspondence evaluation
      ↓
ClaimCorrespondence
      ↓
Change detection
      ↓
PolicyChange
      ↓
Business impact / actions
```

Each stage has a separate responsibility.

---

# Service Responsibilities

## 1. Claim Structure Extraction

Responsible for converting claim text into a semantic representation useful for downstream reasoning.

Conceptually:

```text
Claim text
    ↓
semantic extraction
    ↓
ClaimStructure
```

The extractor should not modify the original claim text.

The semantic representation is an interpretation of the claim.

Possible implementations may include:

```text
RuleBasedClaimStructureExtractor
LLMClaimStructureExtractor
HybridClaimStructureExtractor
```

The rest of the service layer should not depend on which extraction strategy is being used.

### Extraction result

Extraction should eventually provide enough information to determine whether the result can be accepted automatically.

Conceptually:

```text
ExtractionResult
    ├── structure
    ├── confidence
    ├── status
    └── reason
```

Possible statuses include:

```text
AUTO_ACCEPTED
NEEDS_REVIEW
FAILED
```

A reviewer can convert an uncertain or failed extraction into a verified interpretation.

---

# 2. Human Review

Human review exists for claims where automated interpretation is insufficiently reliable.

The reviewer should see:

```text
Original claim
    +
Supporting evidence
    +
Automated interpretation, if available
    +
Reason for review
```

The reviewer may then:

```text
accept the interpretation
modify the interpretation
provide a new interpretation
reject the interpretation
```

The original source text must remain unchanged.

Human-reviewed interpretations should be distinguishable from automatically generated interpretations.

This preserves the provenance distinction between:

```text
SOURCE FACT
AI INTERPRETATION
HUMAN VERIFIED INTERPRETATION
```

---

# 3. Candidate Generation

When comparing claims between document versions, comparing every claim with every other claim does not scale.

For example:

```text
1,000 old claims × 1,000 new claims
= 1,000,000 comparisons
```

Candidate generation reduces this search space.

It should identify claims that are plausible candidates for correspondence using signals such as:

```text
claim type
entities
semantic structure
normalized text
document structure
section/topic
other domain-specific signals
```

Candidate generation should **not** decide that two claims correspond.

Its responsibility is:

> "These claims are worth comparing."

---

# 4. Claim Correspondence Evaluation

The correspondence evaluator determines the relationship between two candidate claims.

Conceptually:

```text
Claim A
   +
Claim B
   ↓
CorrespondenceEvaluator
   ↓
CorrespondenceResult
```

A correspondence result may contain:

```text
relationship_type
confidence
method
```

Possible pairwise relationships include:

```text
SAME
MODIFIED
UNRELATED
POSSIBLE_CONFLICT
```

Set-level relationships such as:

```text
SPLIT
MERGED
```

may require considering multiple claims together and therefore should not necessarily be forced into the pairwise evaluator.

`ADDED` and `REMOVED` are one-sided change concepts and belong to policy-change detection rather than claim correspondence.

---

# 5. Change Detection

Change detection operates on established claim correspondences.

It answers:

> "Given the claims and their relationships across versions, what changed?"

Conceptually:

```text
ClaimCorrespondence
        ↓
ChangeDetector
        ↓
PolicyChange
```

Examples:

```text
Old claim
"Importers must submit the form within 30 days."

New claim
"Importers must submit the form within 15 days."

        ↓

MODIFIED
```

Or:

```text
Old version
"No electronic submission."

New version
"Importers may submit electronically."

        ↓

MODIFIED / PERMITTED
```

Or:

```text
Old version
Rule exists

New version
Rule absent

        ↓

REMOVED
```

The change detector should not independently invent correspondence. It operates on the correspondence layer.

---

# Separation of Responsibilities

The service layer deliberately separates:

```text
DETECTION
    ↓
DECISION
    ↓
PERSISTENCE
```

For example:

```text
CandidateGenerator
    ↓
CorrespondenceEvaluator
    ↓
CorrespondenceResult
    ↓
persistence service
    ↓
ClaimCorrespondence
```

This prevents individual services from becoming tightly coupled to database persistence.

A service should generally be able to reason about domain objects without immediately writing to PostgreSQL.

---

# Provenance and Confidence

Confidence values must describe **the confidence of the operation that produced them**.

For example:

```text
Extraction confidence
```

means:

> How confident are we that the semantic interpretation is correct?

Whereas:

```text
Correspondence confidence
```

means:

> How confident are we that the two claims have the recorded relationship?

These are different concepts and should not be conflated.

Likewise:

```text
Evidence confidence
```

and:

```text
ClaimEvidence strength
```

represent different relationships and should remain separate.

---

# What Services Must Not Do

Services should not:

* redefine database schema
* contain FastAPI route definitions
* contain UI/presentation logic
* replace source evidence with generated text
* silently discard uncertain claims
* treat LLM output as authoritative law
* determine policy changes solely from textual similarity
* overwrite historical regulatory versions
* force every regulatory claim into one rigid semantic structure

---

# Current Service Architecture

The intended service structure is:

```text
src/services/
│
├── README.md
│
├── claim_structure.py
│
├── claim_structure_extractor.py       # planned
├── candidate_generator.py             # planned
├── claim_correspondence.py             # existing evaluator
├── change_detector.py                 # planned
└── ...
```

The exact filenames may evolve as responsibilities become clearer.

The important boundary is the responsibility of each service, not the filename.

---

# Relationship With the Model Layer

The model layer represents persistent domain state.

The service layer reasons over that state.

```text
Models
    ↓
represent what the system knows

Services
    ↓
determine what the system can infer or decide
```

For example:

```text
Claim
ClaimEvidence
Entity
ClaimEntity
ClaimCorrespondence
PolicyChange
```

are domain state.

Whereas:

```text
ClaimStructureExtractor
CandidateGenerator
CorrespondenceEvaluator
ChangeDetector
```

are domain logic.

---

# Core Architectural Goal

The service layer exists to make the following workflow reliable:

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
INTERPRETATION
  ↓
VERIFICATION
  ↓
CORRESPONDENCE
  ↓
CHANGE
  ↓
IMPACT
  ↓
ACTION
```

The system should prefer:

> **uncertainty + human verification**

over:

> **false confidence + automated fabrication**

This is essential because the product's purpose is not merely to generate plausible answers.

Its purpose is to produce **traceable information that users can verify against authoritative evidence**.
