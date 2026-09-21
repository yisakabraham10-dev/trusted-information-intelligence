# Tests

The `tests/` directory protects the behavior and invariants of Trusted Information Intelligence.

The suite is intentionally organized around the domain rather than around individual implementation files.

## Structure

```text
tests/
├── api/
│   ├── test_business_profiles.py
│   ├── test_claims.py
│   ├── test_comparisons.py
│   ├── test_document_submissions.py
│   └── test_policy_changes.py
├── services/
│   ├── test_applicability.py
│   ├── test_change_detector.py
│   ├── test_claim_correspondence.py
│   ├── test_claim_creation.py
│   ├── test_claim_entity.py
│   ├── test_claim_evidence_validation.py
│   ├── test_claim_extraction*.py
│   ├── test_claim_structure*.py
│   ├── test_customs_article_51_change.py
│   ├── test_document_*.py
│   ├── test_entity_resolution.py
│   ├── test_groq_*.py
│   ├── test_moj_source_discovery.py
│   ├── test_policy_change*.py
│   ├── test_primitive_comparison.py
│   ├── test_real_customs_ingestion.py
│   ├── test_regulatory_structure.py
│   └── test_requirement_comparison.py
├── use_cases/
│   └── test_compare_regulatory_versions.py
└── fixtures/
    ├── customs_proclamation_1425_2026.pdf
    └── moj/
```

## Run Everything

From the repository root:

```bash
pytest -q
```

## Run by Layer

API tests:

```bash
pytest -q tests/api
```

Service tests:

```bash
pytest -q tests/services
```

Use-case tests:

```bash
pytest -q tests/use_cases
```

Run one integration test:

```bash
pytest -q tests/services/test_customs_article_51_change.py
```

## What the Tests Protect

### Evidence integrity

Claims should not become authoritative without appropriate evidence.

### Version-aware reasoning

Claims from different document versions must retain their temporal context.

### Entity identity

Deterministic entity resolution should not accidentally create duplicate canonical entities or merge unrelated entities.

### Structured comparison

Changes such as:

```60 days → 45 days
```

should be detected through the structured requirement representation.

### Correspondence

The system must distinguish correspondence between claims from the policy change produced from that correspondence.

### Applicability

The evaluator must distinguish:

```APPLIES
DOES_NOT_APPLY
UNKNOWN
```

Missing information must not silently become a positive or negative applicability decision.

### Transactions

Persistence operations should commit successful work and roll back failed operations without leaving inconsistent partial state.

### Real regulatory integration

The Customs fixture provides a realistic vertical slice through ingestion, evidence, claims, correspondence, change detection, policy-change persistence, and applicability.

## Testing Philosophy

The goal is not to maximize a coverage percentage.

The goal is to make incorrect domain behavior difficult to introduce.

Tests should therefore protect:

- invariants
- state transitions
- persistence relationships
- error behavior
- transaction boundaries
- real vertical workflows

When changing domain behavior, update the relevant tests at the same time.
