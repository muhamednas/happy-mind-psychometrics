# AGENTS.md

## Cursor Cloud specific instructions

This repo is a single full-stack product, **Happy Mind Psychometric Assessment Platform**, split into two services:

- `backend/` — Python 3.12 / FastAPI + Uvicorn, SQLAlchemy async on SQLite (WAL). DB file and tables are auto-created on startup (no migration step, no separate DB server). PDF reports use WeasyPrint (needs GTK/Pango/Cairo system libs, already present in the environment snapshot).
- `frontend/` — React 18 + Vite 8 + Tailwind v4 SPA (Admin portal `/admin`, Candidate portal `/portal`, chatbot widget).

Standard commands live in `README.md` (Getting Started / Testing) and `frontend/package.json` scripts. Notes below are only the non-obvious cloud gotchas.

### Running the services

- Backend (dev): from `backend/`, run `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`. Health check: `GET /health`; interactive docs at `/docs`.
- Frontend (dev): from `frontend/`, run `npm run dev`. Vite serves on **port 5173** (not 3000; `vite.config.js` sets no port, so Vite's default is used). The README's "3000" refers to the Docker Compose mapping only.
- The frontend dev server binds to `localhost`. Use `http://localhost:5173` (curling the literal `127.0.0.1:5173` can be refused); the Vite proxy forwards `/api` → `http://127.0.0.1:8000`, so the backend must be running for the UI to load data.

### Non-obvious gotchas

- **Frontend install requires `--legacy-peer-deps`.** `@vitejs/plugin-react` declares a peer range that stops at Vite 7, but the project pins Vite 8, so plain `npm install`/`npm ci` fail with `ERESOLVE`. Use `npm ci --legacy-peer-deps` (works with the committed lockfile). It runs fine with Vite 8 in practice.
- **Backend Python deps install to the user site** (`~/.local/bin`, via `pip install --break-system-packages`, no venv). `~/.local/bin` is added to PATH in `~/.bashrc`, but the most robust way to invoke tools is `python3 -m uvicorn` / `python3 -m pytest`.
- **Backend config has working defaults** (`app/config.py`), including CORS for ports 3000 and 5173, so `backend/.env` is optional. `.env` and `*.db` are gitignored.
- **No frontend test runner is configured** — `npm test` (mentioned in README) is not defined in `package.json`; only `npm run lint` (ESLint) exists for the frontend.

### Lint / test / build / run summary

| Service | Lint | Test | Build | Run (dev) |
|---|---|---|---|---|
| backend | (none configured) | `python3 -m pytest tests/ -v` | (none; runtime service) | `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` |
| frontend | `npm run lint` | (none configured) | `npm run build` | `npm run dev` (serves on :5173) |
