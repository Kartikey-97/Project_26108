# SIH 26108 — Backend

AI-Powered Procurement Intelligence Platform

## Developer ownership

| Folder | Owner | Responsibility |
|---|---|---|
| `kartikey/` | Kartikey | API, analysis pipeline, compliance reasoning, evidence assembly |
| `kshiraj/` | Kshiraj | Database, ingestion, retrieval, source adapters, utilities |
| `shared/` | Both | Domain models, contracts, config — agree before changing |

## Running the server

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your values
uvicorn kartikey.api.main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

## Environment variables

See `.env.example` for all required variables.

## API base URL

All endpoints are under `/api/v1/`
