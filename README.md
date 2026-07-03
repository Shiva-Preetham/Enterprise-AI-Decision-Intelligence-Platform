# Enterprise AI Customer Intelligence Platform

> Enterprise-grade AI platform for customer intelligence, churn prediction, explainable AI, and agentic decision support.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![React](https://img.shields.io/badge/React-18-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# Project Overview

The Enterprise AI Customer Intelligence Platform is an end-to-end enterprise analytics platform designed for internal business, marketing, and risk teams.

It combines traditional Machine Learning, Explainable AI, and Agentic AI into a single production-style application capable of:

- Customer Segmentation (RFM)
- Customer Lifetime Value Prediction
- Churn Prediction using XGBoost
- SHAP Explainability
- Next Best Action Recommendation
- AI-powered Business Assistant using LangGraph + RAG
- Interactive Analytics Dashboard
- Model Monitoring & Drift Detection

---

# Why This Project?

Most churn prediction projects stop after training a machine learning model.

Real enterprise systems require much more.

This project demonstrates how predictive models are integrated into scalable software systems with feature engineering pipelines, model serving APIs, caching, asynchronous workers, explainability, agentic AI, and production deployment.

The goal is to simulate how customer intelligence platforms are built inside organizations such as:

- American Express
- JPMorgan Chase
- Citi
- Fractal Analytics
- EXL
- ZS Associates

while also showcasing software engineering skills expected at companies like:

- Google
- Amazon
- Microsoft
- LinkedIn
- Zomato

---

# Key Features

### Data Engineering

- Customer & Transaction Data Ingestion
- Feature Engineering Pipeline
- PySpark Batch Processing
- Feature Store

### Machine Learning

- RFM Segmentation
- Customer Lifetime Value Prediction
- Churn Prediction (XGBoost)
- SHAP Explainability
- Model Evaluation
- Drift Detection

### Recommendation Engine

- Next Best Action Prediction
- A/B Testing Framework

### Backend

- FastAPI
- PostgreSQL
- Redis
- RabbitMQ
- JWT Authentication

### Agentic AI

- LangChain
- LangGraph
- Tool Calling
- Retrieval Augmented Generation (RAG)
- Conversation Memory

### Frontend

- React
- TypeScript
- Explainability Dashboard
- Analytics Dashboard
- AI Chat Assistant

### Deployment

- Docker
- AWS
- Logging
- Monitoring
- CI/CD

---

# High-Level Architecture

```text
React Dashboard
       │
       ▼
FastAPI Backend
       │
 ┌─────┴─────────────┐
 │                   │
 ▼                   ▼
PostgreSQL        Redis
 │
 ▼
RabbitMQ
 │
 ▼
Workers
 │
 ▼
ML Models (XGBoost)
 │
 ▼
SHAP Explainability
 │
 ▼
LangGraph Agent
 │
 ▼
RAG Knowledge Base
```

---

# Technology Stack

| Layer | Technologies |
|---------|----------------------------|
| Frontend | React, Vite, TypeScript |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Cache | Redis |
| Queue | RabbitMQ |
| ML | XGBoost, SHAP, scikit-learn |
| AI | LangChain, LangGraph, OpenAI |
| Vector DB | pgvector |
| Data Engineering | PySpark |
| Deployment | Docker, AWS |

---

# Folder Structure

```text
backend/
frontend/
ml/
data_pipeline/
agent/
workers/
infra/
tests/
docs/
```

---

# Local Setup

```bash
git clone https://github.com/Shiva-Preetham/Enterprise-AI-Customer-Intelligence-Platform

cd Enterprise-AI-Customer-Intelligence-Platform

cp .env.example .env

docker compose up -d
```

Backend

```bash
cd backend

python -m venv .venv

pip install -r requirements.txt
```

Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# Sprint Progress

| Sprint | Status |
|---------|--------|
| Sprint 0 | ✅ Completed |
| Sprint 1 | ✅ Database Foundation |
| Sprint 2 | ✅ Feature Store |
| Sprint 3 | ✅ ML Pipeline |
| Sprint 4 | ⏳ FastAPI |
| Sprint 5 | ⏳ Redis |
| Sprint 6 | ⏳ RabbitMQ |
| Sprint 7 | ⏳ LangGraph |
| Sprint 8 | ⏳ RAG |
| Sprint 9 | ⏳ React Dashboard |
| Sprint 10 | ⏳ AWS Deployment |

---

# Documentation

Detailed architecture documentation is available inside the `docs/` directory.

- ARCHITECTURE.md
- ROADMAP.md
- LEARNING_GUIDE.md
- SPRINT_0_NOTES.md
- SPRINT_1_NOTES.md
- SPRINT_2_NOTES.md
- SPRINT_3_NOTES.md
- INTERVIEW_GUIDE.md

Future documentation will include:

- Database Design
- API Specification
- ML Pipeline
- Agent Architecture
- Deployment Guide
- Security Guide

---

# Roadmap

**Phase 1 — Foundation**

- Project Setup
- Database
- Feature Store

**Phase 2 — Intelligence**

- Machine Learning
- Explainability
- FastAPI
- Redis
- RabbitMQ

**Phase 3 — Agentic AI**

- LangGraph
- RAG
- Tool Calling

**Phase 4 — Production**

- React Dashboard
- Docker
- AWS
- Monitoring
- MLOps

---

# License

Licensed under the MIT License.
