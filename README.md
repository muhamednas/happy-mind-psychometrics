<h1 align="center">
  🧠 Happy Mind Psychometric Assessment Platform
</h1>

<p align="center">
  <strong>A modern, full-stack psychometric assessment platform for organizations to create, administer, and analyze psychological assessments.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
  <img src="https://img.shields.io/badge/SQLite-WAL_Mode-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Docker Setup](#docker-setup-optional)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Access Code System](#-access-code-system)
- [Report Engine](#-report-engine)
- [Chatbot](#-chatbot)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🌟 Overview

Happy Mind Psychometrics is an end-to-end assessment platform that enables organizations to:

1. **Create** assessment packages with multiple tests (MCQ, Likert scale, open-ended)
2. **Distribute** unique access codes (`HM-XXXX-X`) to candidates
3. **Administer** tests with real-time autosaving and progress tracking
4. **Analyze** results with automated PDF report generation
5. **Support** candidates with an integrated onboarding chatbot

---

## ✨ Features

### Admin Portal (`/admin`)
| Feature | Description |
|---------|-------------|
| 📦 **Package Builder** | Create assessment packages with multiple tests and question types |
| 🔑 **Code Generator** | Auto-generate unique `HM-XXXX-X` access codes |
| 📊 **Candidate Tracker** | Real-time dashboard showing candidate progress across all tests |
| 📄 **PDF Reports** | Generate professional branded PDF summary reports per candidate |
| 🔍 **Search & Filter** | Filter candidates by package, status, search by name/email |

### Candidate Portal (`/portal`)
| Feature | Description |
|---------|-------------|
| 🔐 **Code Login** | Secure login with access code + email |
| 🎯 **Test Dashboard** | Visual tile grid showing test statuses (Not Started / In Progress / Completed) |
| ✏️ **Test Runner** | Clean one-question-at-a-time interface with progress tracking |
| 💾 **Autosave** | Automatic 5-second debounced saving — never lose progress |
| 🤖 **Chatbot Support** | Integrated FAQ chatbot for onboarding assistance |

### Report Engine
| Feature | Description |
|---------|-------------|
| 📑 **PDF Generation** | WeasyPrint-powered HTML-to-PDF conversion |
| 🎨 **Professional Templates** | Branded Jinja2 HTML templates with print-optimized CSS |
| 📊 **Score Breakdowns** | Per-test scoring with visual progress indicators |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│         React + Vite + Tailwind CSS v4           │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │  Admin   │  │   Candidate  │  │  Chatbot  │  │
│  │  Portal  │  │    Portal    │  │  Widget   │  │
│  └────┬─────┘  └──────┬───────┘  └─────┬─────┘  │
│       │               │               │         │
└───────┼───────────────┼───────────────┼─────────┘
        │               │               │
        ▼               ▼               ▼
┌─────────────────────────────────────────────────┐
│              API Gateway (FastAPI)                │
│                                                  │
│  /api/v1/admin/*   /api/v1/candidate/*           │
│  /api/v1/reports/* /api/v1/chat/*                │
│                                                  │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐  │
│  │ Services │  │  Code Gen  │  │   Report    │  │
│  │  Layer   │  │  HM-XXXX-X │  │   Engine    │  │
│  └────┬─────┘  └────────────┘  │ (WeasyPrint)│  │
│       │                        └─────────────┘  │
└───────┼─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────┐
│             SQLite Database (WAL Mode)           │
│                                                  │
│  organizations ─┐                                │
│  packages ──────┤                                │
│  candidates ────┤                                │
│  candidate_progress ──┤                          │
│  candidate_responses ─┘                          │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
happy-mind-psychometrics/
├── README.md                          # This file
├── docker-compose.yml                 # Docker orchestration
│
├── backend/                           # Python FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app + lifespan
│   │   ├── config.py                  # Pydantic settings
│   │   ├── database.py                # SQLAlchemy async engine
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── organization.py
│   │   │   ├── package.py
│   │   │   ├── candidate.py
│   │   │   ├── candidate_progress.py
│   │   │   └── candidate_response.py
│   │   ├── schemas/                   # Pydantic request/response
│   │   │   ├── __init__.py
│   │   │   ├── organization.py
│   │   │   ├── package.py
│   │   │   ├── candidate.py
│   │   │   └── response.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py          # Aggregated API router
│   │   │       ├── admin.py           # Admin endpoints
│   │   │       ├── candidate.py       # Candidate endpoints
│   │   │       ├── reports.py         # PDF report endpoints
│   │   │       └── chat.py            # Chatbot endpoint
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── package_service.py     # Package CRUD
│   │   │   ├── candidate_service.py   # Candidate management
│   │   │   ├── code_generator.py      # HM-XXXX-X generator
│   │   │   └── report_service.py      # PDF generation
│   │   └── templates/
│   │       └── report.html            # Jinja2 PDF template
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Test fixtures
│       └── test_api.py                # API integration tests
│
└── frontend/                          # React Frontend
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── public/
    │   └── favicon.svg
    └── src/
        ├── main.jsx                   # React entry point
        ├── App.jsx                    # Router configuration
        ├── index.css                  # Tailwind v4 + design tokens
        ├── api/
        │   └── client.js             # API client wrapper
        ├── components/
        │   ├── Layout.jsx            # Admin sidebar layout
        │   ├── PortalLayout.jsx      # Candidate portal layout
        │   ├── Chatbot.jsx           # Floating chat widget
        │   └── ui/                   # Reusable UI primitives
        │       ├── Button.jsx
        │       ├── Card.jsx
        │       ├── Modal.jsx
        │       ├── Badge.jsx
        │       ├── Input.jsx
        │       └── StatusTile.jsx
        ├── pages/
        │   ├── admin/
        │   │   ├── Dashboard.jsx     # Overview + package list
        │   │   ├── PackageBuilder.jsx # Create assessment packages
        │   │   └── CandidateTracker.jsx # Track all candidates
        │   └── portal/
        │       ├── Login.jsx         # Access code + email login
        │       ├── TestDashboard.jsx  # Test status tiles
        │       └── TestRunner.jsx     # Autosaving test interface
        └── hooks/
            ├── useAutosave.js        # Debounced autosave hook
            └── useApi.js             # API state management hook
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.11+ ([python.org](https://www.python.org/downloads/))
- **Node.js** 18+ ([nodejs.org](https://nodejs.org/))
- **Git** ([git-scm.com](https://git-scm.com/))

> **Note for PDF Reports**: WeasyPrint requires GTK+3 system libraries.
> - **Linux/Docker**: `apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2`
> - **macOS**: `brew install pango gdk-pixbuf cairo libffi`
> - **Windows**: Install [GTK+3 Runtime](https://github.com/nickvdyck/gtk-runtime-installer/releases) and add to PATH, or use Docker/WSL2

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment file
cp .env.example .env
# Edit .env with your settings

# 6. Start the development server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000` (or `5173`).
API calls are automatically proxied to `http://localhost:8000`.

### Docker Setup (Optional)

```bash
# Start both services
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 📡 API Reference

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/admin/packages/create` | Create a new assessment package |
| `GET` | `/api/v1/admin/packages` | List all packages |
| `GET` | `/api/v1/admin/packages/{id}` | Get package with candidate stats |
| `GET` | `/api/v1/admin/candidates` | List all candidates (filter by `package_id`) |
| `GET` | `/api/v1/admin/candidates/{id}` | Get candidate with progress details |
| `GET` | `/api/v1/admin/candidates/{id}/report` | Download candidate PDF report |

### Candidate Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/candidate/login` | Login with access code + email |
| `GET` | `/api/v1/candidate/dashboard?candidate_id=...` | Get test statuses |
| `GET` | `/api/v1/candidate/test/{test_id}?candidate_id=...` | Get test questions |
| `POST` | `/api/v1/candidate/autosave` | Autosave a response |
| `POST` | `/api/v1/candidate/test/{test_id}/submit` | Submit completed test |

### Chat Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/message` | Send message to chatbot |

### Example: Create a Package

```bash
curl -X POST http://localhost:8000/api/v1/admin/packages/create \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Engineering Aptitude Assessment",
    "description": "Comprehensive cognitive and personality assessment",
    "tests": [
      {
        "id": "cognitive-1",
        "title": "Logical Reasoning",
        "description": "Pattern recognition and logical deduction",
        "time_limit_minutes": 30,
        "questions": [
          {
            "id": "q1",
            "text": "What comes next in the sequence: 2, 6, 12, 20, ?",
            "type": "mcq",
            "options": ["28", "30", "32", "26"],
            "correct_answer": "30"
          }
        ]
      }
    ]
  }'
```

**Response:**
```json
{
  "id": "a1b2c3d4-...",
  "title": "Engineering Aptitude Assessment",
  "access_code": "HM-A7K2-B",
  "is_active": true,
  "created_at": "2026-07-30T06:00:00Z"
}
```

---

## 🗄 Database Schema

```
┌──────────────────┐       ┌──────────────────────┐
│  organizations   │       │      packages         │
├──────────────────┤       ├──────────────────────┤
│ id (UUID PK)     │──┐    │ id (UUID PK)         │
│ name             │  │    │ organization_id (FK) │◄─┐
│ slug (unique)    │  └───►│ title                │  │
│ created_at       │       │ description          │  │
│ updated_at       │       │ tests (JSON)         │  │
└──────────────────┘       │ access_code (unique) │  │
                           │ is_active            │  │
                           │ created_at           │  │
                           └──────┬───────────────┘  │
                                  │                   │
                                  ▼                   │
                    ┌──────────────────────┐          │
                    │     candidates       │          │
                    ├──────────────────────┤          │
                    │ id (UUID PK)         │          │
                    │ package_id (FK)      │◄─────────┘
                    │ full_name            │
                    │ email                │
                    │ access_code          │
                    │ logged_in_at         │
                    │ created_at           │
                    └──────┬───────────────┘
                           │
              ┌────────────┼────────────────┐
              ▼                             ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  candidate_progress     │  │  candidate_responses    │
├─────────────────────────┤  ├─────────────────────────┤
│ id (UUID PK)            │  │ id (UUID PK)            │
│ candidate_id (FK)       │  │ candidate_id (FK)       │
│ test_id (str)           │  │ test_id (str)           │
│ status (enum)           │  │ question_id (str)       │
│ started_at              │  │ response (JSON)         │
│ completed_at            │  │ saved_at                │
│ score (float, nullable) │  └─────────────────────────┘
└─────────────────────────┘
```

**Status Enum Values**: `NOT_STARTED` | `IN_PROGRESS` | `COMPLETED`

---

## 🔑 Access Code System

Access codes follow the format **`HM-XXXX-X`**:

| Segment | Description | Example |
|---------|-------------|---------|
| `HM` | Fixed prefix (Happy Mind) | `HM` |
| `-` | Separator | `-` |
| `XXXX` | 4 random uppercase alphanumeric characters | `A7K2` |
| `-` | Separator | `-` |
| `X` | 1 check character for validation | `B` |

- Codes are **auto-generated** when creating a package
- Each code is **unique** across the entire system
- Candidates use the code + their email to log in

---

## 📄 Report Engine

The report engine generates professional PDF reports using:

1. **Jinja2 Templates** — HTML templates with dynamic data binding
2. **WeasyPrint** — HTML/CSS to PDF conversion with CSS Paged Media support

### Report Contents

- **Header**: Organization branding, candidate info, date
- **Summary**: Overall score and performance level
- **Per-Test Breakdown**: Individual test scores with visual indicators
- **Response Details**: Question-by-question analysis
- **Footer**: Page numbers, confidentiality notice

### Generating a Report

```bash
# Via API
curl -O http://localhost:8000/api/v1/admin/candidates/{id}/report

# Via Admin Dashboard
# Click "Download Report" button on any candidate row
```

---

## 🤖 Chatbot

The integrated chatbot provides **onboarding support** for candidates:

- **Getting started** — How to use the platform
- **Access codes** — What they are and where to find them
- **Test duration** — Expected time for each assessment
- **Technical help** — Common troubleshooting steps
- **Fallback** — Directs to organization admin for unsupported queries

The chatbot uses client-side keyword matching for instant responses, with an optional server-side fallback via `/api/v1/chat/message`.

---

## ⚙️ Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite+aiosqlite:///./happymind.db` |
| `SECRET_KEY` | Application secret key | (required) |
| `PROJECT_NAME` | Display name | `Happy Mind Psychometrics` |
| `DEBUG` | Debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000` |

### Frontend Configuration

The Vite dev server proxies `/api` requests to the backend. Configure the proxy target in `vite.config.js`.

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx
python -m pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set a strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` for your production domain
- [ ] Set `DEBUG=false`
- [ ] Consider migrating to PostgreSQL for production workloads
- [ ] Set up HTTPS/TLS
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Install WeasyPrint system dependencies on the server

### PostgreSQL Migration

To switch from SQLite to PostgreSQL, update:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/happymind
```

And add `asyncpg` to `requirements.txt`.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

<p align="center">
  Made with 💜 by Happy Mind Psychometrics
</p>
