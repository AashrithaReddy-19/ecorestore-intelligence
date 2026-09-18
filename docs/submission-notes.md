# Submission notes — EcoRestore Intelligence

## Repository

- **GitHub (public):** `<TO BE FILLED>`
- **Account used:** the GitHub CLI account already authenticated in the build environment.

## Live URLs

- **Frontend (Vercel):** `<TO BE FILLED>`
- **Backend (Render):** `<TO BE FILLED>`
- **API docs:** `<backend URL>/docs`

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

## Notes for reviewers

- The repository is **public**.
- Local review does not require any API key — `LLM_PROVIDER=none` (default) uses a
  deterministic, fully-grounded template fallback for narrative text, while the reasoning
  engine and RAG retrieval are always real (no mocked data).
- See `docs/demo-script.md` for a guided walkthrough and `README.md` for architecture,
  schema, and setup details.
