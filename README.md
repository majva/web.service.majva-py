# Majva Python FastAPI Template

A lean **FastAPI** web service template with **constructor DI**, **async PostgreSQL**, **Alembic migrations**, and a **GitLab CI/CD** pipeline.

Use this repository as a starting point for new backend services — not as a throwaway demo.

---

## Why this template

| Principle | How it's applied |
|-----------|------------------|
| **Clear layers** | Host → Application → Core → Infrastructure |
| **Convention over configuration** | `@inject` classes are auto-discovered — no manual DI registration |
| **Pragmatic CRUD** | `BaseRepository` + thin repos; add interfaces only when you need them |
| **Deployability** | Docker, migrations on startup, CI pipeline with validate → migrate → build |
| **Developer experience** | Auto-registered controllers, Swagger UI, typed DTOs with Pydantic |

---

## Architecture

```mermaid
flowchart TB
    subgraph Host["Host"]
        App["app.py"]
    end

    subgraph Application["Application"]
        Web["WebService"]
        Ctrl["Controllers"]
        DTO["DTOs"]
    end

    subgraph Core["Core"]
        Svc["Services"]
    end

    subgraph Infrastructure["Infrastructure"]
        Repo["Repositories"]
        Models["SQLAlchemy Models"]
        DB["PsqlDbContext"]
        Vault["VaultService"]
        Config["ConfigReader"]
        DI["bootstrap_di"]
    end

    App --> DI
    App --> Web
    Web --> Ctrl
    Ctrl --> Svc
    Svc --> Repo
    Repo --> Models
    Repo --> DB
    DB --> Config
    DB --> Vault
```

### Layer responsibilities

| Layer | Path | Responsibility |
|-------|------|----------------|
| **Host** | `src/host/` | Entry point, appsettings, Docker entrypoint |
| **Application** | `src/application/` | HTTP — controllers, DTOs, FastAPI wiring |
| **Core** | `src/core/` | Business logic — services (optional Keycloak helpers) |
| **Infrastructure** | `src/infrastructure/` | DB, models, Vault, repositories, DI, migrations |

### Request flow (example: create profile)

```
HTTP POST /api/v1/profile
  → ProfileController
    → ProfileService
      → ProfileRepository
        → PsqlDbContext → PostgreSQL
```

---

## Project structure

```
web.service.majva-py/
├── ci/
│   └── staging-ci.yml
├── docs/
│   └── CHANGELOG.md
├── .env.example
├── src/
│   ├── host/
│   │   ├── app.py              # Entry point
│   │   ├── entrypoint.sh       # Docker: migrate + start
│   │   └── res/
│   │       ├── appsettings.yaml
│   │       └── appsettings.development.yaml
│   ├── application/
│   │   ├── web.py              # FastAPI app + controller discovery
│   │   ├── health_check/
│   │   └── profile/
│   ├── core/
│   │   └── services/
│   │       ├── profile/
│   │       └── sso/            # Optional Keycloak Depends helpers
│   └── infrastructure/
│       ├── di/                 # @inject + bootstrap
│       ├── models/             # SQLAlchemy entities
│       ├── repositories/
│       ├── context/            # DB, Vault
│       ├── alembic/
│       └── scripts/
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

Edit `src/host/res/appsettings.development.yaml` (local) or `appsettings.yaml` (non-dev):

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

Settings live in `src/host/res/`. The app picks a file from `env_type` in the project-root `.env` file (copy from `.env.example` if needed):

```bash
env_type=development
```

| `env_type` | File loaded |
|------------|-------------|
| `development` (default if unset) | `./res/appsettings.development.yaml` |
| anything else | `./res/appsettings.yaml` |

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
| `env_type` | In `.env` — selects `appsettings.development.yaml` vs `appsettings.yaml` |
| `VAULT_TOKEN` / `vaulthc.VAULT_TOKEN` | Vault enabled |
| `POSTGRES_CONNECTION_STRING` | CI migrations & Docker entrypoint (overrides config when set) |
| `ENVIRONMENT` | Docker entrypoint migration guard |

---

## Dependency injection

Mark a class with `@inject` and type-hint constructor parameters. `bootstrap_di()` scans `infrastructure` → `core` → `application` once and registers providers.

```python
from src.infrastructure.di.inject import inject, resolve
from src.infrastructure.di.bootstrap import bootstrap_di

bootstrap_di()
service = resolve(ProfileService)
```

### Singletons

```python
@inject
class PsqlDbContext:
    __di_singleton__ = True

    def __init__(self, config_reader: ConfigReader, vault_service: VaultService):
        ...
```

### When to use `@inject`

| Component | `@inject`? |
|-----------|------------|
| Services | **Yes** |
| Repositories | **Yes** |
| Infrastructure (DB, Vault, Config) | **Yes** |
| Controllers with dependencies | **Yes** |
| Controllers with no dependencies | Optional |
| Models / DTOs | **No** |

---

## Developing a new feature

Follow the **Profile** example. To add a `Product` feature:

### Step 1 — Model

`src/infrastructure/models/product.py` — SQLAlchemy entity. Import it in `src/infrastructure/alembic/env.py` (same pattern as `profile`) so Alembic sees the metadata.

### Step 2 — Repository

```python
@inject
class ProductRepository(BaseRepository[Product]):

    def __init__(self, db_context: PsqlDbContext):
        super().__init__(db_context=db_context, model=Product)
```

Add a custom interface only when you have non-CRUD queries or a second implementation.

### Step 3 — Service

```python
@inject
class ProductService:

    def __init__(self, product_repository: ProductRepository):
        self._repository = product_repository
```

### Step 4 — DTOs + controller

`src/application/product/dtos/product_dto.py` and `product_controller.py`:

```python
@inject
class ProductController:

    def __init__(self, product_service: ProductService):
        self._service = product_service

    def api(self):
        router = APIRouter(tags=["Product"])
        # define routes...
        return router
```

Controllers are auto-registered when they follow:

```
src/application/{feature}/{feature}_controller.py
```

Routes mount at `/api/v1/{feature}`.

### Step 5 — Migration

```bash
python src/infrastructure/scripts/run_migrations.py --sync -m "add product table"
```

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

1. **Controllers stay thin** — validate input, call service, return DTO.
2. **Skip pass-through interfaces** — inject concrete repos/services until you need a second implementation.
3. **One migration per logical change** — always commit Alembic files to git.
4. **Use `@inject` on services and repos** — optional on controllers with no dependencies.
5. **Keep Vault disabled locally** — use `database.url` in appsettings for fast iteration.
6. **Follow naming conventions** — `*_service.py`, `*_repository.py`, `*_controller.py` so discovery picks them up.

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
| `Error loading configuration` | Run from `src/host` or ensure the matching `./res/appsettings*.yaml` exists relative to CWD |
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
