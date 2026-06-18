# AGENTS.md - back_sys (Backend)

## Quick Start

```bash
# Development
uvicorn main:app --reload          # http://localhost:8000
# Docs at http://localhost:8000/docs (Swagger) or /redoc

# Tests
pytest tests/ -v

# Deploy
./deploy.sh
```

## Stack

- **Framework**: FastAPI 0.122 (Python 3.11+)
- **Server**: Uvicorn 0.38
- **Database**: PostgreSQL 18 (db: `hospital`)
- **ORM**: SQLAlchemy 2.0 + psycopg2-binary
- **Auth**: JWT (python-jose HS256) + Argon2 (passlib)
- **Validation**: Pydantic 2.12
- **Email**: FastAPI-Mail (SMTP Gmail) + Jinja2 templates
- **Testing**: pytest 9 + FastAPI TestClient
- **Analytics**: pandas, matplotlib, numpy, plotly
- **Excel**: openpyxl
- **Package manager**: Poetry (primary) + pip

## Architecture: Modular Monolith

```
back_sys/
├── main.py                    # FastAPI app entry point
├── core/                      # Shared framework
│   ├── config.py              # Env vars (JWT, mail, DB)
│   ├── database.py            # SQLAlchemy engine + session
│   ├── security.py            # JWT creation/verify, Argon2 hash
│   ├── dependencies.py        # FastAPI DI re-exports
│   ├── exceptions.py          # Global error handlers (422, 409, 500)
│   └── mail.py                # FastAPI-Mail config
├── modules/                   # 24 domain modules
│   ├── auth/                  # POST /auth/login, GET /auth/me
│   ├── users/                 # Full user CRUD
│   ├── pacientes/             # Patient CRUD, duplicates (trigram/soundex), merge, neonates
│   ├── consultas/             # Medical consultations registry
│   ├── ciclos/                # Clinical cycles
│   ├── encamamiento/          # Bed census by service
│   ├── eventos/               # Clinical events (admission, evolution, discharge)
│   ├── medicos/               # Doctors CRUD
│   ├── citas/                 # Appointments
│   ├── expediente/            # Correlative number generation
│   ├── constancias_nacimiento/ # Birth certificates
│   ├── prestamos/             # Record/file loans
│   ├── procedimientos/        # Procedure catalog + records
│   ├── municipios/            # Guatemalan municipalities
│   ├── nacimientos/           # Birth records from madre-hijo
│   ├── paises_iso/            # ISO country codes
│   ├── renap/                 # RENAP civil registry integration
│   ├── totales/               # Real-time dashboard KPIs
│   ├── estadisticas/          # Statistics & reports
│   ├── audit_log/             # Access audit logging
│   ├── laboratorios/          # Lab tests (models only)
│   ├── rayos_x/               # X-rays (models only)
│   └── common/schemas.py      # Shared Pydantic schemas
├── app/                       # Legacy (being migrated to modules/)
│   ├── models/                # 18 legacy model files
│   ├── routes/                # 20 legacy route files
│   └── schemas/               # 19 legacy schema files
└── api-cie11/                 # ICD-11 medical coding data
```

## Module Convention

Each module in `modules/` contains:
- `router.py` → Route definitions
- `schemas.py` → Pydantic models
- `models.py` → SQLAlchemy ORM models
- `service.py` → Business logic

## API Overview

All routes under root path `/fah` (e.g., `https://host/fah/auth/login`).

| Module | Prefix | Key Endpoints |
|--------|--------|---------------|
| Health | `/health` | `GET /health` (DB check) |
| Auth | `/auth` | `POST /login`, `GET /me` |
| Users | `/users` | `GET/POST`, `GET/PUT /{id}`, `DELETE /{id}` |
| Patients | `/pacientes` | `GET/POST`, `GET/PATCH /{id}`, `/duplicados`, `/merge`, `/madre-hijo/{id}` (auto-crea constancia_nacimiento + nacimiento), `/neonatales` |
| Consultations | `/consultas` | `GET/POST`, `GET/PATCH /{id}`, `/registro`, `/pacienteId/{id}` |
| Doctors | `/medicos` | `GET/POST`, `GET/PUT/DELETE /{id}` |
| Encamamiento | `/encamamiento` | `GET/POST`, `GET/PATCH/DELETE /{id}`, filtros: `activo` |
| Appointments | `/citas` | `GET/POST`, `GET/PUT/DELETE /{id}`, `/disponibles` |
| Cycles | `/ciclos` | `GET/POST`, `GET /{id}` |
| Events | `/eventos` | `GET/POST`, `PATCH/DELETE /{id}` |
| Procedures | `/procedimientos` | `/catalogo` (con filtros `abreviatura`, `nombre`), `/catalogo/*`, `/estadisticas/*`, `GET/POST /{id}` |
| Correlatives | `/correlativos` | `POST /expediente`, `/emergencia`, `/constancia_nacimiento`, `/constancia_defuncion`, `/constancia_medica` |
| Birth Certs | `/constancias-nacimiento` | `GET/POST`, `GET /{id}` |
| Loans | `/prestamos` | `GET/POST`, `GET/PUT/DELETE /{id}` |
| Municipalities | `/municipios` | `GET /` (filtros: `q`, `codigo`, `municipio`, `departamento`, `vecindad`), `GET /departamentos` |
| Births | `/nacimientos` | `GET/POST`, `GET/PATCH/DELETE /{id}`, `/desde-paciente/{id}`, `/sincronizar` (unifica madre-hijo + legacy), `/referenciar-legacy` (cruza con `nacimientos_legacy`) |
| Countries | `/paises` | `GET /`, `GET /select` |
| RENAP | `/renap` | `GET /persona` |
| Totals | `/totales` | `GET /` |
| Statistics | `/estadisticas` | `/resumen`, `/consultas/por-dia`, `/por-especialidad`, `/pacientes/piramide`, `/procedimientos/top`, `/ocupacion`, `/reporte`, `/personal-salud` |
| Audit | `/audit-log` | `GET /` |

## Database

- **Name**: `hospital` (PostgreSQL)
- **Extensions**: `pg_trgm`, `unaccent`
- **Key tables**: `pacientes` (JSONB fields), `consultas`, `medicos`, `users`, `citas`, `ciclos_consulta`, `eventos_consulta`, `procedimientos`, `proce_medicos`, `constancia_nacimiento`, `prestamos`, `expediente_control`, `municipios`, `paises_iso`, `audit_log`, `laboratorios`, `rayos_x`, `encamamiento`, `nacimientos`, `nacimientos_legacy`
- **Indexes**: GIN on JSONB, partial unique indexes, trigram GIN on `nombre_completo`
- **Trigger**: `trg_set_nombre_completo` auto-generates full name from JSONB `nombre` before insert/update

## Auth Flow

1. `POST /auth/login` with username+password → returns JWT `access_token`
2. Token validated via `get_current_user` dependency on protected routes
3. Passwords hashed with **Argon2** (memory_cost=65536, time_cost=3, parallelism=4)
4. Token expiry: configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default 1440 min = 24h)

## Related Projects

- **hospital3** → Angular 20 PWA frontend (the main consumer of this API)
- **migration_api** → MySQL → PostgreSQL data migration scripts

## Key Config (`.env`)

```
POSTGRES_USER/PASSWORD/HOST/PORT/DB
SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES
MAIL_USERNAME/PASSWORD/FROM/SERVER/PORT
ENVIRONMENT
FRONTEND_URL
```
