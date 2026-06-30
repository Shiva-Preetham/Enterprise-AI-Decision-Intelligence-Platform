# Enterprise AI Customer Intelligence Platform

> An enterprise-grade AI-powered platform for real-time customer behavior analysis, predictive intelligence, and agentic AI-driven insights.

---

## Project Overview

This platform combines traditional ML, large language models, and agentic AI to deliver actionable customer intelligence at scale. It processes customer interaction data through feature engineering pipelines, serves predictions via REST APIs, and provides natural-language insights through a LangGraph-powered agent — all accessible from a React dashboard.

---

## High-Level Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│   React UI   │────▶│  FastAPI      │────▶│  PostgreSQL      │
│  (Dashboard) │     │  (REST API)   │     │  (Feature Store) │
└──────────────┘     └──────┬───────┘     └──────────────────┘
                            │
                    ┌───────┴────────┐
                    │                │
              ┌─────▼─────┐   ┌─────▼──────┐
              │   Redis    │   │  RabbitMQ   │
              │  (Cache)   │   │  (Queue)    │
              └────────────┘   └─────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   Workers    │
                              │  (Celery)    │
                              └──────┬──────┘
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                   ┌─────▼──────┐         ┌──────▼──────┐
                   │  ML Models │         │  LangGraph  │
                   │ (sklearn)  │         │   Agent     │
                   └────────────┘         └─────────────┘
```

---

## Tech Stack

| Layer           | Technology                       |
|-----------------|----------------------------------|
| Frontend        | React, Vite, TypeScript          |
| Backend API     | FastAPI, Pydantic, SQLAlchemy    |
| Database        | PostgreSQL 16                    |
| Cache           | Redis 7                          |
| Message Queue   | RabbitMQ 3.13                    |
| ML              | scikit-learn, pandas, NumPy      |
| LLM / Agent     | OpenAI, LangChain, LangGraph    |
| Containerization| Docker, Docker Compose           |
| Language        | Python 3.11, TypeScript 5.6      |

---

## Folder Structure

```
Enterprise-AI-Customer-Intelligence-Platform/
├── backend/            # FastAPI application, config, models, routes
├── frontend/           # React + Vite + TypeScript dashboard
├── ml/                 # ML training, evaluation, model artifacts
├── data_pipeline/      # ETL scripts, feature engineering
├── agent/              # LangChain / LangGraph agentic workflows
├── workers/            # Background task workers (Celery)
├── infra/              # Dockerfiles, IaC, CI/CD configs
├── tests/              # All test suites (unit, integration, e2e)
├── docs/               # Architecture docs, roadmap, learning guides
├── docker-compose.yml  # Local dev services (Postgres, Redis, RabbitMQ)
├── pyproject.toml      # Python tooling config (ruff, mypy, pytest)
├── .env.example        # Environment variable template
├── .editorconfig       # Cross-editor formatting rules
├── .gitignore          # Ignore rules for all project technologies
└── LICENSE             # MIT License
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 20+ & npm
- Docker & Docker Compose

### 1. Clone & configure environment

```bash
git clone https://github.com/Shiva-Preetham/Enterprise-AI-Customer-Intelligence-Platform.git
cd Enterprise-AI-Customer-Intelligence-Platform
cp .env.example .env
# Edit .env with your local values
```

### 2. Start infrastructure services

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, and RabbitMQ.

### 3. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

---

## Sprint Progress

| Sprint | Description                        | Status       |
|--------|------------------------------------|--------------|
| 0      | Project Foundation                 | ✅ Complete   |
| 1      | Database & Feature Store           | 🔲 Planned   |
| 2      | Feature Engineering + ML           | 🔲 Planned   |
| 3      | FastAPI                            | 🔲 Planned   |
| 4      | Redis Caching                      | 🔲 Planned   |
| 5      | RabbitMQ + Workers                 | 🔲 Planned   |
| 6      | LangChain + LangGraph              | 🔲 Planned   |
| 7      | RAG + Agentic AI                   | 🔲 Planned   |
| 8      | React Dashboard                    | 🔲 Planned   |
| 9      | Docker + AWS Deployment            | 🔲 Planned   |
| 10     | Monitoring + MLOps                 | 🔲 Planned   |

---

## High-Level Roadmap

**Phase 1 — Foundation (Sprint 0–1)**
Project structure, database schema, feature store.

**Phase 2 — Intelligence (Sprint 2–5)**
ML pipelines, FastAPI, caching, async task processing.

**Phase 3 — AI & Agents (Sprint 6–7)**
LLM integration, agentic RAG workflows.

**Phase 4 — Delivery (Sprint 8–10)**
Dashboard UI, containerized deployment, monitoring.

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
