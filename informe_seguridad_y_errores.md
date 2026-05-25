# Informe de Seguridad y Manejo de Errores

> **Proyecto:** back-sys v2.0.0 — Sistema de Gestión Hospitalaria  
> **Framework:** FastAPI + SQLAlchemy + PostgreSQL  
> **Fecha del análisis:** Mayo 2026  

---

## Tabla de Contenidos

1. [Manejo de Errores — Estado Actual](#1-manejo-de-errores--estado-actual)
2. [Vulnerabilidades de Seguridad](#2-vulnerabilidades-de-seguridad)
3. [Recomendaciones de Implementación](#3-recomendaciones-de-implementación)

---

## 1. Manejo de Errores — Estado Actual

### 1.1 Patrones Existentes (Buenos)

| Patrón | Archivo | Líneas | Descripción |
|--------|---------|--------|-------------|
| `IntegrityError` + `rollback()` | `routes/pacientes.py` | 252-270, 394-412 | Captura violaciones de unicidad en DB y hace rollback |
| `try/finally` para cerrar DB session | `database/db.py` | 59-62 | Garantiza `db.close()` siempre |
| `HTTPException` re-lanzada tras rollback | `routes/merge_paciente.py` | 319-327 | Rollback + re-lanzar excepción HTTP específica |
| 404 consistente para recursos no encontrados | Todos los routes | — | Mensaje descriptivo con ID del recurso |
| 403 para autorización fallida | Varios | — | Mensajes claros sin revelar datos internos |
| `with_for_update()` para secuencias concurrentes | `utils/expediente.py` | 59, 80, 101 | Lock pesimista para evitar race conditions |
| 502 para errores de API externa | `routes/renap.py` | 97-102 | Gateway timeout, apropiado para upstream |
| Manejo estructurado de errores de servicios externos | `services/renap_service.py` | 46-51 | Respuesta con `error=True` sin leaks |
| Aislamiento de errores en background tasks | `routes/user.py` | 209-210 | No afecta la respuesta HTTP si falla el email |

### 1.2 Patrones Malos / Críticos

#### 🔴 CRÍTICO: `except: pass` silencioso

**Archivo:** `routes/pacientes.py:151-152`
```python
try:
    query = query.filter(PacienteModel.fecha_nacimiento == fecha_nac)
except:
    pass
```
- Traga **todas** las excepciones (incluyendo `KeyboardInterrupt`, `SystemExit`)
- Oculta errores de tipo de datos, formato de fecha, etc.
- **Solución:** Especificar excepción, al menos `except Exception`, y loguear.

**Archivo:** `schemas/paciente.py:219`
```python
except:
    data["nombre_completo"] = ""
```
- Mismo problema: bare `except` dentro de un model_validator de Pydantic
- Oculta `TypeError`, `KeyError`, etc.

#### 🔴 CRÍTICO: Código muerto ejecutándose al importar

**Archivo:** `utils/expediente.py:156-178`
```python
# Fuera de cualquier función — se ejecuta al importar el módulo
anio_actual = int(datetime.now().strftime("%y"))
control = db.query(DefuncionControl)...  # ¡db no está definido!
```
- Esto **rompe el arranque del servidor** porque `db` no existe en ámbito global.

#### 🔴 CRÍTICO: Sin manejadores globales de excepción

**Archivo:** `main.py` — No hay `@app.exception_handler(...)` registrados.
- Sin `exception_handler(Exception)` — toda excepción no capturada retorna el HTML por defecto de Starlette
- Sin `exception_handler(RequestValidationError)` — errores de validación Pydantic usan formato default
- En producción con `DEBUG=True`, se mostrarían stack traces completos al cliente

#### 🟠 ALTO: Leak de detalles de excepción al cliente

Múltiples endpoints usan `str(e)` en el mensaje de error:

| Archivo | Línea | Código |
|---------|-------|--------|
| `routes/consultas.py` | 400, 532 | `detail=f"Error al actualizar: {str(e)}"` |
| `routes/citas.py` | 195 | `detail=f"Error al actualizar cita: {str(e)}"` |
| `routes/expediente.py` | 49-52 | `detail=f"Error: {str(e)}"` |
| `routes/ciclos.py` | 102 | `detail=f"Error al crear ciclo: {str(e)}"` |
| `routes/merge_paciente.py` | 326 | `detail=f"Error durante merge: {str(e)}"` |
| `routes/total.py` | 165 | `detail=f"Error al obtener totales: {str(e)}"` |

**Impacto:** Revela rutas del servidor, estructura de DB, tipos de datos, nombres de columnas.

#### 🟠 ALTO: Endpoints sin try/except en `db.commit()`

Múltiples endpoints no capturan `IntegrityError` ni otras excepciones de DB:

| Archivo | Línea | Endpoint |
|---------|-------|----------|
| `routes/user.py` | 98, 127, 143, 170 | CRUD usuarios |
| `routes/medicos.py` | 22, 90 | Crear/actualizar médico |
| `routes/citas.py` | 39, 212 | Crear/eliminar cita |
| `routes/municipios.py` | 67, 89, 108 | CRUD municipios |
| `routes/prestamos.py` | 40, 65, 112, 135 | CRUD préstamos |
| `routes/constancia_nacimiento.py` | 41, 131, 144 | CRUD constancias |
| `routes/eventos.py` | 93, 117, 136 | CRUD eventos |
| `routes/nacimientos_legacy.py` | 57 | Actualizar legacy |

**Impacto:** Cualquier violación de constraint (FK, unique) retorna 500 con stack trace.

#### 🟠 ALTO: Sin logging estructurado

**En todo el proyecto:** No se usa el módulo `logging` de Python.
- Todo es `print()` — no hay niveles (INFO, WARNING, ERROR)
- No hay formato consistente
- No hay rotación de logs
- En producción, `print()` va a stdout del contenedor sin estructura

### 1.3 Patrones Inconsistentes

| Aspecto | Endpoints con manejo | Endpoints sin manejo |
|---------|---------------------|----------------------|
| `try/except` + `rollback()` en `commit()` | `pacientes.py`, `merge_paciente.py`, `consultas.py`, `citas.py` | `user.py`, `medicos.py`, `municipios.py`, `prestamos.py`, `constancia_nacimiento.py`, `eventos.py`, `recienNacido.py` |
| Formato de error | `{"detail": "..."}` (default FastAPI) | `{"detail": f"Error: {str(e)}"}` con leak |
| Códigos de error | 400, 404, 403, 401 | 500 genérico con o sin detalles |
| Rollback en error | Algunos sí | Muchos no |

### 1.4 Patrones Ausentes por Completo

- **Manejador global de excepciones** (`@app.exception_handler`)
- **Manejador de `RequestValidationError`** — mensajes default de Pydantic
- **Clases de excepción personalizadas**
- **Logging** (`import logging` no aparece en ningún archivo)
- **Auditoría de operaciones** (quién creó/modificó/eliminó qué y cuándo)
- **Retry lógica** para fallos transitorios de DB
- **Envelope de respuesta** consistente tipo `{"success": false, "error": {...}}`

---

## 2. Vulnerabilidades de Seguridad

### 2.1 Resumen por Severidad

| Severidad | Cantidad | Hallazgos Clave |
|-----------|----------|-----------------|
| 🔴 **CRÍTICA** | 5 | API key hardcodeada, TLS key en git, `.env` fuera de `.gitignore`, password reset sin auth, DB password débil |
| 🟠 **ALTA** | 7 | TLS verification off, CORS abierto, JWT secret default, SMTP pass plano, rate limiting ausente, DEBUG en producción, defaults hardcodeados |
| 🟡 **MEDIA** | 11 | Account enumeration, SQL injection potencial, debug endpoint expuesto, password policy débil, audit logging ausente, auth duplicada, sin revocación de tokens, mail cert off, hardcoded "admin", rol hardcoded |
| 🟢 **BAJA** | 6 | URLs hardcodeadas, security headers faltantes, long timeout, data exposure potencial, mass assignment, geo codes hardcodeados |

### 2.2 Hallazgos Críticos

#### 🔴 C01 — API Key Hardcodeada

**Archivo:** `services/renap_service.py:15`
```python
API_KEY = "b6039f4a35ae824f9d7abe6a8bda8f7d5e590cfd9ee53ba87dce37b890588fb3"
```
**Impacto:** Cualquiera con acceso al repo puede consultar la base de datos nacional de personas (RENAP/MSPAS).
**Solución:** Mover a variable de entorno, rotar la clave inmediatamente.

#### 🔴 C02 — Certificado TLS Cliente en Git

**Archivos:**
- `services/ssl/client.key.pem`
- `services/ssl/client.cert.pem`

**Impacto:** La clave privada del certificado cliente para autenticarse con MSPAS está en texto plano en el repo. Cualquiera puede impersonar al hospital.
**Solución:**
```bash
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch app/services/ssl/client.key.pem' --prune-empty --tag-name-filter cat -- --all
echo "*.key.pem" >> .gitignore
echo "*.cert.pem" >> .gitignore
```
Además, rotar los certificados con MSPAS.

#### 🔴 C03 — `.env` Fuera de `.gitignore`

**Archivo:** `.gitignore` — No contiene `.env`

**Impacto:** El archivo `.env` contiene: `POSTGRES_PASSWORD=secreto123`, `SECRET_KEY`, `MAIL_PASSWORD`, `DEBUG=true`. Si alguien hace `git add .` y commitea, todas las credenciales de producción quedan expuestas.
**Solución:**
```
# En .gitignore
.env
.env.*
```
```bash
git rm --cached .env
```

#### 🔴 C04 — Password Reset Sin Verificación

**Archivo:** `routes/user.py:131-145`
```python
@router.patch("/recuperar")
def recuperar_contraseña(data: RecuperarPassword, db: Session = Depends(get_db)):
    usuario = db.query(UserModel).filter(UserModel.email == data.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password = hash_password(data.password)
    db.commit()
    return {"message": "Contraseña actualizada correctamente"}
```
**Impacto:** Cualquier atacante que conozca o adivine un email válido puede cambiar la contraseña de ese usuario inmediatamente. Sin autenticación, sin token, sin verificación.
**Solución:** Requerir autenticación (admin) o implementar flujo con token por correo.

#### 🔴 C05 — Password Débil por Defecto en DB

**Archivos:** `.env:10`, `database/db.py:20`
```
POSTGRES_PASSWORD=secreto123
```
**Impacto:** La base de datos PostgreSQL tiene una contraseña débil con fallback hardcodeado. Un atacante con acceso a la red interna puede acceder a todos los expedientes médicos (datos de salud protegidos).
**Solución:**
```python
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD no configurada")
```

### 2.3 Hallazgos Altos

#### 🟠 A01 — TLS Verification Disabled (RENAP)

**Archivo:** `services/renap_service.py:27`
```python
verify=False,  # ← Ignora certificado vencido del servidor
```
**Impacto:** MITM permite interceptar consultas de personas (nombres, CUIs, fechas de nacimiento).
**Solución:** Habilitar verificación TLS y resolver el certificado vencido con MSPAS.

#### 🟠 A02 — TLS Verification Disabled (Mail)

**Archivo:** `config/mail_config.py:19`
```python
VALIDATE_CERTS=False,
```
**Impacto:** MITM en comunicaciones de email (reset de contraseñas, bienvenidas).
**Solución:** `VALIDATE_CERTS=True`

#### 🟠 A03 — CORS Misconfigured

**Archivo:** `main.py:80-86`
```python
allow_origins=["*"],
allow_credentials=True,
```
**Impacto:** Cualquier sitio web puede hacer peticiones autenticadas desde el navegador del usuario. Violación de especificación CORS.
**Solución:**
```python
allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
```

#### 🟠 A04 — JWT Secret Default Débil

**Archivo:** `database/config.py:20-23`
```python
SECRET_KEY = os.getenv("SECRET_KEY", "e87cbfc88ff202c6442638d03d576513d01c153e8e1bdeb2eebc4832088ec9be")
```
**Impacto:** Si el `.env` no está configurado, se usa un secret hardcodeado en el código fuente. Cualquiera puede forjar JWTs.
**Solución:** No usar default; forzar configuración:
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no configurada")
```

#### 🟠 A05 — Sin Rate Limiting en Login

**Archivo:** `auth/login.py:18-39`
**Impacto:** Fuerza bruta de contraseñas ilimitada.
**Solución:** Implementar con `slowapi` o similar:
```python
@router.post("/login")
@limiter.limit("5/minute")
def login(form_data, db, request: Request):
```

#### 🟠 A06 — DEBUG Habilitado

**Archivo:** `.env:48`
```
DEBUG=true
```
**Impacto:** FastAPI en modo debug muestra stack traces completos en respuestas de error.
**Solución:** Asegurar `DEBUG=false` en producción.

#### 🟠 A07 — Hardcoded Defaults en DB Config

**Archivo:** `database/db.py:19-23` — Todos los parámetros de conexión tienen defaults hardcodeados.
**Solución:** No usar defaults para credenciales; validar que existan.

### 2.4 Hallazgos Medios

| ID | Hallazgo | Archivo | Línea | Solución Propuesta |
|----|----------|---------|-------|-------------------|
| 🟡M01 | Account enumeration | `routes/auth.py` | 21-22 | Combinar chequeos (como ya hace `auth/login.py`) |
| 🟡M02 | SQL injection potencial | `routes/pacientes_duplicados.py` | 44 | Usar `comparison_map` en vez de f-string |
| 🟡M03 | Debug endpoint expuesto | `routes/pacientes.py` | 463-487 | Agregar `get_current_admin_user` o eliminar |
| 🟡M04 | Password policy débil | `schemas/user.py` | 37 | `min_length=8`, validar mayúscula+número+símbolo |
| 🟡M05 | Falta de auditoría | Todos | — | `logging` module + tabla `audit_log` |
| 🟡M06 | Sin revocación de tokens | `database/security.py` | — | Token blacklist con Redis o `jti` claim |
| 🟡M07 | Endpoints médicos sin auth | `routes/medicos.py` | 17,26,64,74,96 | Agregar `Depends(get_current_user)` |
| 🟡M08 | Rutas de auth duplicadas | `auth/login.py` vs `routes/auth.py` | — | Unificar en un solo módulo |
| 🟡M09 | Rol hardcodeado como string | `database/security.py` | 133 | Usar constante o Enum |
| 🟡M10 | "admin" en generate_hash.py | `generate_hash.py` | 5 | Usar variable de entorno o `getpass` |
| 🟡M11 | JWT expiración larga (24h default) | `database/config.py` | 25 | Reducir a 60 min, implementar refresh tokens |

---

## 3. Recomendaciones de Implementación

### 3.1 Manejo de Errores — Plan de Implementación

#### Fase 1 — Inmediata (Corregir bugs que rompen el servidor)

```python
# utils/expediente.py: Eliminar líneas 156-178 (código duplicado fuera de función)
# La función generar_defuncion() termina en línea 155. Borrar líneas 156-178.
```

```python
# routes/pacientes.py:151 — Reemplazar except: pass
except (ValueError, TypeError) as e:
    logger.warning(f"Formato de fecha_nac inválido: {fecha_nac} — {e}")
```

```python
# schemas/paciente.py:219 — Reemplazar bare except
except (KeyError, TypeError, ValueError) as e:
    logger.error(f"Error generando nombre_completo: {e}")
    data["nombre_completo"] = ""
```

#### Fase 2 — Global Exception Handlers

```python
# main.py — Agregar manejadores globales
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Error de validación en los datos enviados"
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Error no manejado")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )
```

#### Fase 3 — Middleware de Errores + Logging

```python
# main.py — Agregar logging estructurado
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("hospsys")
```

#### Fase 4 — Patrón Consistente para Todos los Endpoints Write

```python
# PATRÓN ESTÁNDAR para todos los endpoints POST/PUT/PATCH/DELETE
@router.post("/ejemplo")
def crear_recurso(
    data: SchemaCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    try:
        # Validaciones de negocio
        # ...
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"IntegrityError creando recurso: {e}")
        raise HTTPException(
            status_code=400,
            detail="El recurso ya existe o tiene datos duplicados"
        )
    except Exception as e:
        db.rollback()
        logger.exception(f"Error creando recurso")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )
```

#### Fase 5 — Middleware de Auditoría

```python
# auditoria.py
class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            logger.info(
                f"{request.method} {request.url.path} "
                f"→ {response.status_code} | "
                f"user: {getattr(request.state, 'user_id', 'anonymous')} | "
                f"ip: {request.client.host}"
            )
        return response
```

### 3.2 Seguridad — Plan de Implementación

#### Día 1 — Correcciones Críticas

| Tarea | Archivo | Acción |
|-------|---------|--------|
| Agregar `.env` a `.gitignore` | `.gitignore` | Añadir `.env` `.env.*` |
| Remover TLS keys de git | `services/ssl/` | `git rm --cached`, `git filter-branch` |
| Rotar API key RENAP | `services/renap_service.py` | Mover a `os.getenv("RENAP_API_KEY")` |
| Proteger password reset | `routes/user.py` | Agregar `Depends(get_current_user)` |
| Rotar DB password | `.env` + `db.py` | Quitar fallback, usar pass fuerte |

#### Día 2 — Correcciones Altas

| Tarea | Archivo | Acción |
|-------|---------|--------|
| Habilitar TLS verify | `services/renap_service.py:27` | `verify=True` |
| Habilitar mail TLS verify | `config/mail_config.py:19` | `VALIDATE_CERTS=True` |
| Corregir CORS | `main.py:80-86` | Orígenes específicos desde env |
| Rate limiting login | `auth/login.py` | `slowapi` |
| DEBUG=false en prod | `.env` | Asegurar en despliegue |
| Rotar JWT secret | `config.py` | Quitar fallback, regenerar |

#### Día 3 — Correcciones Medias

| Tarea | Archivo | Acción |
|-------|---------|--------|
| Auth en endpoints médicos | `routes/medicos.py` | Agregar `Depends(get_current_user)` |
| Eliminar debug endpoint | `routes/pacientes.py` | O agregar admin check |
| Fortalecer password policy | `schemas/user.py` | `min_length=8`, validación fuerza |
| Unificar módulos auth | `auth/login.py` + `routes/auth.py` | Elegir uno, eliminar otro |
| Consolidated audit logging | Todos | Implementar `logging` |
| SQL injection fix | `routes/pacientes_duplicados.py` | Usar diccionario de SQL fragments |

#### Día 4+ — Hardening

| Tarea | Archivo | Acción |
|-------|---------|--------|
| Security headers middleware | `main.py` | `X-Content-Type-Options`, `X-Frame-Options`, HSTS |
| Token revocation | Nuevo archivo | Redis blacklist o `jti` claim |
| Refresh tokens | `database/security.py` | Short-lived access + long-lived refresh |
| Account lockout | `auth/login.py` | Bloquear tras N intentos fallidos |
| Captcha en login | `auth/login.py` | Después de 3 intentos fallidos |

### 3.3 Arquitectura de Errores Propuesta

```
Cliente HTTP
    │
    ▼
[Middleware: Seguridad (HSTS, CORS, Headers)]
    │
    ▼
[Middleware: Auditoría (log cada request)]
    │
    ▼
[Middleware: Rate Limiting]
    │
    ▼
[Dependencias: Auth (get_current_user)]
    │
    ▼
[Route Handler]
    │  ├── try: Lógica de negocio
    │  ├── except HTTPException: raise (deja pasar)
    │  ├── except IntegrityError: rollback + 400
    │  ├── except Exception: rollback + log + 500 genérico
    │  └── finally: (opcional)
    │
    ▼
[Global Exception Handlers]
    │  ├── RequestValidationError → 422 con detalles
    │  ├── HTTPException → según código
    │  └── Exception → 500 genérico (sin stack trace)
    │
    ▼
[Respuesta JSON consistente]
    {
        "success": true|false,
        "data": {...} | null,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "...",
            "details": [...]  // solo en desarrollo
        } | null
    }
```

### 3.4 Variables de Entorno Requeridas (Seguras)

```
# .env.example (COMMITEAR ESTO, NO .env)
POSTGRES_USER=
POSTGRES_PASSWORD=           # ¡sin default!
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hospital

SECRET_KEY=                   # ¡sin default! generar con secrets.token_hex(32)
ACCESS_TOKEN_EXPIRE_MINUTES=60

RENAP_API_KEY=                # ¡sin default!
RENAP_API_URL=https://salud-digital.mspas.gob.gt/personas
SSL_VERIFY=true

MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=noreply@hospital.gob.gt
MAIL_FROM_NAME=Hospital Tecpan

CORS_ORIGINS=http://localhost:3000,https://hgtecpan.duckdns.org

DEBUG=false
LOG_LEVEL=INFO
```

---

## 4. Resumen de Acciones Prioritarias

| Prioridad | Acción | Esfuerzo | Dependencias |
|-----------|--------|----------|-------------|
| 🔴 **DÍA 1** | `.env` a `.gitignore` + rotar credenciales | 30 min | Acceso a MSPAS |
| 🔴 **DÍA 1** | Eliminar TLS key de git history | 1 hora | `git filter-branch` |
| 🔴 **DÍA 1** | Proteger endpoint `/users/recuperar` | 15 min | Ninguna |
| 🔴 **DÍA 1** | Eliminar código muerto en `expediente.py:156-178` | 5 min | Ninguna |
| 🟠 **DÍA 2** | Corregir CORS | 10 min | URL frontend |
| 🟠 **DÍA 2** | Rate limiting en login | 1 hora | `slowapi` |
| 🟠 **DÍA 2** | TLS verify en RENAP + Mail | 15 min | Certificados válidos |
| 🟠 **DÍA 2** | Quitar `except: pass` en `pacientes.py` y `paciente.py` | 10 min | Ninguna |
| 🟠 **DÍA 3** | Auth en endpoints de médicos | 30 min | Ninguna |
| 🟠 **DÍA 3** | Global exception handlers | 1 hora | Ninguna |
| 🟡 **DÍA 3** | Logging estructurado | 2 horas | Ninguna |
| 🟡 **DÍA 4** | Auditoría de operaciones | 3 horas | Diseño de tabla/log |
| 🟡 **DÍA 4** | Fortalecer password policy | 30 min | Ninguna |
| 🟢 **DÍA 5+** | Security headers, token revoc, refresh tokens | 4 horas | Redis (opcional) |

---

*Documento generado automáticamente mediante análisis estático del código fuente.*
