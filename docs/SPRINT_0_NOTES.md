# Sprint 0 — Project Foundation

---

## Sprint Goal

Establish a clean, production-ready repository foundation so that all future sprints can begin writing application code immediately without debating project structure, tooling, or configuration.

---

## What Was Built

- **Project structure** — 9 top-level directories reflecting the system architecture
- **Backend scaffold** — Python 3.11 with pinned dependencies, `pyproject.toml` for tooling, config placeholder
- **Frontend scaffold** — React 18 + Vite 6 + TypeScript 5.6, ready for `npm install && npm run dev`
- **Docker Compose** — PostgreSQL 16, Redis 7, RabbitMQ 3.13 with named volumes and healthchecks
- **Environment management** — `.env.example` with all required service placeholders
- **Git hygiene** — `.gitignore` covering Python, Node, Docker, macOS, Windows, and IDE artifacts
- **Code quality** — `.editorconfig` for consistent formatting across all editors
- **Documentation** — README, architecture doc, roadmap, learning guide, and this sprint notes file
- **License** — MIT

---

## Why We Built It

Sprint 0 exists because **professional engineering teams never start coding in an empty repo.**

Without a foundation sprint:
- Developers waste time arguing about folder structure mid-feature
- Environment setup differs across machines, causing "works on my machine" bugs
- Docker configurations get created ad-hoc and conflict
- Dependencies drift because there's no central manifest
- Code quality is inconsistent without shared formatter/linter config

Sprint 0 eliminates these problems on day one.

---

## How It Works

### Folder Structure

The directory layout mirrors the system architecture:

| Folder          | Purpose                                                   | First Used |
|-----------------|-----------------------------------------------------------|------------|
| `backend/`      | FastAPI application — routes, models, services, config    | Sprint 1   |
| `frontend/`     | React dashboard — components, pages, API client           | Sprint 8   |
| `ml/`           | ML training scripts, evaluation, serialized models        | Sprint 2   |
| `data_pipeline/`| ETL and feature engineering scripts                       | Sprint 1   |
| `agent/`        | LangChain/LangGraph agent definitions                     | Sprint 6   |
| `workers/`      | Celery background task workers                            | Sprint 5   |
| `infra/`        | Dockerfiles, Terraform/CDK, CI/CD workflows               | Sprint 9   |
| `tests/`        | All test suites (unit, integration, e2e)                  | Sprint 1   |
| `docs/`         | Architecture docs, roadmap, learning materials            | Sprint 0   |

### Configuration Files (Root)

| File                | Purpose                                                    |
|---------------------|------------------------------------------------------------|
| `docker-compose.yml`| Defines local infrastructure services                     |
| `pyproject.toml`    | Centralizes Python tool config (ruff, mypy, pytest)       |
| `.env.example`      | Template for environment variables — never stores secrets |
| `.editorconfig`     | Cross-editor formatting rules (indent, charset, EOL)      |
| `.gitignore`        | Prevents committing build artifacts, secrets, IDE files   |
| `LICENSE`           | MIT license for the project                               |
| `README.md`         | Project overview and setup instructions                   |

---

## Important Engineering Decisions

### 1. `pyproject.toml` at root, not inside `backend/`

The `pyproject.toml` lives at the repository root because tools like `ruff`, `mypy`, and `pytest` are invoked from the root. Placing it inside `backend/` would require `cd backend` before every lint/test command, which breaks CI workflows and IDE integrations.

### 2. `requirements.txt` inside `backend/`, not at root

Dependencies are backend-specific. Keeping `requirements.txt` inside `backend/` makes it clear these are Python dependencies, not project-wide. This matters when the repo has multiple runtimes (Python + Node).

### 3. Version pinning with ranges, not exact pins

We use `>=X.Y,<Z.0` instead of `==X.Y.Z` because:
- Exact pins prevent security patches from being installed
- Ranges allow `pip install --upgrade` to pull patch fixes
- Upper bounds (`<Z.0`) protect against breaking major version changes

### 4. Docker Compose: no backend container

The backend runs directly on the host during development for faster iteration (no container rebuild on code changes). Only infrastructure services (database, cache, queue) run in containers.

### 5. `.gitkeep` files instead of empty directories

Git doesn't track empty directories. `.gitkeep` is a convention (not a Git feature) to ensure the directory structure exists after cloning.

### 6. Healthchecks on every Docker service

Healthchecks ensure `docker compose up` reports accurate service status and enable `depends_on` with `condition: service_healthy` in future sprints.

---

## Industry Best Practices

1. **Twelve-Factor App** — Environment config via `.env`, not hardcoded values
2. **Monorepo with clear boundaries** — One repo, but each module has its own dependency manifest
3. **Infrastructure as Code** — Docker Compose defines the local environment declaratively
4. **Fail-fast configuration** — `${VAR:?error}` syntax in Compose forces developers to set required vars
5. **Conventional Commits** — Structured commit messages for changelogs and CI automation
6. **EditorConfig** — Eliminates formatting debates before they start

---

## Common Mistakes

| Mistake                                        | Why It's Wrong                                           |
|------------------------------------------------|----------------------------------------------------------|
| Committing `.env` with real passwords           | Secrets leak into Git history permanently                |
| No `.gitignore` from day one                    | `node_modules/` or `__pycache__/` gets committed early   |
| Using `latest` tag in Docker images             | Builds break when upstream pushes breaking changes       |
| Putting all config in one `settings.py`         | Grows into an unmaintainable god-file                    |
| Skipping Docker healthchecks                    | Services report "running" before they're actually ready  |
| Exact version pins (`==`) for all packages      | Blocks security patches and creates merge conflicts      |
| Creating business logic in Sprint 0             | Foundation sprint should only create structure            |

---

## Interview Questions

**Q1: Why use Docker Compose for local development instead of installing PostgreSQL directly?**
Docker Compose guarantees every developer runs the identical database version with the same configuration. It eliminates "works on my machine" problems and makes onboarding a single `docker compose up` command.

**Q2: What is the purpose of `pyproject.toml`?**
It is the modern standard (PEP 621) for Python project metadata and tool configuration. It replaces scattered config files like `setup.cfg`, `tox.ini`, `.flake8`, and `mypy.ini` with a single source of truth.

**Q3: Why separate `requirements.txt` from `pyproject.toml`?**
`requirements.txt` declares installable dependencies. `pyproject.toml` configures development tools (linter rules, test paths). They serve different purposes. In larger projects, you might also have `requirements-dev.txt` for dev-only dependencies.

**Q4: What does `asyncpg` provide that `psycopg2` doesn't?**
`asyncpg` is a native async PostgreSQL driver. It integrates with Python's `asyncio` event loop, which is essential for FastAPI's async request handling. `psycopg2` is synchronous and would block the event loop.

**Q5: Why is there no backend container in `docker-compose.yml`?**
During development, running the backend on the host gives faster iteration — no need to rebuild a Docker image on every code change. The backend container is added in Sprint 9 for production deployment.

---

## Follow-Up Interview Questions

**Q6: How would you handle different configurations for development, staging, and production?**
Use environment-specific `.env` files (`.env.development`, `.env.staging`, `.env.production`) loaded by `pydantic-settings`. The `APP_ENV` variable selects the active configuration. Never commit non-example env files.

**Q7: What would you add to this foundation for a team of 10 developers?**
Pre-commit hooks (via `pre-commit`), branch protection rules, a `CONTRIBUTING.md`, PR templates, and a CI pipeline that runs linting + tests on every push.

**Q8: How do named Docker volumes differ from bind mounts?**
Named volumes are managed by Docker and persist across container restarts. Bind mounts map a host directory into the container. Named volumes are preferred for database data because they avoid filesystem permission issues across OS platforms.

**Q9: What is the risk of using `latest` as a Docker image tag?**
`latest` is a mutable tag — it points to whatever was most recently pushed. A `docker compose pull` could silently upgrade PostgreSQL from 16 to 17, breaking your schema migrations. Always pin to a specific major version.

**Q10: Why use `StrictMode` in the React entry point?**
`StrictMode` activates additional development-time checks: detecting unsafe lifecycle methods, unexpected side effects, and deprecated APIs. It renders components twice in development to surface impure renders. It has zero production overhead.

---

## Key Takeaways

1. **Sprint 0 is not optional** — it's the engineering equivalent of laying a foundation before building walls.
2. **Every file must have a clear purpose** — if you can't explain why a file exists, delete it.
3. **Tooling decisions compound** — the linter, formatter, and type checker you pick in Sprint 0 affect every sprint after.
4. **Environment management is a security concern** — `.env.example` is checked in; `.env` is not. Ever.
5. **Docker Compose is for development, not production** — production uses orchestrators like ECS or Kubernetes.
