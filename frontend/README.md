# Frontend

The `frontend/` directory contains the React and TypeScript interface for Trusted Information Intelligence.

The interface is designed around the same principle as the backend: **important regulatory conclusions should remain traceable to evidence.**

## Live Demo

The deployed application is available at:

https://trusted-information-intelligence.onrender.com/

## Frontend Architecture

```text
React + TypeScript
       ↓
Routing
       ↓
Pages / Feature Views
       ↓
Reusable UI Components
       ↓
Axios API Client
       ↓
FastAPI Backend
```

The frontend is a presentation and interaction layer. Regulatory reasoning remains in the backend.

## Main Routes

| Route | Purpose |
|---|---|
| `/` | Dashboard |
| `/changes` | Regulatory changes |
| `/changes/:id` | Detailed change investigation |
| `/documents` | Document library |
| `/documents/:id` | Document details |
| `/sources` | Regulatory sources |
| `/business-profile` | Business profile |
| `/review` | Human review workflow |
| `/settings` | Application settings |
| `/system-status` | Backend/system status |

## Core Screens

### Dashboard

Provides an overview of the regulatory intelligence available to the business user.

### Regulatory Changes

Lists detected changes so the user can move from a high-level alert to a specific regulatory requirement.

### Regulatory Change Detail

This is the central investigation view.

A useful change should be understandable through:

```text
What changed?
     ↓
Old requirement
     ↓
New requirement
     ↓
Evidence
     ↓
Why / context
     ↓
Applicability
     ↓
Business implication
```

### Documents

Provides access to the underlying regulatory documents.

### Document Detail

Connects document metadata and content back to the evidence used by the intelligence pipeline.

### Sources

Shows the institutions and source context behind regulatory documents.

### Business Profile

Represents the business context against which applicability conditions are evaluated.

### Review

Supports the human-in-the-loop principle for uncertain automated interpretations.

### System Status

Exposes operational health information so the user can distinguish an unavailable system from missing regulatory information.

## Evidence-Centered UI

The interface should avoid presenting AI-generated text as if it were an authoritative source.

The intended distinction is:

```text
SOURCE
  ↓
EVIDENCE
  ↓
STRUCTURED CLAIM
  ↓
DETECTED CHANGE
  ↓
BUSINESS INTERPRETATION
```

The user should be able to move back toward the source when a conclusion needs verification.

## API Integration

The frontend communicates with the FastAPI backend through HTTP requests.

Typical flow:

```text
User opens change
       ↓
Frontend requests policy-change detail
       ↓
FastAPI retrieves domain data
       ↓
Backend returns structured response
       ↓
Frontend renders change + evidence + applicability
```

The frontend should not duplicate backend comparison or applicability logic.

## Technology

- React 19
- TypeScript
- Vite
- Tailwind CSS
- Radix UI
- Wouter
- Axios
- Recharts
- Framer Motion

## Development

From the `frontend/` directory:

```bash
npm install
npm run dev
```

Type-check:

```bash
npm run check
```

Production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Project Structure

The frontend is organized around pages, reusable components, API integration, and shared types.

The Vite configuration uses aliases for the client source, shared code, and attached assets.

## Design Principles

1. **Evidence before explanation.**
2. **Show uncertainty rather than hide it.**
3. **Keep regulatory logic in the backend.**
4. **Make the path from change to source understandable.**
5. **Prefer clear information hierarchy over decorative complexity.**
6. **Treat human review as part of the workflow, not an exception.**

## Related Documentation

- `../README.md` — project overview
- `../src/api/README.md` — API contract
- `../src/services/README.md` — backend reasoning
- `../tests/README.md` — test suite
