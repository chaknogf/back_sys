# Arquitectura del sistema `back_sys` (FastAPI + PostgreSQL)

> Documento generado con el skill `code-architect-documenter` (modo **Completo**, alcance **sistema completo**).
> Fuente de verdad: código real del repositorio (`main.py`, `core/`, `modules/`, `docs/`, `AGENTS.md`). Las afirmaciones inferidas se marcan `[Inferido]`.

---

## 0. Metadatos

| Campo | Valor |
|---|---|
| Sistema | `back_sys` — backend del Sistema FAH (Hospital General Tipo I de Tecpán) |
| Versión API | 3.0.0 (`main.py`) |
| Framework | FastAPI 0.139 (Python 3.11+; dev 3.14) |
| Servidor | Uvicorn 0.38 (workers vía gunicorn 26) |
| Base de datos | PostgreSQL 18, base `hospital` |
| ORM | SQLAlchemy 2.0 + psycopg2-binary |
| Auth | JWT (joserfc HS256) + Argon2 (passlib) |
| Validación | Pydantic 2.12 |
| Caché / rate limit | Redis 8 (fastapi-cache2 + slowapi; fallback a memoria) |
| Tests | pytest 9 + FastAPI TestClient |
| Prefijo de rutas | `/fah` (root_path) |
| Módulos | 37 paquetes en `modules/` (34 con router, 2 solo modelos) |

---

## 1. Comentarios de código inteligentes (fragmentos clave)

Fragmentos reales con docstrings que documentan el **por qué** (no se modificó la lógica).

### 1.1 `main.py` — ciclo de vida y caché compartida

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa la caché compartida (Redis) al arrancar y la libera al apagar.

    En producción, si Redis no responde, la app arranca en modo degradado
    (caché y rate limit en memoria por worker) pero lo deja registrado como
    error, porque sin Redis compartido los límites de tasa no son globales.
    """
    ...
    yield
    engine.dispose()
```

### 1.2 `core/security.py` — guardia global de escritura

```python
def write_guard(request: Request, db: Session = Depends(get_db)):
    """Guardia global: los métodos de escritura exigen rol >= EDITOR.

    - GET/HEAD/OPTIONS nunca se bloquean: el rol `read_only` puede leer todo.
    - Rutas exentas (login, recuperación, catálogos legacy) quedan fuera para
      no romper contratos existentes.
    - La autorización se resuelve contra la BD (fuente de verdad), no contra
      el claim del JWT, para que un usuario desactivado pierda acceso de
      inmediato aunque su token siga vigente.
    """
```

### 1.3 `core/security.py` — emisión de JWT

```python
def create_access_token(data: dict, expires_delta=None, audience=JWT_AUD_API) -> str:
    """Firma un JWT con expiración y un identificador único de emisión (jti).

    El `jti` permite revocación futura por token sin invalidar sesiones
    ajenas; hoy no se persiste, pero se reserva para auditoría.
    """
```

### 1.4 `modules/expediente/service.py` — correlativos atómicos

```python
def _generar_correlativo(db: Session, tipo: str, formato: str) -> str:
    """Incrementa el contador anual bajo bloqueo de fila (FOR UPDATE).

    No confirma la transacción: el llamador hace commit (o rollback) junto
    con el resto de su operación, para que el correlativo y el documento que
    lo usa sean atómicos. Si se confirmara aquí, un fallo posterior dejaría
    un hueco en la numeración.
    """
```

### 1.5 `modules/nacimientos/service.py` — derivación de métricas neonatales

```python
def _computar(neonatales: dict) -> dict:
    """Deriva peso en gramos, clasificación (EBP/MBP/BP/PN) y trabajo de parto
    (Prematuro / a Término / Prolongado) desde el texto crudo capturado por
    la recepción (libras/onzas, semanas gestacionales). Se reutiliza tanto al
    crear como al recomputar masivamente.
    """
```

### 1.6 `modules/nacimientos/service.py` — confianza de la evidencia

```python
def confianza_evidencias_neonatales(neonatales: dict, computado: dict) -> dict:
    """Nivel de confianza del análisis según la evidencia disponible.

    - peso + edad gestacional presentes → alta.
    - solo uno → media (la inferencia del otro queda 'sin evidencia').
    - ninguno → sin_evidencia: no se puede concluir nada.
    """
```

---

## 2. Resumen de diseño y arquitectura

### 2.1 Contexto y responsabilidad

`back_sys` es el backend del Sistema FAH de un hospital público de Guatemala (Hospital General Tipo I de Tecpán). Resuelve el registro clínico y administrativo: expedientes únicos, consultas (COEX, hospitalización, emergencia), ciclos de atención y eventos, nacimientos y defunciones, censo de camas, procedimientos, SIGSA-3 (consultas normalizadas para estadística ministerial), citas, préstamos de expedientes, catálogos (CIE-10, municipios, países), reportes y KPIs del dashboard, y un asistente NL→SQL de solo lectura. Expone una API REST consumida por el frontend Angular `hospital3`.

### 2.2 Patrón arquitectónico

**Monolito modular** (evidencia: un único proceso FastAPI, `main.py` incluye ~34 routers; módulos por dominio con `router/schemas/models/service`; BD compartida `hospital`). No hay microservicios ni bus de eventos; la integración es sincrónica HTTP→servicio→SQLAlchemy→PostgreSQL. `[Inferido]` La consistencia se logra con transacciones por operación y bloqueos de fila (`FOR UPDATE`) en correlativos.

### 2.3 Stack tecnológico

- **Lenguaje/Framework:** Python 3.11+ / FastAPI 0.139.
- **Servidor:** Uvicorn 0.38, gunicorn 26 (workers).
- **BD:** PostgreSQL 18 (`hospital`), extensiones `pg_trgm`, `unaccent`.
- **ORM:** SQLAlchemy 2.0 + psycopg2-binary.
- **Auth:** JWT HS256 (joserfc) + Argon2 (passlib), expiración configurable (default 24 h).
- **Validación:** Pydantic 2.12.
- **Email:** FastAPI-Mail (SMTP Gmail) + Jinja2.
- **Caché / rate limit:** Redis 8 (fastapi-cache2 + slowapi), degradación a memoria en dev.
- **Tests:** pytest 9 + FastAPI TestClient (requiere PostgreSQL real).
- **Paquetes:** Poetry (primario) + pip (`requirements.txt` usado por `deploy.sh`).

### 2.4 Tabla de componentes

| Componente | Capa | Responsabilidad | Depende de | Ubicación |
|---|---|---|---|---|
| `FastAPI app` | Interfaz/API | Ensambla routers, middlewares, excepciones, OpenAPI | todos los routers | `main.py` |
| `core/config.py` | Infraestructura | Variables de entorno (JWT, mail, DB, Redis, LLM) | — | `core/config.py` |
| `core/database.py` | Infraestructura | Engine SQLAlchemy, sesión, engine read-only | config | `core/database.py` |
| `core/security.py` | Dominio transversal | Hash/verify Argon2, JWT, guards RBAC | database, config | `core/security.py` |
| `core/exceptions.py` | Interfaz/API | Handlers globales (422, 409, 500) | — | `core/exceptions.py` |
| `core/limiter.py` | Infraestructura | Rate limiter compartido | Redis/memoria | `core/limiter.py` |
| `core/mail.py` | Infraestructura | Config FastAPI-Mail | config | `core/mail.py` |
| `core/db_helpers.py` | Infraestructura | Helpers `fetchone/fetchall` para SQL raw | database | `core/db_helpers.py` |
| `modules/<dominio>/router.py` | Interfaz/API | Endpoints HTTP, validación, auth | schemas, service | `modules/*/router.py` |
| `modules/<dominio>/schemas.py` | Interfaz/API | Pydantic entrada/salida | — | `modules/*/schemas.py` |
| `modules/<dominio>/models.py` | Datos | ORM SQLAlchemy | Base | `modules/*/models.py` |
| `modules/<dominio>/service.py` | Dominio | Reglas de negocio, SQL, transacciones | models, db | `modules/*/service.py` |
| `modules/chat/` | Dominio | NL→SQL read-only con LLM | database, config | `modules/chat/` |
| `modules/agente/` | Dominio | Agente/automatización | — | `modules/agente/` |
| `modules/audit_log/middleware.py` | Interfaz/API | Captura IP de cliente para auditoría | — | `modules/audit_log/middleware.py` |
| `tests/` | Calidad | pytest + TestClient | app, BD real | `tests/` |

### 2.5 Flujo de control general

1. El cliente (Angular `hospital3`) envía `HTTP/JSON` con `Authorization: Bearer <jwt>` al prefijo `/fah`.
2. `TrustedHostMiddleware`, `SlowAPIMiddleware` (rate limit), `AuditClientIPMiddleware` y `CORSMiddleware` procesan la petición.
3. `FastAPI` resuelve la ruta; la dependency global `_write_guard` exige rol ≥ EDITOR para métodos de escritura (salvo rutas exentas).
4. El router valida entrada con Pydantic y resuelve auth (`get_current_user` / `get_current_admin_user`).
5. El servicio ejecuta la lógica de negocio y SQL (ORM o `text()` raw) dentro de una sesión.
6. La transacción se confirma en el servicio (o se revierte en error); el correlativo y el documento se confirman juntos.
7. La respuesta serializada vuelve al cliente. Errores se normalizan en `core/exceptions.py`.

### 2.6 Decisiones de diseño (ADR cortos)

- **ADR-1: Monolito modular sobre microservicios.**
  - Contexto: usuarios, pacientes, consultas y transacciones compartidas.
  - Decisión: mantener un solo proceso con módulos por dominio.
  - Consecuencias: despliegue simple y consistencia local; a cambio, todo escala como una unidad y los cambios de schema afectan a toda la app.

- **ADR-2: SQLAlchemy + SQL raw mezclado.**
  - Contexto: reportes y estadísticas requieren SQL complejo (joins, agregaciones, `unaccent`).
  - Decisión: ORM para CRUD simple; `text()` raw para reportes/estadísticas.
  - Consecuencias: flexibilidad y rendimiento; riesgo de SQL disperso y duplicación de helpers (`_unaccent_ilike`, parseo de fechas).

- **ADR-3: Correlativos con bloqueo de fila y commit diferido.**
  - Contexto: numeración sin duplicados ante concurrencia.
  - Decisión: `SELECT ... FOR UPDATE` sobre tabla de control por año; el servicio no hace commit propio.
  - Consecuencias: atomicidad correlativo/documento; depende de que el llamador confirme la transacción (deuda: `generar_expediente()` hace commit interno en alta madre-hijo).

- **ADR-4: JSONB para datos flexibles (`pacientes.datos_extra`, `consultas.indicadores`).**
  - Contexto: campos socioeconómicos y banderas clínicas variables.
  - Decisión: almacenar en JSONB con índices GIN.
  - Consecuencias: evolución sin migraciones; consultas y validación menos estrictas; riesgo de claves inconsistentes (`viene_referido` vs `viene_referido_de`).

### 2.7 Seguridad y operación

- **Auth:** `POST /auth/login` → JWT (`access_token`), validado por `get_current_user`; `get_current_admin_user` restringe a `role == "admin"`.
- **RBAC:** roles `admin`, `editor`, `regular` (histórico, nivel escritura), `read_only`, más roles de dominio legados (`registro`, `uisau`, etc.) con nivel escritura. `write_guard` global bloquea escritura a `read_only`.
- **Secretos:** `.env` (no versionar en producción; deuda crítica: `.env` con secretos reales en repo).
- **Rate limit:** slowapi por IP; desactivado en tests (`RATELIMIT_ENABLED=false`).
- **Caché:** Redis compartido en producción; en dev, memoria con warnings.
- **DB:** pool SQLAlchemy (pre_ping, recycle), statement_timeout 300 s, timezone `America/Guatemala`; engine read-only opcional para chat.
- **Manejo de errores:** handlers globales; riesgo de filtrar `str(exc)`/body (PHI) — deuda media.
- **CORS/Hosts:** configurables por `.env`; laxos en dev.
- **Auditoría:** `audit_log` registra accesos (tabla, registro, endpoint, método, usuario, IP).

---

## 3. Grafo de interconexión y modelo de datos

### 3.1 Diagrama de componentes por capas

```mermaid
flowchart TD
  subgraph ui["Interfaz (Angular hospital3)"]
    web["Angular 20 PWA"]
  end
  subgraph api["API FastAPI (/fah)"]
    main["main.py (app)"]
    mw["Middlewares<br/>CORS, SlowAPI, AuditIP, TrustedHost"]
    routers["Routers (34 módulos)"]
    exc["Exception handlers"]
  end
  subgraph dom["Dominio (modules/*/service.py)"]
    svcPac["Pacientes"]
    svcCons["Consultas / Ciclos / Eventos"]
    svcNac["Nacimientos / Defunciones"]
    svcSigsa["SIGSA-3 / sigsa3_registros"]
    svcChat["Chat NL→SQL"]
    svcExp["Expediente (correlativos)"]
    svcCom["common / vector_similarity"]
  end
  subgraph data["Datos"]
    orm["SQLAlchemy ORM"]
    raw["SQL raw (text())"]
    db[("PostgreSQL 18<br/>hospital")]
    redis[("Redis 8<br/>caché / rate limit")]
  end
  subgraph ext["Servicios externos"]
    renap["RENAP (civil)"]
    smtp["SMTP Gmail"]
    llm["LLM (CIE-10 / chat)"]
  end

  web -->|HTTP/JSON| main
  main --> mw
  mw --> routers
  routers --> exc
  routers --> svcPac
  routers --> svcCons
  routers --> svcNac
  routers --> svcSigsa
  routers --> svcChat
  routers --> svcExp
  svcPac --> orm
  svcCons --> orm
  svcCons --> raw
  svcNac --> raw
  svcSigsa --> raw
  svcChat --> raw
  svcExp --> orm
  orm --> db
  raw --> db
  main --> redis
  svcChat --> llm
  svcCons --> renap
  main --> smtp
```

### 3.2 Modelo de datos (núcleo clínico)

```mermaid
erDiagram
  PACIENTES ||--o{ CONSULTAS : "paciente_id"
  PACIENTES ||--o{ NACIMIENTOS : "paciente_id (neonato)"
  PACIENTES ||--o{ NACIMIENTOS : "madre_id"
  PACIENTES ||--o{ CONSTANCIA_NACIMIENTO : "paciente_id / madre_id"
  PACIENTES ||--o{ DEFUNCIONES : "paciente_id"
  PACIENTES ||--o{ CITAS : "paciente_id"
  PACIENTES ||--o{ SIGSA3_REGISTROS : "paciente_id"
  PACIENTES ||--o{ PRESTAMOS : "id_paciente"

  CONSULTAS ||--o{ CICLOS_CONSULTA : "consulta_id"
  CONSULTAS ||--o{ EVENTOS_CONSULTA : "consulta_id"
  CONSULTAS ||--o{ LABORATORIOS : "consulta_id"
  CONSULTAS ||--o{ RAYOS_X : "consulta_id"
  CONSULTAS ||--o{ SIGSA3_REGISTROS : "consulta_id"
  CONSULTAS ||--o{ CONSULTAS_HISTORIAL : "consulta_id"

  ESPECIALIDADES ||--o{ MEDICOS : "especialidad_id"
  ESPECIALIDADES ||--o{ CONSULTAS : "especialidad_id"
  ESPECIALIDADES ||--o{ CICLOS_CONSULTA : "especialidad_id"
  ESPECIALIDADES ||--o{ CITAS : "especialidad_id"
  ESPECIALIDADES ||--o{ PERSONAL_SALUD : "especialidad_id"
  ESPECIALIDADES ||--o{ SIGSA3_REGISTROS : "especialidad_id"

  MEDICOS ||--o{ PERSONAL_SALUD : "medico_id"
  MEDICOS ||--o{ CONSTANCIA_NACIMIENTO : "medico_id"
  MEDICOS ||--o{ DEFUNCIONES : "medico_id"
  MEDICOS ||--o{ SIGSA3_REGISTROS : "medico_id"

  CICLOS_CONSULTA ||--o{ LABORATORIOS : "ciclo_consulta_id"
  CICLOS_CONSULTA ||--o{ RAYOS_X : "ciclo_consulta_id"

  PROCEDIMIENTOS ||--o{ PROCE_MEDICOS : "id_procedimiento"
  ENCAMAMIENTO ||--o{ CENSO_CAMAS : "servicio_id"

  USERS ||--o{ CONSTANCIA_NACIMIENTO : "registrador_id"
  USERS ||--o{ DEFUNCIONES : "registrador_id"
  USERS ||--o{ NACIMIENTOS : "registrador_id"

  CONSTANCIA_NACIMIENTO ||--o{ CONSTANCIA_NACIMIENTO_HISTORIAL : "constancia_id"
```

> Modelo completo (50 tablas, 83 FK, catálogos, insumos, control de correlativos): `docs/esquema_bd.md`.

### 3.3 Contexto del sistema (externos)

```mermaid
flowchart LR
  subgraph sys["back_sys (FastAPI)"]
    api["API /fah"]
  end
  fe["Frontend Angular<br/>hospital3"] -->|HTTP/JSON| api
  api -->|SQL| pg[("PostgreSQL 18")]
  api -->|cache/ratelimit| redis[("Redis 8")]
  api -->|SMTP| mail["Gmail SMTP"]
  api -->|HTTP| renap["RENAP civil"]
  api -->|API key| llm["LLM (CIE-10 / chat)"]
  api -->|lectura| legacy["nacimientos_legacy<br/>(histórico)"]
```

---

## 4. Procesos, secuencias y estados

### 4.1 Login

```mermaid
sequenceDiagram
  autonumber
  participant C as Cliente (Angular)
  participant A as FastAPI /auth
  participant S as core/security.py
  participant D as PostgreSQL

  C->>A: POST /fah/auth/login {username, password}
  A->>D: SELECT user WHERE username
  D-->>A: fila usuario (o none)
  alt usuario inexistente o estado != A
    A-->>C: 401/403
  else contraseña válida
    A->>S: verify_password(plain, hash)
    S-->>A: True
    A->>S: create_access_token({sub: username})
    S-->>A: JWT
    A-->>C: TokenResponse {access_token}
  end
```

### 4.2 Alta de consulta (registro)

```mermaid
sequenceDiagram
  autonumber
  participant C as Cliente
  participant R as Router consultas
  participant S as service consultas
  participant D as PostgreSQL

  C->>R: POST /fah/consultas/registro (auth)
  R->>R: get_current_user + validación Pydantic
  R->>S: crear registro
  S->>D: INSERT consultas (paciente, especialidad, tipo, fecha, indicadores)
  D-->>S: id
  S->>D: (opcional) INSERT ciclos/eventos
  S-->>R: RegistroConsultaOut
  R-->>C: 201
```

### 4.3 Alta de nacimiento madre-hijo

```mermaid
sequenceDiagram
  autonumber
  participant C as Cliente
  participant P as Router pacientes
  participant N as Router nacimientos
  participant S as services
  participant D as PostgreSQL

  C->>P: POST /fah/pacientes/madre-hijo/{madre_id}
  P->>S: crear neonato (datos_extra.origen tipo=MADRE)
  S->>D: INSERT pacientes (neonatales + origen)
  D-->>S: paciente_id
  S-->>P: PacienteOut
  P-->>C: 201 paciente neonato

  C->>N: POST /fah/nacimientos/desde-paciente/{paciente_id}
  N->>S: crear_nacimiento_desde_paciente
  S->>D: SELECT pacientes (neonatales, origen)
  S->>S: _computar (peso, clasificación, trabajo de parto)
  S->>D: INSERT nacimientos (paciente_id, madre_id, computados)
  D-->>S: nacimiento_id
  S-->>N: NacimientoOut
  N-->>C: 201 nacimiento
```

### 4.4 Asociación completa SIGSA-3 (`/sigsa3/asociar-todo`)

```mermaid
flowchart TD
  start["POST /sigsa3/asociar-todo"] --> p1["1. Asociar paciente_id<br/>(por expediente / historia clínica)"]
  p1 --> p2["2. Asociar medico_id<br/>(personal_salud → medicos.nombre)"]
  p2 --> p3["3. Asociar consulta_id<br/>(por paciente + fecha)"]
  p3 --> p4["4. Normalizar a sigsa3_registros<br/>(claves FK + hechos)"]
  p4 --> p5["5. Reporte de cobertura<br/>(asociados vs pendientes)"]
  p5 --> endn["Respuesta JSON con contadores"]
```

### 4.5 Ciclo de vida de una consulta (estados)

```mermaid
stateDiagram-v2
  [*] --> Activa: POST /consultas/registro
  Activa --> ConCiclo: POST /ciclos
  ConCiclo --> ConEventos: POST /eventos (ingreso/evolucion/egreso)
  Activa --> Inactiva: DELETE /consultas/{id} (soft delete)
  Inactiva --> Activa: PATCH reactivar
  Activa --> Eliminada: DELETE /consultas/{id}/eliminar (admin, físico)
  Inactiva --> Eliminada: DELETE /consultas/{id}/eliminar (admin, físico)
  Eliminada --> [*]
```

---

## 5. Deuda técnica, riesgos y observaciones

| # | Hallazgo | Evidencia | Severidad |
|---|---|---|---|
| 1 | `.env` con secretos reales versionado en repo remoto | `.env`, `AGENTS.md` | Crítica |
| 2 | Auto-escalada de privilegios: `PUT /users/{id}` permite asignarse `role: admin` | `modules/users/router.py:65`, `schemas.py:25` | Crítica |
| 3 | Falta rol read-only efectivo y ownership; merge/borrados físicos y `audit-log`/`GET users/{id}` solo exigen auth | `modules/pacientes/merge_router.py`, `modules/audit_log/router.py` | Alta |
| 4 | `generar_expediente()` hace `commit()` interno → rompe atomicidad en alta madre-hijo | `modules/expediente/service.py` (deuda reportada) | Alta |
| 5 | Errores filtran `str(exc)`/body (posible PHI); docs públicas; CORS/Hosts laxos | `core/exceptions.py` | Media |
| 6 | Dependencias: `pyproject.toml` declara 63 (29 transitivas mal listadas, 14 huérfanas); `pytest`/`rust_engine` no declarados; `requirements.txt` trae numpy/et-xmlfile/pillow innecesarias | `pyproject.toml`, `requirements.txt` | Media |
| 7 | Índices faltantes en `citas`, `prestamos`, `defunciones`, `audit_log`; N+1 en varios services | `docs/esquema_bd.md`, services | Media |
| 8 | Código muerto (`modules/sigsa3/implementacion/sigsa3_optimizado.py`, helpers de `chat/service.py`); duplicación de helpers (`_unaccent_ilike`, parseo de fechas, cálculo de edad) | reportado en `AGENTS.md` | Baja |
| 9 | Claves JSONB inconsistentes (`viene_referido` vs `viene_referido_de`) y `personal_hospital` como `S`/`N`/null vs booleanos | `modules/estadisticas/service.py` | Media |
| 10 | `GET /encamamiento`, `/municipios`, `/paises` son públicos (catálogos); revisar allowlist | `main.py` (write_guard exentos) | Baja |

---

## 6. Guía rápida de lectura (onboarding)

**Por dónde empezar (en orden):**

1. `main.py` — ensamblaje de la app, middlewares, routers, prefijo `/fah`.
2. `core/config.py` + `core/database.py` — configuración y conexión a PostgreSQL.
3. `core/security.py` — auth, JWT, RBAC (`write_guard`, `get_current_user`).
4. `modules/pacientes/` — CRUD, duplicados (trigram/soundex), merge, neonatos.
5. `modules/consultas/` + `modules/ciclos/` + `modules/eventos/` — ciclo de atención.
6. `modules/nacimientos/service.py` — derivación de métricas y sincronización legacy.
7. `modules/sigsa3/` + `modules/sigsa3_registros/` — normalización y asociación.
8. `modules/estadisticas/` + `modules/totales/` — reportes y KPIs.
9. `docs/esquema_bd.md` — modelo de datos completo.

**Cómo ejecutar y probar localmente:**

```bash
cd back_sys
cp .env.example .env   # completar valores
uvicorn main:app --reload          # http://localhost:8000, docs en /docs
pytest tests/ -v                   # requiere PostgreSQL 'hospital' real
```

En tests se fija `RATELIMIT_ENABLED=false` en `tests/conftest.py` antes de importar `main`.

**Glosario de dominio:**

- **Expediente:** correlativo `EXP-YYYY-######` del paciente.
- **COEX / tipo_consulta 1/2/3:** consulta externa, hospitalización, emergencia.
- **SIGSA-3:** registro normalizado de consultas para estadística ministerial.
- **Neonatales:** datos del recién nacido (peso, edad gestacional, tipo/clase de parto) en `pacientes.datos_extra`.
- **EBP/MBP/BP/PN:** clasificación por peso al nacer (extremo/muy bajo/bajo/peso normal).
- **FEFO/FIFO:** no aplican aquí; el correlativo usa bloqueo de fila.
- **Soft delete:** `estado='I'`/`activo=false` en lugar de borrado físico.

**Preguntas abiertas / `[Por confirmar]`:**

- ¿Existe un rol `read_only` funcional en producción o solo en código? `[Por confirmar]`
- ¿Se usan credenciales read-only de PostgreSQL (`POSTGRES_RO_USER`) en producción? `[Por confirmar]`
- ¿El frontend `hospital3` consume todos los 318 endpoints publicados? `[Por confirmar]`
- ¿Hay pipeline CI que valide OpenAPI y rutas públicas? `[Por confirmar]` (la rutina está documentada en `docs/arquitectura_api.md`).