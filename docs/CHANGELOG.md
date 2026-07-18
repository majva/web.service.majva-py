# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

----------------------------------------------------------------------------------

## [1.1.1.5] - 2026-07-18

### Added
- Environment-based appsettings: `appsettings.yaml` and `appsettings.development.yaml`
- Project-root `.env` / `.env.example` with `env_type` to select which appsettings file loads
- `python-dotenv` for loading local environment configuration
- Single `bootstrap_di()` entry that discovers `@inject` providers under infrastructure, core, and application

### Changed
- Replaced `config.yaml` with the appsettings pair selected by `env_type`
- Collapsed Host / Application / Core / Infrastructure DI collections into one bootstrap scan
- Slimmed Profile feature to concrete `ProfileService` and `ProfileRepository` (no pass-through interfaces)
- Moved SQLAlchemy entities to `src/infrastructure/models/` (removed fake domain models layer)
- `PsqlDbContext` creates a shared async engine and session factory once (no engine-per-request)
- `ConfigReader` resolves config from package path, fails fast when the file is missing
- Keycloak SSO helpers initialize lazily after DI bootstrap (no import-time Vault/Keycloak setup)
- Host entry (`app.py`) bootstraps DI and resolves `WebService` directly
- README updated for the lean architecture and feature workflow
- Removed package `__init__.py` files; imports target concrete modules (e.g. `di.inject`)

### Removed
- `dependency_injector` and all `*_collection.py` IoC wrappers
- Per-entity CRUD interfaces (`IProfileService`, `IProfileRepository`, `IBaseRepository`)
- Unused template surface: Account model, broken log/ELK stack, SSO STOs, unused HTTP exception decorator
- `src/domain/` layer

### Fixed
- Database URL resolution for local migrations when Vault is disabled (`database.url` in appsettings)
- Async PostgreSQL URL normalization (`postgresql://` → `postgresql+asyncpg://`)

### Dependencies
- Added `python-dotenv==1.1.0`
- Removed `dependency_injector==4.41.0`

----------------------------------------------------------------------------------

## [1.0.0.0] - 2025-06-02

### Added
- Initial release of the Jupiter Service
- Core authentication service with JWT token support
- Health check endpoint for service monitoring
- FastAPI-based REST API with proper documentation
- Swagger UI integration for API documentation
- Dependency injection using dependency_injector
- Controller-based architecture for better organization
- CORS middleware for cross-origin requests
- Docker support with Dockerfile and docker-compose
- GitLab CI/CD pipeline for automated deployment
- Comprehensive API documentation with examples
- Type hints and Pydantic models for request/response validation

### Changed
- Improved API route organization using APIRouter instead of mount
- Enhanced Swagger UI documentation with proper tags and grouping
- Updated controller structure for better maintainability
- Refactored authentication flow for better security
- Optimized Docker image size and build process

### Fixed
- Resolved "Failed to load API definition" error in Swagger UI
- Fixed route registration to properly integrate with FastAPI's OpenAPI schema
- Corrected authentication response format
- Addressed CORS configuration for production environments

### Security
- Implemented JWT-based authentication
- Added proper error handling for authentication failures
- Secured sensitive endpoints with authentication middleware
- Added security headers and CORS configuration

### Documentation
- Added comprehensive API documentation with Swagger UI
- Included request/response examples for all endpoints
- Documented authentication flow and requirements
- Added inline code documentation and type hints

### Dependencies
- FastAPI 0.95.1 for the web framework
- Uvicorn 0.21.1 for the ASGI server
- PyJWT 2.6.0 for JWT token handling
- Pydantic 1.10.7 for data validation
- Dependency Injector 4.41.0 for IoC container
- Other supporting libraries as specified in requirements.txt 