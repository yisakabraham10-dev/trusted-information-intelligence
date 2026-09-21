# API

The `src/api/` package is the HTTP boundary of Trusted Information Intelligence. It exposes the backend through FastAPI routers while keeping regulatory reasoning in services and use cases.

## Architecture

```text
Frontend
   ↓
FastAPI Router
   ↓
Request / Response Schema
   ↓
Use Case / Service
   ↓
Domain Models
   ↓
PostgreSQL
```

Routers should validate HTTP input, call application behavior, and return API responses. They should not contain the core regulatory reasoning.

## API Areas

- **Business profiles** — retrieve a business profile and its regulatory context.
- **Claims** — retrieve source-backed claims.
- **Comparisons** — compare two versioned claims.
- **Policy changes** — retrieve detected regulatory changes and detailed evidence.
- **Document submissions** — submit, review, ingest, and inspect documents.
- **Health** — verify application and database availability.

## Endpoints

### Business Profiles

```http
GET /business-profiles/{business_profile_id}
```

Returns the stored business profile used for applicability evaluation.

### Claims

```http
GET /claims/{claim_id}
```

Returns a claim together with its relevant source-backed information.

### Claim Comparison

```http
POST /claims/{old_claim_id}/compare/{new_claim_id}
```

Compares two claims from different regulatory versions.

### Policy Changes

```http
GET /policy-changes/{id}
GET /policy-changes/{id}/detail
```

The detail endpoint exposes the relationships needed to understand a detected change rather than returning only a summary.

### Document Submissions

```http
POST /document-submissions
POST /document-submissions/{submission_id}/review
POST /document-submissions/{submission_id}/ingest
GET  /document-submissions/{submission_id}/file
```

Document submission is separated from ingestion so that review and processing can remain explicit stages.

### Health

```http
GET /health
GET /health/db
```

The first checks application availability. The second verifies database connectivity.

## Router Registration

Routers are registered by the FastAPI application in `src/main.py`.

The API currently covers:

```text
business_profiles
claims
comparisons
policy_changes
document_submissions
```

## API vs Domain Logic

The boundary is intentional:

| API layer | Service/domain layer |
|---|---|
| Parse HTTP requests | Interpret regulatory claims |
| Validate request schemas | Resolve entities |
| Select response shape | Match claims across versions |
| Handle HTTP errors | Detect policy changes |
| Expose endpoints | Evaluate applicability |

This keeps the backend testable without requiring every domain operation to run through HTTP.

## Error Handling

API endpoints should return clear HTTP-level errors while preserving useful domain failure information.

Validation belongs at the API boundary when the problem is malformed input. Domain invariants belong in the service/domain layer so they remain enforced regardless of the caller.

## API Documentation

FastAPI provides interactive OpenAPI documentation when the development server is running:

```text
/docs
/redoc
```

## Local Development

From the repository root:

```bash
source .venv/bin/activate
uvicorn src.main:app --reload
```

The frontend can then call the local API according to its configured backend URL.

## Design Principle

The API should remain boring.

The difficult reasoning belongs behind the API boundary, where it can be tested independently and kept grounded in evidence.

## Related Documentation

- `src/models/README.md` — persistence and domain model
- `src/services/README.md` — regulatory intelligence logic
- `tests/README.md` — test architecture
- `frontend/README.md` — frontend integration
