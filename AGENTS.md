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
├── modules/                   # 25 domain modules
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
│   ├── sigsa3/                # SIGSA-3 consultation registry
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
| Births | `/nacimientos` | `GET/POST`, `GET/PATCH/DELETE /{id}`, `/desde-paciente/{id}`, `/sincronizar` (unifica madre-hijo + legacy), `/referenciar-legacy` (cruza con `nacimientos_legacy`). **Sin datos redundantes:** expediente, sexo, fecha_nac, neonatales se obtienen vía JOIN con `pacientes`. Columnas computadas: `peso_gramos`, `clasificacion_nacimiento` (EBP/MBP/BP/PN), `trabajo_parto` (Prematuro/a Termino/Prolongado) |
| Countries | `/paises` | `GET /`, `GET /select` |
| RENAP | `/renap` | `GET /persona` |
| Statistics | `/estadisticas` | `/consultas/pacientesAtendidos`, `/consultas/hospitalizacion-infantil`, `/consultas/promedioDiario`, `/consultas/personal-hospital`, `/consultas/estudiante-publico`, `/consultas/reingresos`, `/consultas/reingresos-tipo3`, `/consultas/activos-mayores-a-30-dias`, `/nacimientos` |
| SIGSA-3 | `/sigsa3` | `GET/POST`, `GET/PUT/DELETE /{id}`, filtros: personal_salud, fecha, nombre, sexo, tipo_consulta, especialidad, cie10, q |
| Totales | `/totales` | `GET /` (KPIs dashboard, 7 indicadores, opcional `fecha`) |
| Audit | `/audit-log` | `GET /` |

## Database

- **Name**: `hospital` (PostgreSQL)
- **Extensions**: `pg_trgm`, `unaccent`
- **Key tables**: `pacientes` (JSONB fields), `consultas`, `medicos`, `users`, `citas`, `ciclos_consulta`, `eventos_consulta`, `procedimientos`, `proce_medicos`, `constancia_nacimiento`, `prestamos`, `expediente_control`, `municipios`, `paises_iso`, `audit_log`, `laboratorios`, `rayos_x`, `encamamiento`, `nacimientos` (sin datos redundantes — solo `id`, `paciente_id`, `madre_id`, `registrador_id`, `peso_gramos`, `clasificacion_nacimiento`, `trabajo_parto`, timestamps), `nacimientos_legacy`, `sigsa3`
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
| Estadisticas | GET | `/estadisticas/consultas/pacientesAtendidos` | auth | `PacientesAtendidosResponse` | Pacientes atendidos por tipo, especialidad y sexo (req: `desde`, `hasta`) |
| Estadisticas | GET | `/estadisticas/consultas/hospitalizacion-infantil` | auth | `HospitalizacionInfantilResponse` | Hospitalizaciones infantiles >28d y <5años (req: `desde`, `hasta`) |
| Estadisticas | GET | `/estadisticas/consultas/promedioDiario` | auth | `PromedioDiarioResponse` | Promedio diario de consultas por especialidad (req: `desde`, `hasta`) |
| Estadisticas | GET | `/estadisticas/consultas/personal-hospital` | auth | `PersonalHospitalResponse` | Consultas de personal del hospital (filtro `datos_extra.socioeconomicos.personal_hospital=S`, req: `desde`, `hasta`) |
| Estadisticas | GET | `/estadisticas/consultas/estudiante-publico` | auth | `EstudiantePublicoResponse` | Consultas de estudiantes públicos (filtro `datos_extra.socioeconomicos.estudiante_publico=S`, req: `desde`, `hasta`) |
| Estadisticas | GET | `/estadisticas/consultas/reingresos` | auth | `ReingresoResponse` | Reingresos hospitalarios clasificados (<8d / complicaciones). req: `desde`, `hasta` |
| Estadisticas | GET | `/estadisticas/consultas/reingresos-tipo3` | auth | `ConsultaListResponse` | Reingresos tipo 3 paginados (filtros: `skip`, `limit`) |
| Estadisticas | GET | `/estadisticas/consultas/activos-mayores-a-30-dias` | auth | `ConsultaListResponse` | Consultas activas >30 días (filtros: `skip`, `limit`) |
| Estadisticas | GET | `/estadisticas/nacimientos` | auth | `NacimientosStatsResponse` | Estadísticas de nacimientos por sexo/estado, clase de parto, clasificación y trabajo de parto (req: `desde`, `hasta`) |
| Totales | GET | `/totales/` | auth | `TotalesResponse` | KPIs dashboard (7 indicadores: pacientes totales/activos, consultas totales/día, COEX/hosp/emerg del día). Opcional: `fecha` |
| Procedimientos | GET | `/procedimientos/estadisticas/resumen` | auth | dict | Estadísticas anuales/mensuales de procedimientos (req: `anio`, opc: `mes`). Retorna total registros, total cantidad, top 5 |
| Audit | GET | `/audit-log/` | admin | dict (paginated) | Logs (filtros: tabla, username, desde, hasta) |
| Encamamiento | POST | `/encamamiento/` | public | `EncamamientoOut` (201) | Create servicio |
| Encamamiento | GET | `/encamamiento/` | public | `List[EncamamientoOut]` | List (filtro: activo) |
| Encamamiento | GET | `/encamamiento/{servicio_id}` | public | `EncamamientoOut` | By ID |
| Encamamiento | PATCH | `/encamamiento/{servicio_id}` | public | `EncamamientoOut` | Update |
| Encamamiento | DELETE | `/encamamiento/{servicio_id}` | public | 204 | Delete |
| Nacimientos | POST | `/nacimientos/` | auth | `NacimientoOut` (201) | Create (solo requiere `paciente_id`) |
| Nacimientos | POST | `/nacimientos/desde-paciente/{paciente_id}` | auth | `NacimientoOut` (201) | Desde paciente (lee neonatales de `pacientes.datos_extra`) |
| Nacimientos | GET | `/nacimientos/` | auth | `NacimientoListResponse` | List (6 filtros, JOIN con pacientes) |
| Nacimientos | GET | `/nacimientos/{nacimiento_id}` | auth | `NacimientoOut` | By ID (incluye `neonatales` + `paciente` del JOIN) |
| Nacimientos | PATCH | `/nacimientos/{nacimiento_id}` | auth | `NacimientoOut` | Update (solo `madre_id`) |
| Nacimientos | DELETE | `/nacimientos/{nacimiento_id}` | auth | 204 | Delete |
| Nacimientos | POST | `/nacimientos/sincronizar` | auth | dict | Sincronizar madre-hijo + legacy |
| Nacimientos | GET | `/nacimientos/referenciar-legacy` | auth | `LegacyReferenceResponse` | Referenciar legacy |
| SIGSA-3 | GET | `/sigsa3/` | auth | `List[Sigsa3Out]` | List (9 filtros: personal_salud, fecha_consulta, historia_clinica, nombre, sexo, tipo_consulta, especialidad, cie10, q) |
| SIGSA-3 | GET | `/sigsa3/{id}` | auth | `Sigsa3Out` | By ID |
| SIGSA-3 | POST | `/sigsa3/` | auth | `Sigsa3Out` (201) | Create |
| SIGSA-3 | PUT | `/sigsa3/{id}` | auth | `Sigsa3Out` | Update |
| SIGSA-3 | DELETE | `/sigsa3/{id}` | auth | 204 | Delete |

## Estadísticas y Reportes

Módulo centralizado en `modules/estadisticas/`. Todos los endpoints devuelven JSON con `titulo`, `desde`, `hasta`, `datos`, `total_general` y `generado_en`.

```bash
# Autenticación requerida para todos los endpoints
TOKEN=$(curl -s -X POST https://host/fah/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
AUTH="Authorization: Bearer $TOKEN"
```

### Consultas por rango de fechas (requieren `desde` y `hasta` en YYYY-MM-DD)

```bash
# Pacientes atendidos agrupados por tipo_consulta, especialidad y sexo
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/pacientesAtendidos?desde=2025-01-01&hasta=2025-12-31"

# Hospitalizaciones infantiles (>28 días y <5 años) solo tipo_consulta=2
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/hospitalizacion-infantil?desde=2025-01-01&hasta=2025-12-31"

# Promedio diario de consultas por especialidad (con desglose por tipo)
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/promedioDiario?desde=2025-01-01&hasta=2025-12-31"

# Consultas de personal del hospital (filtra datos_extra.socioeconomicos.personal_hospital=S)
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/personal-hospital?desde=2025-01-01&hasta=2025-12-31"

# Consultas de estudiantes públicos (filtra datos_extra.socioeconomicos.estudiante_publico=S)
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/estudiante-publico?desde=2025-01-01&hasta=2025-12-31"

# Reingresos hospitalarios clasificados en <8 días y por complicaciones
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/reingresos?desde=2025-01-01&hasta=2025-12-31"
```

### Consultas paginadas (usan `skip`/`limit`)

```bash
# Reingresos tipo 3 (delegado a consultas.service)
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/reingresos-tipo3?skip=0&limit=50"

# Consultas activas con más de 30 días de antigüedad
curl -H "$AUTH" "https://host/fah/estadisticas/consultas/activos-mayores-a-30-dias?skip=0&limit=50"
```

### Nacimientos

```bash
# Estadísticas de nacimientos: por sexo/estado, clase de parto, clasificación, trabajo de parto
curl -H "$AUTH" "https://host/fah/estadisticas/nacimientos?desde=2025-01-01&hasta=2025-12-31"
```

### Dashboard KPIs (`modules/totales/`)

```bash
# 7 indicadores en tiempo real (hoy)
curl -H "$AUTH" "https://host/fah/totales/"

# O de una fecha específica
curl -H "$AUTH" "https://host/fah/totales/?fecha=2025-06-15"
```

Retorna:
```json
{
  "totales": [
    {"entidad": "Pacientes Totales", "total": 15000, "icono": "users", "color": "blue"},
    {"entidad": "Pacientes Activos", "total": 12000, "icono": "user-check", "color": "purple"},
    {"entidad": "Consultas Totales", "total": 85000, "icono": "file-medical", "color": "green"},
    {"entidad": "Consultas Hoy", "total": 120, "icono": "calendar-check", "color": "teal"},
    {"entidad": "COEX Hoy", "total": 45, "icono": "stethoscope", "color": "cyan"},
    {"entidad": "Hospitalizaciones Hoy", "total": 30, "icono": "bed", "color": "orange"},
    {"entidad": "Emergencias Hoy", "total": 45, "icono": "ambulance", "color": "red"}
  ],
  "generado_en": "2025-06-23T10:30:00"
}
```

### Procedimientos

```bash
# Reporte agregado de procedimientos realizados
curl -H "$AUTH" "https://host/fah/procedimientos/reporte"

# Estadísticas anuales/mensuales (top 5 procedimientos)
curl -H "$AUTH" "https://host/fah/procedimientos/estadisticas/resumen?anio=2025"
curl -H "$AUTH" "https://host/fah/procedimientos/estadisticas/resumen?anio=2025&mes=6"
```

### Arquitectura del módulo

```
modules/
├── estadisticas/           # Reportes personalizados sobre consultas + pacientes + nacimientos
│   ├── router.py           # 9 endpoints, todos auth, SQL raw con text()
│   ├── service.py          # Lógica de negocio con consultas SQL directas
│   └── schemas.py          # Schemas Pydantic de respuesta (sin modelos ORM)
├── totales/                # KPIs del dashboard en tiempo real
│   ├── router.py           # 1 endpoint GET / (fecha opcional), SQL con text()
│   ├── service.py          # Misma lógica que router (duplicado)
│   └── schemas.py          # TotalesItem + TotalesResponse
└── procedimientos/         # Catálogo + procedimientos realizados
    ├── router.py           # CRUD + GET /reporte + GET /estadisticas/resumen
    ├── models.py           # Procedimiento + ProceMedico (ORM)
    └── schemas.py          # Schemas de solicitud/respuesta
```

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
