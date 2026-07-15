# Majva Python FastAPI Template

A production-ready **FastAPI** web service template built with **Clean Architecture**, **reflection-based dependency injection**, **async PostgreSQL**, **Alembic migrations**, and a **GitLab CI/CD** pipeline.

Use this repository as a starting point for new backend services — not as a throwaway demo. The structure scales with your team and keeps business logic isolated from HTTP and infrastructure concerns.

---

## Why this template

| Principle | How it's applied |
|-----------|------------------|
| **Separation of concerns** | Four clear layers: Host → Application → Core → Infrastructure |
| **Dependency inversion** | Core depends on interfaces; infrastructure provides implementations |
| **Convention over configuration** | `@inject` classes are auto-discovered — no manual DI registration |
| **Deployability** | Docker, migrations on startup, CI pipeline with validate → migrate → build |
| **Developer experience** | Auto-registered controllers, Swagger UI, typed DTOs with Pydantic |

---

## Architecture

```mermaid
flowchart TB
    subgraph Host["Host Layer"]
        App["app.py"]
        HostCol["WebHostCollection"]
    end

    subgraph Application["Application Layer"]
        Web["WebService"]
        Ctrl["Controllers"]
        DTO["DTOs"]
    end

    subgraph Core["Core Layer"]
        Svc["Services"]
        ISvc["Service Interfaces"]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        Repo["Repositories"]
        DB["PsqlDbContext"]
        Vault["VaultService"]
        Config["ConfigReader"]
    end

    subgraph Domain["Domain Layer"]
        Models["SQLAlchemy Models"]
        Agg["Aggregations / Value Objects"]
    end

    App --> HostCol --> Web
    Web --> Ctrl
    Ctrl --> Svc
    Svc --> ISvc
    Svc --> Repo
    Repo --> Models
    Repo --> DB
    DB --> Vault
    Vault --> Config
```

### Layer responsibilities

| Layer | Path | Responsibility |
|-------|------|----------------|
| **Host** | `src/host/` | Application entry point, config files, Docker entrypoint |
| **Application** | `src/application/` | HTTP layer — controllers, DTOs, FastAPI wiring |
| **Core** | `src/core/` | Business logic — services and their interfaces |
| **Infrastructure** | `src/infrastructure/` | DB, Vault, repositories, migrations, logging |
| **Domain** | `src/domain/` | Entities and domain models (no framework imports in aggregations) |

### Request flow (example: create profile)

```
HTTP POST /api/v1/profile
  → ProfileController
    → ProfileService (core)
      → ProfileRepository (infrastructure)
        → PsqlDbContext → PostgreSQL
```

---

## Project structure

```
web.service.majva-py/
├── ci/
│   └── staging-ci.yml          # GitLab CI pipeline
├── docs/
│   └── CHANGELOG.md
├── src/
│   ├── host/
│   │   ├── app.py              # Entry point
│   │   ├── host_collection.py  # Host IoC
│   │   ├── entrypoint.sh       # Docker: migrate + start
│   │   └── res/
│   │       └── config.yaml     # Application configuration
│   ├── application/
│   │   ├── web.py              # FastAPI app + controller discovery
│   │   ├── application_collection.py
│   │   ├── health_check/       # Example: simple controller
│   │   └── profile/            # Example: full CRUD feature
│   │       ├── profile_controller.py
│   │       └── dtos/
│   ├── core/
│   │   ├── core_collection.py
│   │   └── services/
│   │       └── profile/
│   │           ├── iprofile_service.py
│   │           └── profile_service.py
│   ├── domain/
│   │   ├── models/             # SQLAlchemy entities
│   │   └── aggregations/       # Pydantic domain objects
│   └── infrastructure/
│       ├── infrastructure_collection.py
│       ├── di/                 # @inject + reflection engine
│       ├── repositories/
│       ├── context/            # DB, Vault, logging
│       ├── alembic/            # Database migrations
│       └── scripts/
│           └── run_migrations.py
├── Dockerfile
├── requirements.txt
└── .gitlab-ci.yml
```

---

## Quick start

### Prerequisites

- Python 3.11+
- PostgreSQL (local or remote)
- pip

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the app

Edit `src/host/res/config.yaml`:

```yaml
app:
  name: "My Service"
  version: "1.0.0.0"

server:
  host: "0.0.0.0"
  port: 5000

database:
  url: "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

vaulthc:
  enabled: false   # local dev — read secrets from config/env
```

### 3. Run migrations

From the project root:

```bash
python src/infrastructure/scripts/run_migrations.py --upgrade
```

Or generate + apply in one step during development:

```bash
python src/infrastructure/scripts/run_migrations.py --sync -m "describe your change"
```

### 4. Start the service

```bash
cd src/host
python app.py
```

### 5. Open API docs

| URL | Description |
|-----|-------------|
| http://localhost:5000/docs | Swagger UI |
| http://localhost:5000/api/v1/health_check/version | Health check |
| http://localhost:5000/api/v1/profile | Profile CRUD (example) |

---

## Configuration

All settings live in `src/host/res/config.yaml`. The app loads this file from `./res/config.yaml` relative to the working directory (`src/host` when running locally).

### Vault vs local secrets

| `vaulthc.enabled` | Behavior |
|-------------------|----------|
| `false` | No Vault connection. Database URL from `database.url` in config. Other secrets from environment variables. |
| `true` | Secrets loaded from HashiCorp Vault. Requires `vaulthc.VAULT_HOST`, `vaulthc.VAULT_TOKEN`, and `vaulthc.KV_NAMESPACE`. |

**Local development** — keep Vault disabled:

```yaml
vaulthc:
  enabled: false

database:
  url: "postgresql+asyncpg://user:pass@localhost:5432/mydb"
```

**Production** — enable Vault:

```yaml
vaulthc:
  enabled: true
  VAULT_HOST: "https://vault.your-company.com"
  KV_NAMESPACE: "secret"
  KV_VERSION: "1"
```

Set the Vault token via environment variable:

```bash
export VAULT_TOKEN="your-token"
```

### Environment variables

| Variable | When needed |
|----------|-------------|
| `VAULT_TOKEN` / `vaulthc.VAULT_TOKEN` | Vault enabled |
| `POSTGRES_CONNECTION_STRING` | CI migrations & Docker entrypoint (overrides config when set) |
| `ENVIRONMENT` | Docker entrypoint migration guard |

---

## Dependency injection

This template uses a **reflection-based IoC** system. Mark a class with `@inject` and declare dependencies as typed constructor parameters — the container resolves them automatically.

### How it works

Each layer has a collection that scans its own package tree:

```mermaid
flowchart LR
    Host["WebHostCollection"] --> App["ApplicationCollection"]
    App --> Core["CoreCollection"]
    Core --> Infra["InfrastructureCollection"]
```

| Collection | Auto-discovers |
|--------------|----------------|
| `InfrastructureCollection` | Everything under `src/infrastructure/` with `@inject` |
| `CoreCollection` | Everything under `src/core/` with `@inject` |
| `ApplicationCollection` | Everything under `src/application/` with `@inject` |
| `WebHostCollection` | Boots the full chain and starts `WebService` |

No manual registration. Add a file, add `@inject`, done.

### Singletons

Use `__di_singleton__ = True` for shared instances (DB context, config, Vault):

```python
@inject
class PsqlDbContext:
    __di_singleton__ = True

    def __init__(self, vault_service: VaultService, config_reader: ConfigReader):
        ...
```

### When to use `@inject`

| Component | `@inject`? |
|-----------|------------|
| Services | **Yes** |
| Repositories | **Yes** |
| Infrastructure (DB, Vault, Config) | **Yes** |
| Controllers with dependencies | **Yes** |
| Controllers with no dependencies | **No** |
| Domain models / DTOs | **No** |

### Resolve manually (when needed)

```python
from src.core.core_collection import CoreCollection
from src.core.services.profile.iprofile_service import IProfileService

service = CoreCollection.resolve(IProfileService)
```

---

## Developing a new feature

Follow the **Profile** example as a blueprint. To add a `Product` feature:

### Step 1 — Domain model

`src/domain/models/product/product.py`

```python
from sqlalchemy import Column, String
from src.infrastructure.context.sql_db.psql_dbcontext import Base

class Product(Base):
    __tablename__ = "product"

    id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=False)
```

Register it in `src/domain/models/__init__.py` for Alembic autogenerate.

### Step 2 — Repository interface + implementation

`src/infrastructure/repositories/product/iproduct_repository.py`

```python
from abc import ABC, abstractmethod
from src.infrastructure.repositories.base.ibase_repository import IBaseRepository

class IProductRepository(IBaseRepository, ABC):
    ...
```

`src/infrastructure/repositories/product/product_repository.py`

```python
from src.infrastructure.di import inject
from src.infrastructure.context.sql_db.psql_dbcontext import PsqlDbContext

@inject
class ProductRepository(BaseRepository[Product], IProductRepository):

    def __init__(self, db_context: PsqlDbContext):
        super().__init__(db_context=db_context, model=Product)
```

### Step 3 — Core service

`src/core/services/product/iproduct_service.py` — define the interface.

`src/core/services/product/product_service.py`:

```python
from src.infrastructure.di import inject

@inject
class ProductService(IProductService):

    def __init__(self, product_repository: IProductRepository):
        self._repository = product_repository
```

### Step 4 — DTOs + controller

`src/application/product/dtos/product_dto.py` — Pydantic request/response models.

`src/application/product/product_controller.py`:

```python
from src.infrastructure.di import inject

@inject
class ProductController:

    def __init__(self, product_service: IProductService):
        self._service = product_service

    def api(self):
        router = APIRouter(tags=["Product"])
        # define routes...
        return router
```

Controllers are **auto-registered** by `WebService` when they follow the convention:

```
src/application/{feature}/{feature}_controller.py
```

Routes are mounted at `/api/v1/{feature}`.

### Step 5 — Database migration

```bash
python src/infrastructure/scripts/run_migrations.py --sync -m "add product table"
```

Commit the generated file under `src/infrastructure/alembic/versions/`.

---

## Database & migrations

| Command | Purpose |
|---------|---------|
| `--upgrade` | Apply all pending migrations |
| `--autogenerate -m "msg"` | Generate migration from model changes |
| `--sync -m "msg"` | Generate + apply in one step |

Alembic reads the database URL from `POSTGRES_CONNECTION_STRING` (env) or `database.url` (config). Async URLs (`postgresql+asyncpg://`) are converted automatically for Alembic.

**Workflow:**

1. Change SQLAlchemy models
2. Run `--sync` locally and commit the migration file
3. CI applies `--upgrade` before building the Docker image
4. Docker entrypoint runs `--upgrade` again on container start

---

## CI/CD pipeline

```mermaid
flowchart LR
    subgraph MR["Merge Request"]
        V1["validate::mr"]
    end

    subgraph Main["main branch"]
        V2["validate::prod"] --> M["migrate::prod"] --> B["build::prod"]
    end
```

| Stage | MR pipeline | `main` pipeline |
|-------|-------------|-----------------|
| **validate** | Compile + pytest (if tests exist) | Same |
| **migrate** | Skipped | Applies Alembic migrations |
| **build** | Skipped | Builds & pushes Docker image |

### Required GitLab CI/CD variables

| Variable | Used by |
|----------|---------|
| `POSTGRES_CONNECTION_STRING` | `migrate::prod` |
| `CI_NEXUS_PROD_ADMIN_USERNAME` | `build::prod` |
| `CI_NEXUS_PROD_ADMIN_PASSWORD` | `build::prod` |

---

## Docker

```bash
docker build -t majva/python-template .
docker run -p 5000:5000 \
  -e POSTGRES_CONNECTION_STRING="postgresql+asyncpg://user:pass@host:5432/db" \
  majva/python-template
```

The entrypoint (`src/host/entrypoint.sh`) runs migrations before starting the app.

---

## API conventions

| Convention | Value |
|------------|-------|
| Base prefix | `/api/v1` |
| Controller route | `/api/v1/{feature}` |
| Swagger UI | `/docs` |
| Controller file | `src/application/{feature}/{feature}_controller.py` |
| Controller class | Must end with `Controller` and expose `api()` → `APIRouter` |

---

## Included examples

### Health Check

Simple controller with no dependencies.

```
GET /api/v1/health_check/version
```

### Profile (full CRUD)

Demonstrates the complete stack: model → repository → service → controller → migration.

| Method | Endpoint | Action |
|--------|----------|--------|
| `POST` | `/api/v1/profile/` | Create |
| `GET` | `/api/v1/profile/` | List all |
| `GET` | `/api/v1/profile/{id}` | Get by ID |
| `PUT` | `/api/v1/profile/{id}` | Update |
| `DELETE` | `/api/v1/profile/{id}` | Delete |

---

## Best practices

1. **Core never imports infrastructure** — only interfaces (`IProfileRepository`, not `ProfileRepository`).
2. **Controllers stay thin** — validate input, call service, return DTO. No business logic.
3. **One migration per logical change** — always commit Alembic files to git.
4. **Use `@inject` on services and repos** — skip it on controllers that have no dependencies.
5. **Keep Vault disabled locally** — use `database.url` in config for fast iteration.
6. **Follow naming conventions** — `*_service.py`, `*_repository.py`, `*_controller.py` so reflection picks them up.

---

## Tech stack

| Technology | Version | Role |
|------------|---------|------|
| FastAPI | 0.115+ | Web framework |
| Uvicorn | 0.34+ | ASGI server |
| SQLAlchemy | 2.0+ | Async ORM |
| Alembic | 1.15+ | Migrations |
| Pydantic | 2.11+ | Validation / DTOs |
| dependency-injector | 4.41+ | IoC container base |
| asyncpg | 0.30+ | PostgreSQL async driver |
| PyJWT + Keycloak | — | SSO / auth (scaffolded) |
| hvac | 2.1+ | HashiCorp Vault client |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Error loading configuration` | Run from `src/host` or ensure `./res/config.yaml` exists relative to CWD |
| Vault connection error on startup | Set `vaulthc.enabled: false` in config for local dev |
| Controller not registered | Check folder name matches file: `profile/profile_controller.py` |
| `No provider registered for X` | Add `@inject` to the implementation class |
| Migration fails in CI | Set `POSTGRES_CONNECTION_STRING` in GitLab CI/CD variables |
| Profile controller fails to load | Ensure `database.url` is set when Vault is disabled |

---

## License

Internal template — adjust licensing as needed for your organization.

---

Built with Clean Architecture principles for teams that want structure without ceremony.
