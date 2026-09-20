# Submission notes — EcoRestore Intelligence

## Repository

- **GitHub (public):** https://github.com/AashrithaReddy-19/ecorestore-intelligence
- **Account used:** the GitHub CLI account already authenticated in the build environment
  (`AashrithaReddy-19`).

## Live URLs

- **Frontend (Vercel):** https://ecorestore-intelligence.vercel.app — **verified live** (HTTP 200).
- **Backend (Render):** not yet deployed — no Render account credentials (API key / logged-in
  CLI session) were available in the automated build environment to provision it. The service
  is fully deploy-ready: `backend/Dockerfile` builds and runs correctly, and `render.yaml` at
  the repo root lets Render provision the web service + PostgreSQL database automatically via
  **Dashboard → New → Blueprint → select this repo**. See README section 10 for the exact
  remaining steps (deploy, then point `VITE_API_BASE_URL` at the new URL and redeploy Vercel).
- **API docs:** `<backend URL>/docs` once the above step is done.

Everything the backend needs to run correctly has been verified **locally** instead:
health check, the full Sundarbans assessment end-to-end (evidence-cited ranked
recommendations), the clarifying-question chat flow, and `docker compose up --build` (see
"Final verification results" below).

## Deployment configuration

### Frontend — Vercel

Deployed from `frontend/` as the project root (Vite framework preset).

Environment variable:
```
VITE_API_BASE_URL=<backend URL>
```

### Backend — Render (Docker web service)

Deployed using `backend/Dockerfile` with build context at the repository root (so it can copy
`knowledge_base/`).

Environment variables:
```
DATABASE_URL=<Render/Supabase PostgreSQL connection string>
OPENAI_API_KEY=            # optional; leave blank to use the deterministic fallback
LLM_PROVIDER=none          # or "openai" if OPENAI_API_KEY is set
CORS_ORIGINS=<frontend URL>
CHROMA_PERSIST_DIRECTORY=/app/knowledge_base/chroma_store
```

A `render.yaml` Blueprint is included at the repository root for one-click provisioning via
Render's "New Blueprint" flow. The backend auto-ingests the knowledge base into Chroma and the
relational DB on first startup (`app/main.py::on_startup`), so no manual seeding step is
required after deploy.

### Database

Render PostgreSQL (or Supabase PostgreSQL as a fallback) — see `render.yaml`.

### Vector storage

ChromaDB persists to `CHROMA_PERSIST_DIRECTORY`. On Render's free tier, disk is ephemeral
across deploys, so the knowledge base is re-ingested automatically from the versioned
`knowledge_base/seed_sources/` records on every cold start — this is why ingestion is wired
into the FastAPI startup event rather than assumed to be a one-time manual step.

## Post-deployment verification checklist

- [ ] `GET <backend URL>/api/health` returns `"status": "ok"`.
- [ ] Frontend loads and successfully calls the deployed backend (no CORS errors).
- [ ] The Sundarbans sample scenario runs end-to-end from Assessment → Recovery Plan.
- [ ] Evidence citations are visible and link to real FAO/IPCC/UNEP/CBD/IUCN pages.
- [ ] `<backend URL>/docs` renders the FastAPI interactive documentation.

## Demo credentials

None. The application requires no login; all endpoints are open for the purposes of this
hackathon submission.

## Final verification results

All of the below were run and observed directly in the build environment (not assumed):

- **Backend tests:** `pytest -v` in `backend/` → **38 passed, 0 failed**.
- **Frontend tests:** `npm test` in `frontend/` → **15 passed, 0 failed** (3 test files).
- **Frontend production build:** `npm run build` → succeeds (`tsc -b && vite build`), output
  ~348 kB JS / ~30 kB CSS.
- **Backend health check (local):** `GET /api/health` → `{"status":"ok","database_ok":true,
  "vector_store_ok":true,"evidence_chunks_indexed":34,...}`.
- **Backend `/docs` (local):** returns HTTP 200 (FastAPI Swagger UI).
- **Sundarbans sample end-to-end (local):** `POST /api/assessments` with the exact flagship
  JSON → `biodiversity_risk_level: "critical"`, `confidence: 0.9`, 14 variables considered, 5
  rules activated (R2, R3, R3b, R6, R7), 7 ranked recommendations, every recommendation citing
  2–3 real FAO/IPCC/UNEP/CBD/IUCN sources with clickable URLs and relevance scores, and the
  mandated "no numeric estimate" disclosure on every recommendation — no invented sources or
  statistics (enforced by `tests/test_citations.py` and manually spot-checked).
- **Clarifying-question flow (local):** `POST /api/chat` with `"Biodiversity is declining on
  my land."` → returns exactly 3 focused follow-up questions (land-use/ecosystem type, soil
  condition, rainfall/water availability) and `assessment: null`, matching the required
  response style.
- **Docker Compose:** `docker compose -p ecorestore-intelligence up --build -d` succeeded —
  all three containers (`db`, `backend`, `frontend`) reached a healthy/running state. Verified
  against the running stack: `GET /api/health` → `{"status":"ok","database_ok":true,
  "vector_store_ok":true,"evidence_chunks_indexed":34,"environment":"docker"}`; `/docs` → HTTP
  200; `/api/evidence/search?q=mangrove restoration` returned real cited results; the full
  Sundarbans assessment returned the same `critical`/5-rules/7-recommendations result as the
  local run; the clarifying-question chat flow returned the same 3 focused questions. Run with
  host-port overrides (`DB_HOST_PORT`/`BACKEND_HOST_PORT`/`FRONTEND_HOST_PORT` in a local,
  git-ignored `.env`) to avoid colliding with other projects already running on the build
  machine — the checked-in `docker-compose.yml` defaults to the standard 5432/8000/5173 ports
  when those variables are unset.
- **Evidence source audit:** all 17 `knowledge_base/seed_sources/*.json` records were checked
  individually — organization, title, and URL verified live (HTTP 200, with actual page
  content matching the paraphrased claim rather than a soft-redirect to a generic landing
  page). 9 records had a stale or moved URL (mostly FAO/UNEP/IUCN site restructuring) and were
  corrected to a verified current page from the same organization, with `title`/`year`
  updated to match and `claim`/`evidence_text` re-paraphrased to accurately reflect that
  page's actual content; `year` was set to `null` where a page has no stated publication date
  rather than asserting an unverifiable one. No record asserts a specific numeric improvement
  estimate.
- **GitHub:** repository created and all commits pushed to `main` at
  https://github.com/AashrithaReddy-19/ecorestore-intelligence.

## Notes for reviewers

- The repository is **public**.
- Local review does not require any API key — `LLM_PROVIDER=none` (default) uses a
  deterministic, fully-grounded template fallback for narrative text, while the reasoning
  engine and RAG retrieval are always real (no mocked data).
- See `docs/demo-script.md` for a guided walkthrough and `README.md` for architecture,
  schema, and setup details.
