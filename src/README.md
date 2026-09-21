# Backend Source

The `src/` directory contains the backend application and the core regulatory intelligence domain.

## Architecture

The backend is organized around a separation between HTTP delivery, application use cases, domain services, and persistence.

```text
HTTP / FastAPI
      ↓
API Schemas
      ↓
Use Cases
      ↓
Domain Services
      ↓
SQLAlchemy Models
      ↓
PostgreSQL
```

## Directories

### `api/`

FastAPI routers and HTTP-level orchestration.

Current API areas include:

- business profiles
- claims
- comparisons
- policy changes
- document submissions

### `schemas/`

Pydantic request and response models used at the API boundary.

### `use_cases/`

Application operations that coordinate domain behavior.

Examples include:

- comparing regulatory versions
- retrieving policy-change details

### `services/`

Core regulatory intelligence behavior, including:

- document ingestion
- regulatory structure parsing
- claim extraction
- claim structure
- entity resolution
- primitive comparison
- requirement comparison
- claim correspondence
- change detection
- policy-change persistence
- applicability
- business profiles
- document submissions

### `models/`

SQLAlchemy persistence models representing the regulatory knowledge model.

Important concepts include:

```text
Source
Document
DocumentVersion
Section
Evidence
Claim
Entity
ClaimEntity
ClaimCorrespondence
PolicyChange
BusinessProfile
BusinessProfileEntity
BusinessProfileSource
DocumentSubmission
```

### `db/`

Database engine, sessions, dependencies, and declarative model configuration.

### `domain/`

Domain-level exceptions and concepts that should remain independent of FastAPI.

## Core Domain Flow

```text
Source
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
Policy Change
  ↓
Business Applicability
```

## Important Invariants

The backend is designed around several invariants:

1. Important claims must be supported by evidence.
2. Evidence remains connected to its originating section and document version.
3. Entities have canonical identity within their type/name.
4. Claim correspondence connects specific versioned claims.
5. Policy changes retain the relationships needed to reconstruct the change.
6. Missing applicability information results in `UNKNOWN`.
7. Uncertain states should remain visible rather than becoming silent guesses.
8. HTTP routes should orchestrate application behavior rather than contain the domain model.

## AI Boundary

LLM-assisted extraction lives behind the domain/application layer.

The model can propose structured information, but the resulting data is validated and connected to evidence before it becomes part of the trusted knowledge representation.

This keeps probabilistic generation separate from authoritative persistence.

## Database Migrations

Schema changes are managed with Alembic.

After changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Migrations should be reviewed before applying them.

## Local Development

From the repository root:

```bash
source .venv/bin/activate
uvicorn src.main:app --reload
```

Run backend tests:

```bash
pytest -q
```

The API exposes automatically generated FastAPI documentation while the development server is running.
