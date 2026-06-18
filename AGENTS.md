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

## Full Endpoint Reference

All routes under root path `/fah`. Auth: `admin` = requires `get_current_admin_user`; `auth` = requires `get_current_user`; `public` = no auth.

| Module | Method | Path | Auth | Response | Description |
|--------|--------|------|------|----------|-------------|
| Health | GET | `/health` | public | `{"status","database"}` | Health check |
| Auth | POST | `/auth/login` | public | `TokenResponse` | Login |
| Auth | GET | `/auth/me` | auth | dict | Current user |
| Users | GET | `/users/` | admin | `UsersList` | List (filtros: username, id, email, rol) |
| Users | GET | `/users/{user_id}` | auth | `UserResponse` | By ID |
| Users | POST | `/users/` | admin | `UserCreate` | Create (envía email) |
| Users | PUT | `/users/{user_id}` | admin/self | `UserResponse` | Update |
| Users | PATCH | `/users/recuperar` | public | dict | Reset password |
| Users | DELETE | `/users/{user_id}` | admin | 204 | Soft delete |
| Pacientes | GET | `/pacientes/` | auth | `PacienteListResponse` | Search (15+ filtros: q, id, cui, expediente, nombre, sexo, estado, etc.) |
| Pacientes | GET | `/pacientes/neonatales` | auth | `PacienteListResponse` | Neonatales |
| Pacientes | GET | `/pacientes/{paciente_id}` | auth | `PacienteOut` | By ID |
| Pacientes | POST | `/pacientes/` | auth | `PacienteOut` (201) | Create |
| Pacientes | PATCH | `/pacientes/{paciente_id}` | auth | `PacienteOut\|dict` | Update/activar/desactivar/expediente |
| Pacientes | DELETE | `/pacientes/{paciente_id}/eliminar-permanente` | admin | 204 | Hard delete |
| Pacientes | GET | `/pacientes/debug/count` | auth | dict | Conteo |
| Pacientes | GET | `/pacientes/expediente/{expediente}` | auth | `PacienteContacto` | By expediente |
| Pacientes | GET | `/pacientes/duplicados/nombres-similares` | auth | dict | Trigram/soundex |
| Pacientes | POST | `/pacientes/merge` | admin | dict | Merge duplicados |
| Pacientes | POST | `/pacientes/madre-hijo/{madre_id}` | auth | `PacienteOut` (201) | Crear desde madre |
| Consultas | GET | `/consultas/` | auth | `ConsultaListResponse` | List (15+ filtros) |
| Consultas | GET | `/consultas/buscarpaciente` | auth | `List[PacienteSimple]` | Buscar pacientes |
| Consultas | GET | `/consultas/{consulta_id}` | auth | `ConsultaOut` | By ID |
| Consultas | PATCH | `/consultas/sincronizar-indicadores` | auth | dict | Sync indicadores |
| Consultas | PATCH | `/consultas/{consulta_id}` | auth | `ConsultaOut` | Update |
| Consultas | POST | `/consultas/registro` | auth | `RegistroConsultaOut` (201) | Nueva consulta |
| Consultas | GET | `/consultas/pacienteId/{paciente_id}` | auth | `List[ConsultaHistoriaResumidaOut]` | By patient |
| Consultas | DELETE | `/consultas/{consulta_id}` | auth | `ConsultaOut` | Desactivar |
| Consultas | DELETE | `/consultas/{consulta_id}/eliminar` | admin | dict | Hard delete |
| Ciclos | GET | `/ciclos/consulta/{consulta_id}` | auth | `List[CicloConsulta]` | By consulta |
| Ciclos | GET | `/ciclos/{ciclo_id}` | auth | `CicloOut` | By ID |
| Ciclos | POST | `/ciclos/` | auth | `CicloConsulta` (201) | Create |
| Citas | POST | `/citas/` | auth | `CitaResponse` (201) | Create |
| Citas | GET | `/citas/` | auth | `CitaListResponse` | List (filtros: id, expediente, paciente_id, especialidad, fecha_cita) |
| Citas | GET | `/citas/paciente/{paciente_id}` | auth | `List[CitaResponse]` | By patient |
| Citas | GET | `/citas/disponibles` | auth | `List[CitasPorFechaRazon]` | Disponibles |
| Citas | GET | `/citas/{cita_id}` | auth | `CitaResponse` | By ID |
| Citas | PUT | `/citas/{cita_id}` | auth | `CitaResponse` | Update |
| Citas | DELETE | `/citas/{cita_id}` | auth | dict | Soft delete |
| Medicos | POST | `/medicos/` | public | `MedicoOut` (201) | Create |
| Medicos | GET | `/medicos/` | public | `List[MedicoOut]` | List (filtros: id, activo, nombre, colegiado, especialidad) |
| Medicos | GET | `/medicos/{medico_id}` | public | `MedicoOut` | By ID |
| Medicos | PUT | `/medicos/{medico_id}` | public | `MedicoOut` | Update |
| Medicos | DELETE | `/medicos/{medico_id}` | public | 204 | Delete |
| Nac. Legacy | GET | `/nacimientos-legacy/` | auth | `List[NacimientoLegacyResponse]` | List (filtros: id, madre, doc, fecha) |
| Nac. Legacy | PUT | `/nacimientos-legacy/{id}` | auth | `NacimientoLegacyResponse` | Update |
| Const. Nac. | POST | `/constancias-nacimiento/` | auth | `ConstanciaNacimientoResponse` (201) | Create |
| Const. Nac. | GET | `/constancias-nacimiento/` | auth | `ConstanciaNacimientoListResponse` | List (6 filtros) |
| Const. Nac. | GET | `/constancias-nacimiento/historial/{constancia_id}` | auth | `list[...HistorialResponse]` | Historial |
| Const. Nac. | GET | `/constancias-nacimiento/{constancia_id}` | auth | `ConstanciaNacimientoResponse` | By ID |
| Const. Nac. | PUT | `/constancias-nacimiento/{constancia_id}` | auth | `ConstanciaNacimientoResponse` | Update (guarda historial) |
| Const. Nac. | DELETE | `/constancias-nacimiento/{constancia_id}` | admin | dict | Delete |
| Correlativos | POST | `/correlativos/expediente` | auth | dict (201) | EXP-YYYY-###### |
| Correlativos | POST | `/correlativos/emergencia` | auth | dict (201) | EMERG-###### |
| Correlativos | POST | `/correlativos/constancia_nacimiento` | auth | dict (201) | CN-###### |
| Correlativos | POST | `/correlativos/constancia_defuncion` | auth | dict (201) | DF-###### |
| Correlativos | POST | `/correlativos/constancia_medica` | auth | dict (201) | CM-###### |
| Municipios | GET | `/municipios/` | public | `MunicipioListResponse` | List (filtros: q, codigo, municipio, departamento, vecindad) |
| Municipios | POST | `/municipios/` | admin | `MunicipioSchema` (201) | Create |
| Municipios | PUT | `/municipios/{codigo}` | admin | `MunicipioSchema` | Update |
| Municipios | DELETE | `/municipios/{codigo}` | admin | 204 | Delete |
| Municipios | GET | `/municipios/departamentos` | public | `List[DepartamentoOut]` | Departamentos distinct |
| Paises | GET | `/paises/` | public | `List[PaisOut]` | All ISO countries |
| Paises | GET | `/paises/select` | public | `List[PaisSelect]` | For select/autocomplete |
| Paises | GET | `/paises/{codigo}` | public | `PaisOut` | By ISO code |
| RENAP | GET | `/renap/persona` | auth | `RespuestaRenap` | By CUI or names+dob |
| Totales | GET | `/totales/` | auth | `TotalesResponse` | Dashboard KPIs |
| Prestamos | POST | `/prestamos/` | auth | `PrestamoSchema` | Create |
| Prestamos | GET | `/prestamos/` | auth | `PrestamoListResponse` | List (6 filtros) |
| Prestamos | GET | `/prestamos/{prestamo_id}` | auth | `PrestamoSchema` | By ID |
| Prestamos | PUT | `/prestamos/{prestamo_id}` | auth | `PrestamoSchema` | Update (devuelve si fecha_devolucion) |
| Prestamos | DELETE | `/prestamos/{prestamo_id}` | auth | dict | Desactivar |
| Procedimientos | GET | `/procedimientos/catalogo` | auth | `list[ProcedimientoOut]` | Catálogo (filtros: abreviatura, nombre) |
| Procedimientos | GET | `/procedimientos/catalogo/{id}` | auth | `ProcedimientoOut` | Catálogo by ID |
| Procedimientos | POST | `/procedimientos/catalogo` | admin | `ProcedimientoOut` | Crear en catálogo |
| Procedimientos | PUT | `/procedimientos/catalogo/{id}` | admin | `ProcedimientoOut` | Update catálogo |
| Procedimientos | DELETE | `/procedimientos/catalogo/{id}` | admin | dict | Delete (si sin registros) |
| Procedimientos | GET | `/procedimientos/` | auth | `ProcedimientosListResponse` | List realizados (5 filtros) |
| Procedimientos | GET | `/procedimientos/reporte` | auth | dict | Reporte agregado |
| Procedimientos | GET | `/procedimientos/{id}` | auth | `ProceMedicoResponse` | Realizado by ID |
| Procedimientos | POST | `/procedimientos/` | auth | `ProceMedicoOut` (201) | Create realizado |
| Procedimientos | PUT | `/procedimientos/{id}` | auth | `ProceMedicoOut` | Update realizado |
| Procedimientos | DELETE | `/procedimientos/{id}` | admin | dict | Delete realizado |
| Procedimientos | GET | `/procedimientos/estadisticas/resumen` | auth | dict | Stats por año/mes |
| Eventos | GET | `/eventos/` | auth | `EventoConsultaList` | List (4 filtros) |
| Eventos | GET | `/eventos/{evento_id}` | auth | `EventoConsultaOut` | By ID |
| Eventos | POST | `/eventos/` | auth | `EventoConsultaOut` (201) | Create (ingreso/evolucion/egreso) |
| Eventos | PATCH | `/eventos/{evento_id}` | auth | `EventoConsultaOut` | Update |
| Eventos | DELETE | `/eventos/{evento_id}` | auth | 204 | Delete |
| Estadisticas | GET | `/estadisticas/resumen` | auth | `ResumenResponse` | Dashboard resumen |
| Estadisticas | GET | `/estadisticas/consultas/por-dia` | auth | `SerieResponse` | Por día en rango |
| Estadisticas | GET | `/estadisticas/consultas/por-especialidad` | auth | `SerieResponse` | Por especialidad |
| Estadisticas | GET | `/estadisticas/pacientes/piramide` | auth | `PiramidePoblacional` | Pirámide poblacional |
| Estadisticas | GET | `/estadisticas/procedimientos/top` | auth | `TopProcedimientos` | Top procedimientos |
| Estadisticas | GET | `/estadisticas/ocupacion` | auth | `OcupacionResponse` | Ocupación hospitalaria |
| Estadisticas | GET | `/estadisticas/reporte` | auth | `ReporteFechas` | Reporte personalizado |
| Estadisticas | GET | `/estadisticas/personal-salud` | auth | `PersonalSaludReporte` | Personal de salud |
| Audit | GET | `/audit-log/` | admin | dict (paginated) | Logs (filtros: tabla, username, desde, hasta) |
| Encamamiento | POST | `/encamamiento/` | public | `EncamamientoOut` (201) | Create servicio |
| Encamamiento | GET | `/encamamiento/` | public | `List[EncamamientoOut]` | List (filtro: activo) |
| Encamamiento | GET | `/encamamiento/{servicio_id}` | public | `EncamamientoOut` | By ID |
| Encamamiento | PATCH | `/encamamiento/{servicio_id}` | public | `EncamamientoOut` | Update |
| Encamamiento | DELETE | `/encamamiento/{servicio_id}` | public | 204 | Delete |
| Nacimientos | POST | `/nacimientos/` | auth | `NacimientoOut` (201) | Create |
| Nacimientos | POST | `/nacimientos/desde-paciente/{paciente_id}` | auth | `NacimientoOut` (201) | Desde paciente |
| Nacimientos | GET | `/nacimientos/` | auth | `NacimientoListResponse` | List (6 filtros) |
| Nacimientos | GET | `/nacimientos/{nacimiento_id}` | auth | `NacimientoOut` | By ID |
| Nacimientos | PATCH | `/nacimientos/{nacimiento_id}` | auth | `NacimientoOut` | Update |
| Nacimientos | DELETE | `/nacimientos/{nacimiento_id}` | auth | 204 | Delete |
| Nacimientos | POST | `/nacimientos/sincronizar` | auth | dict | Sincronizar madre-hijo + legacy |
| Nacimientos | GET | `/nacimientos/referenciar-legacy` | auth | `LegacyReferenceResponse` | Referenciar legacy |

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
