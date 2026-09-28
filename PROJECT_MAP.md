# PROJECT_MAP.md — back_sys (Hospital FAH)

> Mapa arquitectónico completo del sistema de gestión hospitalaria.
> Generado para análisis, escalabilidad y desarrollo de nuevas funcionalidades.

---

## 1. Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Framework | FastAPI | >=0.139.0 |
| ORM | SQLAlchemy | >=2.0.51 |
| DB | PostgreSQL | 18 (ext: pg_trgm, unaccent) |
| DB Driver | psycopg2-binary | 2.9.11 |
| Auth | JWT (joserfc) + Argon2 (passlib) | — |
| Validación | Pydantic | 2.12.5 |
| Caché | fastapi-cache2 + Redis (fallback InMemory) | — |
| Rate Limit | slowapi | — |
| Email | FastAPI-Mail + Jinja2 | — |
| Server | Uvicorn / Gunicorn | — |
| Charts | Plotly + Matplotlib + Pandas | — |
| LLM | Ollama / OpenAI-compatible (CIE-10 + Chat) | — |
| Package Mgr | Poetry | — |
| Python | ^3.11 | — |

---

## 2. Arquitectura: Modular Monolith

```
back_sys/
├── main.py                          # Entry point, FastAPI app, middleware, routers
├── core/                            # Framework compartido
│   ├── config.py                    # Env vars (JWT, mail, DB, LLM, Redis)
│   ├── database.py                  # Engine + SessionLocal + get_db + get_db_readonly
│   ├── security.py                  # JWT create/verify, Argon2 hash, get_current_user
│   ├── dependencies.py              # Re-exports: get_db, get_current_user, get_current_admin_user
│   ├── exceptions.py                # Global handlers: 422, 409, 500
│   ├── limiter.py                   # SlowAPI limiter instance
│   └── mail.py                      # FastAPI-Mail ConnectionConfig
├── modules/                         # 34 módulos de dominio
│   ├── auth/                        # Login JWT
│   ├── users/                       # CRUD usuarios + email bienvenida
│   ├── pacientes/                   # Pacientes (4 sub-routers)
│   ├── consultas/                   # Consultas médicas + historial
│   ├── ciclos/                      # Ciclos de consulta
│   ├── eventos/                     # Eventos de consulta (ingreso/evolución/egreso)
│   ├── citas/                       # Citas médicas
│   ├── medicos/                     # Médicos CRUD
│   ├── especialidades/              # Catálogo de especialidades
│   ├── nacimientos/                 # Nacimientos (calculados desde pacientes)
│   ├── nacimientos_legacy/          # Datos legacy de nacimientos
│   ├── constancias_nacimiento/      # Constancias de nacimiento + historial
│   ├── defunciones/                 # Defunciones (adulto + fetal)
│   ├── expediente/                  # Correlativos (EXP, EMERG, CN, DF, CM)
│   ├── procedimientos/              # Catálogo + procedimientos realizados
│   ├── prestamos/                   # Préstamos de expedientes
│   ├── encamamiento/                # Catálogos de servicios de encamamiento
│   ├── censo_camas/                 # Censo diario de camas
│   ├── sigsa3/                      # SIGSA-3 (consulta registry + gestor + importación)
│   ├── sigsa3_registros/            # SIGSA-3 registros normalizados
│   ├── personal_salud/              # Catálogo de personal de salud
│   ├── cie10/                       # CIE-10 catálogo + búsqueda + LLM
│   ├── laboratorios/                # Laboratorios (modelo ORM, sin router activo)
│   ├── rayos_x/                     # Rayos X (modelo ORM, sin router activo)
│   ├── paises_iso/                  # Países ISO
│   ├── municipios/                  # Municipios de Guatemala
│   ├── renap/                       # Integración RENAP
│   ├── estadisticas/                # Reportes estadísticos (11 endpoints)
│   ├── totales/                     # KPIs dashboard en tiempo real
│   ├── audit_log/                   # Auditoría de acceso + middleware IP
│   ├── chat/                        # NL→SQL read-only (LLM)
│   ├── agente/                      # Agente estadístico (rule-based + aprendizaje)
│   ├── quirofano/                   # Quirófano (modelos catálogo)
│   └── common/                      # Schemas compartidos
├── tests/                           # 12 archivos de test
├── migrations/                      # 19 scripts SQL de migración
├── scripts/                         # Scripts auxiliares
├── sql/                             # Optimización de rendimiento
├── docs/                            # Documentación
└── pyproject.toml                   # Dependencias Poetry
```

---

## 3. Mapa de Módulos y Archivos

### 3.1 Core (Framework)

| Archivo | Responsabilidad |
|---------|----------------|
| `core/config.py` | Variables de entorno: SECRET_KEY, DB, Mail, LLM, Redis, Opencode |
| `core/database.py` | Engine SQLAlchemy, SessionLocal, get_db(), get_db_readonly() |
| `core/security.py` | hash_password, verify_password, create_access_token, get_current_user, get_current_admin_user |
| `core/dependencies.py` | Re-exports de get_db y security |
| `core/exceptions.py` | Handlers globales: validación (422), integridad (409), general (500) |
| `core/limiter.py` | Instancia SlowAPI RateLimiter |
| `core/mail.py` | Configuración FastAPI-Mail (SMTP Gmail) |

### 3.2 Módulos de Dominio

| Módulo | Archivos | Modelo ORM | Tabla DB | Dependencias clave |
|--------|----------|-----------|----------|-------------------|
| **auth** | router, schemas, service | — | users | users, security |
| **users** | router, schemas, service, models | UserModel | users | security, mail |
| **pacientes** | router, schemas, service, models + 3 sub-routers | PacienteModel | pacientes | — (raíz) |
| **consultas** | router, schemas, service, models | ConsultaModel + ConsultaHistorialModel | consultas, consultas_historial | pacientes, especialidades |
| **ciclos** | router, schemas, service, models | CiclosConsulta | ciclos_consulta | consultas, especialidades |
| **eventos** | router, schemas, service, models | EventoConsultaModel | eventos_consulta | consultas |
| **citas** | router, schemas, service, models | CitaModel | citas | pacientes, especialidades |
| **medicos** | router, schemas, service, models | MedicoModel | medicos | especialidades |
| **especialidades** | router, schemas, service, models | EspecialidadModel | especialidades | — |
| **nacimientos** | router, schemas, service, models | NacimientoModel | nacimientos | pacientes, users |
| **nacimientos_legacy** | router, schemas, models | NacimientoLegacyModel | nacimientos_legacy | — |
| **constancias_nacimiento** | router, schemas, models | ConstanciaNacimientoModel + Historial | constancia_nacimiento, constancia_nacimiento_historial | pacientes, medicos, users |
| **defunciones** | router, schemas, service, models | DefuncionModel | defunciones | pacientes, medicos, users |
| **expediente** | router, models, service | CorrelativoControl, ExpedienteControl, etc. | tablas de control | — |
| **procedimientos** | router, schemas, models | Procedimiento + ProceMedico | procedimientos, proce_medicos | especialidades |
| **prestamos** | router, schemas, service, models | PrestamoModel | prestamos | — |
| **encamamiento** | router, schemas, service, models | EncamamientoModel | encamamiento | — |
| **censo_camas** | router, schemas, service, models | CensoCamaModel | censo_camas | — |
| **sigsa3** | router, schemas, service, models + gestor_router | Sigsa3Model + Sigsa3RegistroModel | sigsa3, sigsa3_registros | medicos, especialidades, personal_salud |
| **sigsa3_registros** | router, schemas, service, models | Sigsa3RegistroModel | sigsa3_registros | medicos, especialidades |
| **personal_salud** | router, schemas, service, models | PersonalSaludModel | personal_salud | especialidades |
| **cie10** | router, schemas, service, models | Cie10Model | cie10_catalogo | LLM |
| **paises_iso** | router, schemas, models | PaisISOModel | paises_iso | — |
| **municipios** | router, schemas, models | MunicipiosModel | municipios | — |
| **renap** | router, schemas, service | — | — | HTTP externo |
| **estadisticas** | router, schemas, service | — (SQL raw) | — | consultas, pacientes, nacimientos, sigsa3 |
| **totales** | router, schemas, service | — (SQL raw) | — | pacientes, consultas |
| **audit_log** | router, models, service + middleware | AuditLogModel | audit_log | — |
| **chat** | router, schemas, service | — | — | LLM, DB read-only |
| **agente** | router, schemas, service, models, interpreter, entidades | ReglaAgente, FeedbackAgente | reglas, feedback | especialidades, DB |
| **quirofano** | router, schemas, service, models | 6 modelos catálogo | quirofano tables | — |
| **laboratorios** | models | Laboratorios | laboratorios | consultas |
| **rayos_x** | models | RayosX | rayos_x | consultas, ciclos |
| **common** | schemas | — | — | — |

---

## 4. Diagrama de Relaciones entre Modelos (FK)

```
                    ┌─────────────┐
                    │   users     │
                    │  (auth)     │
                    └──────┬──────┘
                           │
              ┌────────────┼─────────────────────────────────┐
              │            │                                  │
              ▼            ▼                                  ▼
    ┌──────────────┐  ┌──────────────┐             ┌──────────────────┐
    │  pacientes   │  │   medicos    │             │  especialidades  │
    │  (center)    │  │              │             │   (catálogo)     │
    └──────┬───────┘  └──────┬───────┘             └────────┬─────────┘
           │                 │                              │
     ┌─────┼─────┬───────────┼──────────┬───────────────────┼──────────┐
     │     │     │           │          │                   │          │
     ▼     ▼     ▼           ▼          ▼                   ▼          ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ┌───────────┐ ┌─────────┐
│consultas│ │ constan- │ │defuncio- │ │  citas   │  │  medico   │ │proce-   │
│        │ │ cias_nac │ │  nes     │ │          │  │ (FK esp.) │ │dimedico │
└───┬────┘ └──────────┘ └──────────┘ └──────────┘  └───────────┘ └─────────┘
    │
    ├──────┬──────────┬──────────────┐
    │      │          │              │
    ▼      ▼          ▼              ▼
┌───────┐ ┌────────┐ ┌───────────┐ ┌──────────────┐
│ciclos │ │eventos │ │laboratorios│ │   rayos_x   │
│       │ │        │ │           │ │              │
└───────┘ └────────┘ └───────────┘ └──────────────┘

┌──────────────┐     ┌──────────────────┐
│ nacimientos  │────▶│ pacientes (×2)   │  paciente_id + madre_id
└──────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ sigsa3_registros │────▶│ medicos          │  medico_id
│                  │────▶│ especialidades   │  especialidad_id
│                  │────▶│ personal_salud   │  personal_salud_id
└──────────────────┘     └──────────────────┘
```

### 4.1 Foreign Keys Principales

| Modelo | Campo FK | Tabla referenciada | ON DELETE |
|--------|----------|-------------------|-----------|
| ConsultaModel.paciente_id | FK | pacientes.id | CASCADE |
| ConsultaModel.especialidad_id | FK | especialidades.id | SET NULL |
| CiclosConsulta.consulta_id | FK | consultas.id | RESTRICT |
| EventoConsultaModel.consulta_id | FK | consultas.id | CASCADE |
| CitaModel.paciente_id | FK | pacientes.id | RESTRICT |
| CitaModel.especialidad_id | FK | especialidades.id | SET NULL |
| MedicoModel.especialidad_id | FK | especialidades.id | SET NULL |
| NacimientoModel.paciente_id | FK | pacientes.id | SET NULL |
| NacimientoModel.madre_id | FK | pacientes.id | SET NULL |
| NacimientoModel.registrador_id | FK | users.id | SET NULL |
| ConstanciaNacimientoModel.paciente_id | FK | pacientes.id | RESTRICT |
| ConstanciaNacimientoModel.madre_id | FK | pacientes.id | SET NULL |
| ConstanciaNacimientoModel.medico_id | FK | medicos.id | RESTRICT |
| DefuncionModel.paciente_id | FK | pacientes.id | SET NULL |
| DefuncionModel.madre_id | FK | pacientes.id | SET NULL |
| DefuncionModel.medico_id | FK | medicos.id | SET NULL |
| RayosX.consulta_id | FK | consultas.id | RESTRICT |
| ProceMedico.id_procedimiento | FK | procedimientos.id | SET NULL |
| ProceMedico.especialidad_id | FK | especialidades.id | SET NULL |
| Sigsa3Registro.medico_id | FK | medicos.id | SET NULL |
| Sigsa3Registro.especialidad_id | FK | especialidades.id | SET NULL |
| Sigsa3Registro.personal_salud_id | FK | personal_salud.id | SET NULL |

---

## 5. Flujo de Autenticación

```
1. POST /fah/auth/login (username + password)
         │
         ▼
2. AuthService.verify() → hash vs Argon2
         │
         ▼
3. create_access_token() → JWT (HS256, exp configurable)
         │
         ▼
4. Token en Authorization: Bearer <token>
         │
         ▼
5. get_current_user() decodifica JWT, busca UserModel, verifica estado
         │
         ├── estado="A" → OK
         ├── estado="I" → 403 "Cuenta no activada"
         ├── estado="B" → 403 "Cuenta bloqueada"
         └── otro → 403 "Usuario no autorizado"

6. get_current_admin_user() → verifica role=="admin"
```

**Roles**: `admin`, `user` (implícito)
**Estados usuario**: `A`=Activo, `I`=Inactivo, `B`=Bloqueado

---

## 6. Mapa de Endpoints por Módulo

### 6.1 Autenticación y Usuarios

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/auth/login` | public | Login, retorna JWT |
| GET | `/auth/me` | auth | Usuario actual |
| GET | `/users/` | admin | Listar usuarios |
| GET | `/users/{id}` | auth | Obtener usuario |
| POST | `/users/` | admin | Crear (envía email) |
| PUT | `/users/{id}` | admin/self | Actualizar |
| PATCH | `/users/recuperar` | public | Reset password |
| DELETE | `/users/{id}` | admin | Soft delete |

### 6.2 Pacientes (4 sub-routers)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/pacientes/` | auth | Búsqueda (15+ filtros) |
| GET | `/pacientes/neonatales` | auth | Neonatales |
| GET | `/pacientes/personal-hospital` | auth | Personal hospital |
| GET | `/pacientes/{id}` | auth | Por ID |
| POST | `/pacientes/` | auth | Crear |
| PATCH | `/pacientes/{id}` | auth | Update/activar/desactivar/expediente |
| DELETE | `/pacientes/{id}/eliminar-permanente` | admin | Hard delete |
| GET | `/pacientes/duplicados/nombres-similares` | auth | Trigram/soundex |
| POST | `/pacientes/merge` | admin | Merge duplicados |
| POST | `/pacientes/madre-hijo/{madre_id}` | auth | Crear desde madre |

### 6.3 Consultas Médicas

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/consultas/` | auth | Listar (15+ filtros) |
| GET | `/consultas/{id}` | auth | Por ID |
| POST | `/consultas/registro` | auth | Nueva consulta |
| PATCH | `/consultas/{id}` | auth | Actualizar |
| PATCH | `/consultas/{id}/reasignar-paciente` | admin | Reasignar |
| GET | `/consultas/pacienteId/{paciente_id}` | auth | Historial por paciente |
| DELETE | `/consultas/{id}` | auth | Desactivar |
| DELETE | `/consultas/{id}/eliminar` | admin | Hard delete |

### 6.4 Ciclos, Eventos, Citas

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/ciclos/consulta/{id}` | auth | Ciclos de una consulta |
| POST | `/ciclos/` | auth | Crear ciclo |
| GET | `/eventos/` | auth | Listar eventos |
| POST | `/eventos/` | auth | Crear (ingreso/evolución/egreso) |
| POST | `/citas/` | auth | Crear cita |
| GET | `/citas/` | auth | Listar (filtros) |
| GET | `/citas/disponibles` | auth | Disponibles |
| PUT | `/citas/{id}` | auth | Actualizar |

### 6.5 Médicos y Especialidades

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/medicos/` | public | Crear |
| GET | `/medicos/` | public | Listar (filtros) |
| PUT | `/medicos/{id}` | public | Actualizar |
| DELETE | `/medicos/{id}` | public | Eliminar |
| GET | `/especialidades/` | — | Catálogo |

### 6.6 Nacimientos y Constancias

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/nacimientos/` | auth | Crear |
| POST | `/nacimientos/desde-paciente/{id}` | auth | Desde paciente |
| GET | `/nacimientos/` | auth | Listar (6 filtros) |
| PATCH | `/nacimientos/{id}/neonatales` | auth | Actualizar neonatales |
| POST | `/nacimientos/sincronizar` | auth | Sincronizar madre-hijo + legacy |
| POST | `/constancias-nacimiento/` | auth | Crear |
| GET | `/constancias-nacimiento/` | auth | Listar |
| PUT | `/constancias-nacimiento/{id}` | auth | Update (guarda historial) |
| PATCH | `/constancias-nacimiento/{id}/estado-informe` | auth | Cambiar estado |

### 6.7 Defunciones

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/defunciones/` | auth | Crear |
| POST | `/defunciones/registrar/{paciente_id}` | auth | Registrar + marcar paciente F |
| GET | `/defunciones/` | auth | Listar (7 filtros) |
| POST | `/defunciones/sincronizar` | auth | Sincronizar desde estado pacientes |

### 6.8 SIGSA-3

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/sigsa3/` | auth | Listar (9 filtros) |
| POST | `/sigsa3/` | auth | Crear |
| POST | `/sigsa3/importar-excel` | auth | Importar Excel |
| POST | `/sigsa3/eliminar-por-ids` | admin | Eliminar por IDs |
| POST | `/sigsa3/eliminar-por-periodo` | admin | Eliminar por rango fechas |
| POST | `/sigsa3/asociar-medico` | auth | Asociar médico por personal_salud |
| POST | `/sigsa3/asociar-todo` | auth | Pipeline completo (5 pasos) |

### 6.9 Censo Camas, Procedimientos, Préstamos

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/censo-camas/` | auth | Crear registro |
| POST | `/censo-camas/upsert` | auth | Upsert |
| POST | `/censo-camas/bulk` | auth | Bulk create |
| POST | `/censo-camas/importar-csv` | auth | Importar CSV |
| GET | `/censo-camas/resumen/{fecha}` | auth | Resumen diario |
| GET | `/procedimientos/catalogo` | auth | Catálogo (filtros) |
| POST | `/procedimientos/` | auth | Crear realizado |
| GET | `/procedimientos/reporte` | auth | Reporte agregado |
| POST | `/prestamos/` | auth | Crear préstamo |

### 6.10 Estadísticas y Dashboard

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/totales/` | auth | 7 KPIs dashboard (cache 30s) |
| GET | `/estadisticas/consultas/pacientesAtendidos` | auth | Por tipo, especialidad, sexo |
| GET | `/estadisticas/consultas/hospitalizacion-infantil` | auth | >28d y <5años |
| GET | `/estadisticas/consultas/promedioDiario` | auth | Promedio diario por especialidad |
| GET | `/estadisticas/consultas/personal-hospital` | auth | Personal hospital |
| GET | `/estadisticas/consultas/estudiante-publico` | auth | Estudiantes públicos |
| GET | `/estadisticas/consultas/reingresos` | auth | Reingresos <8d / complicaciones |
| GET | `/estadisticas/consultas/reingresos-tipo3` | auth | Reingresos tipo 3 paginados |
| GET | `/estadisticas/consultas/mayores-a-7-dias` | auth | Consultas >7 días |
| GET | `/estadisticas/nacimientos` | auth | Stats nacimientos |
| GET | `/estadisticas/sigsa3/por-especialidad` | auth | SIGSA-3 por especialidad |
| GET | `/estadisticas/sigsa3/dx-frecuentes` | auth | Diagnósticos frecuentes |

### 6.11 IA y Chat

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/chat/consulta` | auth | NL→SQL (LLM, read-only, 10/min) |
| GET | `/chat/tablas` | auth | Tablas disponibles |
| POST | `/agente/consulta` | auth | Agente estadístico rule-based |
| POST | `/agente/feedback` | auth | Feedback para aprendizaje |
| GET | `/cie10/buscar` | auth | Búsqueda CIE-10 |
| POST | `/cie10/sugerir` | auth | Sugerir códigos con LLM |

### 6.12 Geografía y Externos

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/municipios/` | public | Municipios Guatemala |
| GET | `/municipios/departamentos` | public | Departamentos |
| GET | `/paises/` | public | Países ISO |
| GET | `/renap/persona` | auth | Consulta RENAP por CUI |

---

## 7. Mecanismos de Escalabilidad

### 7.1 Caché
- **fastapi-cache2** con Redis (fallback InMemory)
- `@cache(expire=30)` en totales (KPIs)
- `@cache(expire=3600)` en municipios, departamentos
- Prefix: `fah-cache`

### 7.2 Rate Limiting
- slowapi middleware global
- `@limiter.limit("5/minute")` en recuperación de password
- `10/min` en chat NL→SQL

### 7.3 Database Optimization
- **Pool**: configurable `DB_POOL_SIZE` (default 20), `DB_MAX_OVERFLOW` (default 40)
- **Read-only engine**: usuario dedicado `POSTGRES_RO_USER` para queries de chat
- **Índices GIN**: trigram en `nombre_completo`, `pg_trgm`
- **JSONB**: campos flexibles en pacientes (nombre, contacto, datos_extra, referencias)
- **Índices parciales**: unique condicional (cui, expediente NOT NULL)
- **Statement timeout**: 300s (write), 30s (read-only)

### 7.4 Middleware Stack
```
1. TrustedHostMiddleware
2. CORSMiddleware (origins from .env)
3. SlowAPIMiddleware (rate limiting)
4. AuditClientIPMiddleware (logging IP)
```

### 7.5 Background Tasks
- `BackgroundTasks` para envío de email de bienvenida al crear usuario

---

## 8. Patrones de Diseño por Módulo

### 8.1 Convención de Módulo (4 archivos)
```
modules/<nombre>/
├── router.py      # Endpoints FastAPI
├── schemas.py     # Pydantic models (request/response)
├── models.py      # SQLAlchemy ORM
└── service.py     # Lógica de negocio
```

### 8.2 Sub-routers (Paciente)
```
modules/pacientes/
├── router.py               # CRUD principal
├── duplicados_router.py    # Detección de duplicados
├── merge_router.py         # Merge de duplicados
└── recien_nacido_router.py # Crear desde madre
```

### 8.3 SIGSA-3 (módulo más complejo)
```
modules/sigsa3/
├── router.py           # CRUD + filtros
├── gestor_router.py    # Pipeline asociación masiva
├── importacion_router.py # Importación Excel
├── schemas.py
├── models.py
└── service.py
```

### 8.4 Patrón de Servicio
```python
#service.py pattern:
def crear_X(data, db) -> XModel:
    obj = XModel(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def listar_X(db, filtros, skip, limit) -> tuple[list, int]:
    query = db.query(XModel)
    # apply filters...
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total
```

---

## 9. Áreas de Mejora y Escalabilidad

### 9.1 Deuda Técnica Identificada

| Área | Problema | Solución sugerida |
|------|----------|-------------------|
| laboratorios/ | Solo modelo ORM, sin router/service | Implementar CRUD completo |
| rayos_x/ | Solo modelo ORM, sin router/service | Implementar CRUD completo |
| quirofano/ | 6 modelos catálogo, lógica incompleta | Desarrollar workflow quirúrgico |
| models sin tests | Varios módulos sin cobertura | Agregar tests |
| SQL raw en estadisticas | Queries SQL directas con `text()` | Considerar SQLAlchemy core queries |
| migrations | Scripts manuales, no usa Alembic | Migrar a Alembic |
| audit_log | Solo middleware de IP, no registra CRUD | Expandir a todos los módulos |

### 9.2 Módulos sin Router Activo

| Módulo | Modelos | Estado |
|--------|---------|--------|
| laboratorios | Laboratorios | ORM solamente |
| rayos_x | RayosX | ORM solamente |
| quirofano | 6 modelos catálogo | Modelos definidos |

### 9.3 Funcionalidades Faltantes

1. **Reportes PDF**: Solo hay un PDF hardcodeado (`informe-de-Defuncion.pdf`)
2. **Exportación Excel/CSV**: Solo SIGSA-3 tiene importación Excel
3. **Notificaciones push**: No implementado
4. **Multi-tenancy**: No hay soporte para múltiples hospitales
5. **API versioning**: Todo en v1 implícito (`/fah/`)
6. **Webhooks**: No hay sistema de eventos internos
7. **Colas de trabajo**: No hay Celery/RQ para tareas pesadas
8. **Monitoring**: No hay métricas (Prometheus/Grafana)
9. **Documentación de modelos DB**: Solo `docs/esquema_bd.md`

### 9.4 Oportunidades de Escalabilidad

| Funcionalidad | Módulos afectados | Complejidad |
|---------------|-------------------|-------------|
| Exportación masiva PDF | constancias_nacimiento, defunciones, nacimientos | Media |
| Dashboard websockets | totales, estadisticas | Alta |
| Batch processing (SIGSA-3) | sigsa3, personal_salud | Media |
| Workflow aprobación | constancias_nacimiento, defunciones | Alta |
| Búsqueda full-text avanzada | pacientes, consultas | Baja |
| API pública (docs abiertos) | todos | Baja |
| CI/CD pipeline | tests, deploy.sh | Baja |
| Alembic migrations | migrations/ | Media |

---

## 10. Dependencias Externas

| Servicio | Uso | Config |
|----------|-----|--------|
| PostgreSQL 18 | DB principal | POSTGRES_* |
| Redis | Caché distribuido | REDIS_URL |
| SMTP Gmail | Envío emails | MAIL_* |
| Ollama / OpenAI | LLM (CIE-10 + Chat) | CIE10_LLM_*, CHAT_LLM_* |
| RENAP | Consulta personas | HTTP externo |
| Opencode Server | Gateway a modelos LLM | OPENCODE_* |

---

## 11. Variables de Entorno Críticas

```env
# Database
POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST / POSTGRES_PORT / POSTGRES_DB
POSTGRES_RO_USER / POSTGRES_RO_PASSWORD  # Read-only para chat

# Security
SECRET_KEY / ACCESS_TOKEN_EXPIRE_MINUTES

# Mail
MAIL_USERNAME / MAIL_PASSWORD / MAIL_FROM / MAIL_SERVER / MAIL_PORT

# LLM
CIE10_LLM_PROVIDER / CIE10_LLM_MODEL / CIE10_LLM_API_KEY / CIE10_LLM_BASE_URL
CHAT_LLM_PROVIDER / CHAT_LLM_MODEL / CHAT_LLM_API_KEY / CHAT_LLM_BASE_URL
OLLAMA_HOST

# Cache
REDIS_URL

# Server
WORKERS / DB_POOL_SIZE / DB_MAX_OVERFLOW / DB_POOL_RECYCLE
CORS_ORIGINS / ALLOWED_HOSTS

# External
OPENCODE_SERVER_URL / OPENCODE_SERVER_PASSWORD
```

---

## 12. Tests

| Archivo | Cobertura |
|---------|-----------|
| test_routers.py | Tests de endpoints principales |
| test_comprehensive.py | Tests integrales (todos los módulos) |
| test_remaining_endpoints.py | Endpoints faltantes |
| test_defunciones.py | Módulo defunciones |
| test_duplicados_service.py | Duplicados pacientes |
| test_prestamos.py / test_prestamos_endpoint.py | Préstamos |
| test_agente.py / test_agente_endpoint.py | Agente estadístico |
| test_sigsa3_registros.py | SIGSA-3 registros |
| test_vector_logic.py | Lógica de vectores |

**Ejecutar**: `pytest tests/ -v`

---

## 13. Scripts Útiles

```bash
# Desarrollo
uvicorn main:app --reload

# Tests
pytest tests/ -v

# Deploy
./deploy.sh

# Migraciones SQL
psql -d hospital -f migrations/019_recrear_unaccent.sql

# Optimización
psql -d hospital -f sql/perf_optimizations.sql
```

---

## 14. Mapa de Navegación Rápida

- **¿Necesitas agregar un nuevo módulo?** → Copiar estructura de `modules/encamamiento/` (simple)
- **¿Necesitas modificar pacientes?** → `modules/pacientes/` (4 sub-routers)
- **¿Necesitas agregar estadística?** → `modules/estadisticas/service.py` (SQL raw)
- **¿Necesitas autenticación?** → `core/security.py` + `get_current_user`
- **¿Necesitas caché?** → `@cache(expire=N)` de fastapi-cache2
- **¿Necesitas migrar DB?** → `migrations/` + `docs/esquema_bd.md`
- **¿Necesitas tests?** → `tests/` + `pytest tests/ -v`
- **¿Necesitas email?** → `core/mail.py` + `modules/users/service.py::send_welcome_email`
