# Análisis OWASP Top 10 — 2021

> **Proyecto:** back-sys — Sistema de Gestión Hospitalaria (FastAPI + PostgreSQL)  
> **Propósito:** Identificar y clasificar vulnerabilidades según el estándar OWASP Top 10 2021  
> **Fecha:** Mayo 2026

---

## ¿Qué es OWASP Top 10?

El **OWASP Top 10** es un documento de concientización sobre seguridad web publicado por

**OWASP (Open Web Application Security Project)** . Representa un consenso general sobre los

riesgos de seguridad más críticos para aplicaciones web. Se actualiza cada 3-4 años; la versión

vigente es 2021.

No es una lista exhaustiva, sino una **priorización de riesgos** basada en datos reales de

incidentes. Cada categoría agrupa vulnerabilidades con causas y mitigaciones similares.

Las categorías están ordenadas por: frecuencia de ocurrencia, explotabilidad, impacto técnico

y prevalencia en datos de la industria.

---

## Mapeo Rápido

| # | Categoría OWASP | ¿Afecta al proyecto? | Severidad estimada |
|---|-----------------|----------------------|--------------------|
| A01 | Broken Access Control | **SÍ** 🔴 | CRÍTICA |
| A02 | Cryptographic Failures | **SÍ** 🔴 | CRÍTICA |
| A03 | Injection | **SÍ** 🟡 | MEDIA |
| A04 | Insecure Design | **SÍ** 🔴 | CRÍTICA |
| A05 | Security Misconfiguration | **SÍ** 🟠 | ALTA |
| A06 | Vulnerable & Outdated Components | **SÍ** 🟡 | MEDIA |
| A07 | Identification & Auth Failures | **SÍ** 🔴 | CRÍTICA |
| A08 | Software & Data Integrity Failures | **SÍ** 🟠 | ALTA |
| A09 | Security Logging & Monitoring Failures | **SÍ** 🟠 | ALTA |
| A10 | SSRF | **SÍ** 🟢 | BAJA |

---

## A01 — Broken Access Control (Control de Acceso Roto)

### ¿Qué es?

Ocurre cuando un usuario puede acceder a recursos o ejecutar acciones para las que no tiene

permiso. Esto incluye: escalación de privilegios, manipulación de identificadores, navegación

forzada, y omisión de controles de acceso.

### Hallazgos en el Proyecto

#### 🔴 A01-1: Endpoints CRUD de Médicos Sin Autenticación

**Archivo:** `app/routes/medicos.py`

Las siguientes operaciones NO requieren autenticación:

- `POST /medicos/` (línea 17) — Crear médicos
- `GET /medicos/` (línea 26) — Listar todos los médicos
- `GET /medicos/{id}` (línea 64) — Ver detalle de médico
- `PUT /medicos/{id}` (línea 74) — Actualizar médico
- `DELETE /medicos/{id}` (línea 96) — Eliminar médico

```python
@router.post("/", response_model=MedicoOut, status_code=201)
def crear_medico(
    data: MedicoCreate,
    db: Session = Depends(get_db),
    # ⚠️ FALTA: current_user: UserModel = Depends(get_current_user)
):
```

**Impacto:** Cualquier persona sin autenticarse puede crear, modificar o eliminar registros de

médicos. Esto incluye acceso a datos personales (DPI, colegiado, especialidad).

**Explicación OWASP:** Esto viola el principio de "denegar por defecto" (*default deny*). Todo

acceso a recursos debe requerir autenticación explícita, y cada operación debe verificar que el

usuario autenticado tenga el rol adecuado.

#### 🔴 A01-2: Endpoints de Nacimientos Legacy Sin Autenticación

**Archivo:** `app/routes/nacimientos_legacy.py`

- `GET /nacimientos-legacy/` (línea 14) — Listar registros legacy
- `PUT /nacimientos-legacy/{id}` (línea 48) — Actualizar registro

**Impacto:** Datos personales de nacimientos (madre, DPI, pasaporte) accesibles públicamente.

#### 🟡 A01-3: Debug Endpoint Expone Datos Sensibles

**Archivo:** `app/routes/pacientes.py:463-487`

```python
@router.get("/debug/count")
def debug_count(db: Session = Depends(get_db)):
    """⚠️ QUITAR EN PRODUCCIÓN"""
```

Aunque dice "quitar en producción", sigue ahí. Retorna IDs, expedientes, CUIs y nombre completo

de pacientes. Cualquier usuario autenticado (no solo admin) puede acceder.

#### 🟡 A01-4: Debug Endpoint en DB URL

**Archivo:** `app/routes/pacientes.py:465` — El endpoint `GET /pacientes/debug/count` está

montado bajo el router de pacientes y expone conteos y datos de muestra.

### Recomendación General A01

```python
# Decorador reusable para rutas que requieren admin
from functools import wraps
from fastapi import Depends

def require_admin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # FastAPI inyecta current_user si está como dependencia
        return func(*args, **kwargs)
    return wrapper

# Aplicar a nivel de router
router = APIRouter(dependencies=[Depends(get_current_user)])

# O por endpoint
@router.post("/", dependencies=[Depends(get_current_admin_user)])
def crear_medico(data: MedicoCreate, db: Session = Depends(get_db)):
    ...
```

---

## A02 — Cryptographic Failures (Fallos Criptográficos)

### ¿Qué es?

Antes llamado "Sensitive Data Exposure". Ocurre cuando datos sensibles no están protegidos

adecuadamente: contraseñas débiles, certificados inválidos, secretos hardcodeados, cifrado

ausente o mal implementado.

### Hallazgos en el Proyecto

#### 🔴 A02-1: API Key Hardcodeada

**Archivo:** `app/services/renap_service.py:15`

```python
API_KEY = "b6039f4a35ae824f9d7abe6a8bda8f7d5e590cfd9ee53ba87dce37b890588fb3"
```

**Impacto:** Esta llave da acceso a la base de datos nacional de personas (RENAP/MSPAS). Al

estar en texto plano en el código fuente, cualquier persona con acceso al repositorio puede

consultar datos personales de ciudadanos guatemaltecos.

**Explicación OWASP:** Los secretos criptográficos (API keys, tokens, contraseñas) NUNCA deben

almacenarse en el código fuente. Deben estar en variables de entorno o en un gestor de secretos.

#### 🔴 A02-2: Clave Privada TLS en el Repositorio

**Archivo:** `app/services/ssl/client.key.pem`

La clave privada del certificado cliente TLS está en texto plano dentro del repositorio git.

**Impacto:** Cualquiera con acceso al repo puede:
- Suplantar la identidad del hospital ante MSPAS
- Descifrar tráfico TLS histórico (si fue capturado)
- Usar el certificado más allá de su alcance previsto

#### 🔴 A02-3: Contraseña de Base de Datos Débil con Default

**Archivo:** `app/database/db.py:20`

```python
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secreto123")
```

`.env`: `POSTGRES_PASSWORD=secreto123`

**Impacto:** "secreto123" es una contraseña débil (palabra en español + número secuencial).

Un atacante con acceso a la red interna puede realizar fuerza bruta contra PostgreSQL y acceder

a todos los expedientes médicos.

#### 🔴 A02-4: Secreto JWT con Default en Código

**Archivo:** `app/database/config.py:20-23`

```python
SECRET_KEY = os.getenv("SECRET_KEY", "e87cbfc88ff202c6442638d03d576513d01c153e8e1bdeb2eebc4832088ec9be")
```

**Impacto:** Si el `.env` no está configurado, el sistema usa un secreto hardcodeado. Cualquiera

con acceso al código puede forjar JWTs válidos para cualquier usuario, incluyendo administradores.

#### 🔴 A02-5: Contraseña SMTP en Texto Plano

**Archivo:** `.env:34`

```
MAIL_PASSWORD="gdjv zqbu zorp ifau"
```

**Impacto:** Esta es una contraseña de aplicación de Gmail. Permite enviar correos desde la

cuenta oficial del hospital.

#### 🟠 A02-6: TLS Verification Deshabilitado (RENAP)

**Archivo:** `app/services/renap_service.py:27`

```python
verify=False,  # Ignora certificado vencido del servidor
```

**Impacto:** Todo el tráfico hacia MSPAS viaja sin verificar la identidad del servidor

remoto. Un atacante en la red puede interceptar y modificar las respuestas (MITM).

**Explicación OWASP:** Deshabilitar la verificación TLS anula por completo el propósito del

cifrado. Es como poner una puerta blindada pero dejarla abierta.

#### 🟠 A02-7: Mail TLS Verification Deshabilitado

**Archivo:** `app/config/mail_config.py:19`

```python
VALIDATE_CERTS=False,
```

**Impacto:** Los correos electrónicos (incluyendo bienvenida y potenciales reseteos de

contraseña) viajan sin verificar la identidad del servidor SMTP.

### Recomendación General A02

```python
# database/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str  # Sin default — fallará si no está configurado
    POSTGRES_PASSWORD: str
    RENAP_API_KEY: str
    MAIL_PASSWORD: str
    SSL_VERIFY: bool = True
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()  # Lanza error si faltan variables requeridas
```

---

## A03 — Injection (Inyección)

### ¿Qué es?

Ocurre cuando datos no confiables son enviados a un intérprete como parte de un comando o

consulta. Los más comunes: SQL, NoSQL, OS command, LDAP, Expression Language.

### Hallazgos en el Proyecto

#### 🟢 A03-1: SQL Injection Potencial (Bajo Riesgo Actual)

**Archivo:** `app/routes/pacientes_duplicados.py:44`

```python
sql_query = text(f"""
    WITH datos_normalizados AS (
        ...
        AND {comparacion}
        ...
    )
""")
```

**Análisis:** La variable `comparacion` se construye a partir del parámetro `metodo` que está

tipado como `Literal["trigram", "soundex", "levenshtein"]`. FastAPI/Pydantic valida que solo

sea uno de esos tres valores. Sin embargo, el patrón de usar f-strings con `text()` es inherentemente

peligroso: si en el futuro se cambia el tipo a `str` o se agrega una ruta que acepte entrada

del usuario, se abre un vector de SQL injection.

**Explicación OWASP:** Aunque las consultas SQLAlchemy ORM son parametrizadas (previniendo

injection en la mayoría del código), el uso de `text()` con interpolación de strings anula

esa protección. La regla de oro es: **nunca concatenar strings en SQL, siempre usar bind params**.

```sql
-- MAL:
text(f"WHERE nombre = '{valor}'")

-- BIEN:
text("WHERE nombre = :valor").bindparams(valor=valor)
```

#### ✅ A03-2: SQLAlchemy ORM — Correcto

El 95%+ de las consultas del proyecto usan SQLAlchemy ORM con filtros como:

```python
query = db.query(PacienteModel).filter(PacienteModel.nombre['primer_nombre'].astext.ilike(f"%{nombre}%"))
```

Aunque el valor del usuario va dentro del `ilike()`, SQLAlchemy lo parametriza internamente.

No hay riesgo de SQL injection aquí.

### Recomendación A03

```python
# routes/pacientes_duplicados.py — Refactorizar
COMPARACIONES = {
    "trigram": "similarity(a.primer_nombre, b.primer_nombre) >= :similitud",
    "soundex": "a.soundex_nombre = b.soundex_nombre",
    "levenshtein": "levenshtein(a.primer_nombre, b.primer_nombre) <= :distancia_max",
}

comparacion_sql = COMPARACIONES[metodo]
sql_query = text(f"""
    WITH datos_normalizados AS (
        SELECT id, primer_nombre, segundo_nombre, primer_apellido,
               segundo_apellido, fecha_nacimiento
        FROM pacientes
        WHERE estado = 'A'
    )
    SELECT a.id, b.id, {comparacion_sql} AS similitud
    FROM datos_normalizados a
    JOIN datos_normalizados b ON ...
""")
sql_query = sql_query.bindparams(similitud=similitud_minima)
```

---

## A04 — Insecure Design (Diseño Inseguro)

### ¿Qué es?

Esta categoría se introdujo en 2021 para capturar vulnerabilidades que no son errores de

implementación sino fallos en el diseño de la aplicación. Incluye: falta de controles de

seguridad en el diseño de la arquitectura, lógica de negocio insegura, flujos de autenticación

mal diseñados.

### Hallazgos en el Proyecto

#### 🔴 A04-1: Password Reset Sin Verificación — Falla de Diseño

**Archivo:** `app/routes/user.py:131-145`

```python
@router.patch("/recuperar")
def recuperar_contraseña(
    data: RecuperarPassword,
    db: Session = Depends(get_db)
    # ⚠️ Sin autenticación, sin token, sin verificación
):
    usuario = db.query(UserModel).filter(UserModel.email == data.email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password = hash_password(data.password)
    db.commit()
    return {"message": "Contraseña actualizada correctamente"}
```

**Impacto:** Cualquier persona que conozca un email válido puede cambiar la contraseña de ese

usuario. Esto es un **defecto de diseño**, no un bug de implementación. El flujo completo de

recuperación de contraseña está ausente.

**Explicación OWASP:** Un diseño seguro de recuperación de contraseña debe incluir:

1. **Paso 1:** Usuario solicita recuperación → sistema envía token por email
2. **Paso 2:** Usuario presenta token + nueva contraseña → sistema verifica token y actualiza
3. El token debe ser: único, crypto-aleatorio, con expiración (15-30 min), de un solo uso

```python
# Diseño correcto:
@router.post("/solicitar-recuperacion")
def solicitar_recuperacion(email: str, db: Session = Depends(get_db)):
    usuario = db.query(UserModel).filter(UserModel.email == email).first()
    if not usuario:
        return {"message": "Si el email existe, recibirás instrucciones"}
    token = secrets.token_urlsafe(32)
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=15)
    usuario.reset_token = hash_token(token)  # Hash, no texto plano
    usuario.reset_token_exp = expiracion
    db.commit()
    enviar_email(email, f"Tu token: {token}")  # Enlace real en producción
    return {"message": "Si el email existe, recibirás instrucciones"}

@router.post("/confirmar-recuperacion")
def confirmar_recuperacion(email: str, token: str, new_password: str, db: Session = Depends(get_db)):
    usuario = db.query(UserModel).filter(
        UserModel.email == email,
        UserModel.reset_token_exp > datetime.now(timezone.utc)
    ).first()
    if not usuario or not verify_token(token, usuario.reset_token):
        raise HTTPException(400, "Token inválido o expirado")
    usuario.password = hash_password(new_password)
    usuario.reset_token = None
    usuario.reset_token_exp = None
    db.commit()
    return {"message": "Contraseña actualizada"}
```

#### 🟡 A04-2: Diseño Sin Bloqueo de Cuenta

No hay mecanismo de bloqueo tras N intentos fallidos de inicio de sesión. El diseño asume que

nunca ocurrirá un ataque de fuerza bruta.

**Explicación OWASP:** El diseño debe incluir defensa en profundidad (*defense in depth*):

- Capa 1: Rate limiting (slowapi)
- Capa 2: Bloqueo temporal tras 5 fallos
- Capa 3: CAPTCHA tras 3 fallos
- Capa 4: Notificación al usuario por email tras bloqueo

#### 🟡 A04-3: Sin Revocación de Tokens JWT

Una vez emitido un JWT, no se puede invalidar hasta que expire (hasta 24h después). Si un token

es robado, el atacante tiene acceso permanente por 24 horas.

**Explicación OWASP:** El diseño de JWTs debe considerar la revocación. Opciones:

- **Blacklist (Redis):** Tokens inválidos se almacenan con su tiempo de expiración
- **Token version (`jti`):** Cada usuario tiene un `token_version` en DB; al cambiar password,
  se incrementa la versión y los tokens viejos son inválidos
- **Refresh tokens:** Access tokens de corta duración (15 min) + refresh tokens de larga
  duración (7 días) que sí pueden revocarse

### Recomendación General A04

Todo endpoint que maneje datos sensibles debe seguir el principio de **"secure by design"** :

1. Definir los requisitos de seguridad ANTES de implementar
2. Aplicar el principio de mínimo privilegio
3. Validar que el diseño cubre los casos de borde (edge cases)
4. Incluir mecanismos de defensa en profundidad

---

## A05 — Security Misconfiguration (Configuración Insegura)

### ¿Qué es?

Ocurre cuando la aplicación, servidor, base de datos o framework están configurados de manera

insegura: puertos abiertos innecesarios, mensajes de error detallados, cabeceras HTTP faltantes,

configuraciones por defecto.

### Hallazgos en el Proyecto

#### 🟠 A05-1: CORS Totalmente Abierto

**Archivo:** `main.py:80-86`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ⚠️ Cualquier origen
    allow_credentials=True,   # ⚠️ Con credenciales
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Impacto:** `allow_origins=["*"]` + `allow_credentials=True` es una combinación inválida

según la especificación CORS. Diferentes navegadores manejan esto de forma distinta: algunos

bloquean la petición, otros permiten el envío de credenciales a cualquier origen.

**Explicación OWASP:** CORS es un mecanismo del navegador, no de seguridad a nivel de servidor.

Un CORS mal configurado permite que sitios maliciosos hagan peticiones autenticadas desde el

navegador de la víctima. La configuración correcta es:

```python
allow_origins=[
    "https://hgtecpan.duckdns.org",
    "http://localhost:3000",
],
```

#### 🟠 A05-2: DEBUG Habilitado

**Archivo:** `.env:48`

```
DEBUG=true
```

**Impacto:** Con `DEBUG=true`, FastAPI retorna stack traces completos en las respuestas HTTP

500. Esto revela:

- Rutas absolutas del servidor
- Nombres de archivos y funciones internas
- Valores de variables en el momento del error
- Estructura de la base de datos

**Explicación OWASP:** Los mensajes de error detallados son útiles en desarrollo pero

peligrosos en producción. Un atacante usa esta información para refinar ataques.

#### 🟠 A05-3: Sin Cabeceras de Seguridad HTTP

**Archivo:** `main.py` — No se configura ninguna cabecera de seguridad.

Faltan:

| Cabecera | Propósito |
|----------|-----------|
| `Strict-Transport-Security` | Forzar HTTPS |
| `X-Content-Type-Options: nosniff` | Prevenir MIME sniffing |
| `X-Frame-Options: DENY` | Prevenir clickjacking |
| `Content-Security-Policy` | Prevenir XSS |
| `X-XSS-Protection` | Activar filtro XSS del navegador |

#### 🟢 A05-4: Versión de Framework Expuesta

FastAPI y Starlette exponen por defecto la cabecera `server: uvicorn`. Esto le dice al atacante

qué versión del servidor está corriendo.

### Recomendación A05

```python
# main.py — Configuración completa
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Server"] = ""  # Ocultar versión del servidor
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS specifico
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## A06 — Vulnerable & Outdated Components (Componentes Vulnerables)

### ¿Qué es?

Ocurre cuando la aplicación usa bibliotecas, frameworks o dependencias con vulnerabilidades

conocidas. Incluye: versiones desactualizadas, componentes no mantenidos, falta de escaneo

de vulnerabilidades.

### Hallazgos en el Proyecto

#### 🟡 A06-1: python-jose (JWT Library)

**Archivo:** `pyproject.toml` (dependencia: `python-jose`)

`python-jose` ha tenido vulnerabilidades conocidas de *algorithm confusion* en el pasado.

Aunque el código actual restringe a `HS256` explícitamente, la biblioteca en sí es menos

activa que alternativas modernas.

#### 🟡 A06-2: Dos Bibliotecas JWT Instaladas

**Archivo:** `pyproject.toml` — `pyjwt` (v2.10.1) y `python-jose` (v3.3.0)

Tener dos bibliotecas que hacen lo mismo aumenta la superficie de ataque y puede causar

confusión sobre cuál se está usando realmente.

#### 🟡 A06-3: psycopg2-binary en Producción

**Archivo:** `requirements.txt` — `psycopg2-binary`

**Explicación:** `psycopg2-binary` es la versión pre-compilada, recomendada solo para

desarrollo. En producción debe usarse `psycopg2` (compilado desde fuente) porque

`psycopg2-binary` tiene linking dinámico que puede causar fallos de seguridad y estabilidad.

#### 🟢 A06-4: Versiones No Verificadas

No hay un archivo de lock (poetry.lock) visible, lo que significa que las dependencias

transitivas no están fijadas. Esto puede causar que diferentes despliegues obtengan versiones

distintas de las dependencias.

### Recomendación A06

```bash
# Escaneo de vulnerabilidades
pip install safety
safety check

# O usando pip-audit
pip install pip-audit
pip-audit

# Reemplazar python-jose con PyJWT moderno (unificar)
# pyproject.toml
[tool.poetry.dependencies]
PyJWT = "^2.10.0"
python-jose = {optional = true}  # o eliminarlo

# psycopg2 en producción
psycopg2 = "^2.9.0"
psycopg2-binary = {optional = true, dev = true}
```

---

## A07 — Identification & Authentication Failures (Fallos de Identificación y Autenticación)

### ¿Qué es?

Agrupa fallos en: autenticación de usuarios, manejo de sesiones, recuperación de credenciales,

y gestión de identidad. Incluye: credenciales débiles, falta de rate limiting, enumeración de

usuarios, sesiones sin invalidar.

### Hallazgos en el Proyecto

#### 🔴 A07-1: Recuperación de Contraseña Sin Autenticación

(Ya descrito en A04-1) — Cualquier persona puede cambiar cualquier contraseña solo con el email.

#### 🔴 A07-2: Sin Rate Limiting en Login

**Archivo:** `app/auth/login.py:18-39`

No hay límite en el número de intentos de inicio de sesión. Un atacante puede probar millones

de contraseñas sin restricción.

**Explicación OWASP:** El rate limiting es la defensa principal contra:

- **Fuerza bruta:** Probar todas las combinaciones posibles
- **Credential stuffing:** Probar credenciales filtradas de otros sitios
- **Password spraying:** Probar contraseñas comunes contra muchos usuarios

#### 🟡 A07-3: Posible Enumeración de Usuarios

**Archivo:** `app/routes/auth.py:21-22`

```python
user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
if not user:
    raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
```

**Análisis:** Aunque el mensaje es genérico ("Usuario o contraseña incorrectos"), el hecho de

que `auth.py` separe el chequeo de existencia del chequeo de contraseña (vs. `auth/login.py`

que lo combina) puede crear diferencias de tiempo medibles.

**Explicación OWASP:** La enumeración de usuarios permite al atacante:
1. Confirmar qué usuarios existen en el sistema
2. Enfocar sus ataques de fuerza bruta solo en usuarios válidos
3. Saber qué direcciones de email/cuentas están registradas

La mitigación es:
```python
# Tiempo constante: siempre ejecutar verify_password aunque el usuario no exista
user = db.query(UserModel).filter(UserModel.username == username).first()
if not user:
    # Hash dummy para mantener tiempo constante
    dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$..."  # Hash pre-generado
    verify_password(password, dummy_hash)
    raise HTTPException(401, "Credenciales inválidas")
```

#### 🟡 A07-4: Política de Contraseñas Débil

**Archivo:** `app/schemas/user.py:37`

```python
password: str = Field(..., min_length=4)  # ⚠️ 4 caracteres
```

**Archivo:** `app/schemas/auth.py:12`

```python
password: str = Field(..., min_length=6, description="Contraseña del usuario")
```

**Archivo:** `generate_hash.py:5`

```python
password = "admin"  # ⚠️ Contraseña por defecto para admin
```

**Impacto:** Contraseñas de 4 caracteres se rompen en segundos con fuerza bruta. La contraseña

"admin" para el usuario administrador es crítica.

**Explicación OWASP:** Una política de contraseñas debe incluir:

- Longitud mínima: 8 caracteres (NIST SP 800-63 recomienda 8+)
- Complejidad: al menos una mayúscula, una minúscula, un número
- No debe contener el nombre de usuario
- Debe compararse contra listas de contraseñas conocidas (HaveIBeenPwned)

```python
@field_validator("password")
def validate_password_strength(cls, v):
    if len(v) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Debe contener al menos una mayúscula")
    if not re.search(r"[a-z]", v):
        raise ValueError("Debe contener al menos una minúscula")
    if not re.search(r"\d", v):
        raise ValueError("Debe contener al menos un número")
    return v
```

#### 🟡 A07-5: JWT con Expiración Larga (24h por defecto)

**Archivo:** `app/database/config.py:25`

```python
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24h
```

**Impacto:** Si un token JWT es robado (XSS, MITM, logging), el atacante tiene acceso por

24 horas. No hay forma de revocarlo.

**Explicación OWASP:** Los tokens de acceso deben tener la menor vida útil posible que sea

práctica para la experiencia del usuario. 15-30 minutos es el estándar, combinado con:

- **Refresh tokens** (vida más larga, 7-30 días, almacenados seguramente)
- **Rotación de refresh tokens** (cada vez que se usa, se emite uno nuevo)
- **Revocación** (el refresh token puede invalidarse en servidor)

### Recomendación General A07

```python
# database/config.py
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # 30 min
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
```

```python
# auth/login.py — Con rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None,
):
    ...
```

---

## A08 — Software & Data Integrity Failures (Fallos de Integridad)

### ¿Qué es?

Ocurre cuando el software o los datos no están protegidos contra modificaciones no autorizadas.

Incluye: actualizaciones sin verificar, pipelines CI/CD inseguros, deserialización insegura,

manipulación de datos en tránsito.

### Hallazgos en el Proyecto

#### 🟠 A08-1: Certificados y Claves en el Repositorio

(Ya descrito en A02-2) — La presencia de `client.key.pem` y `client.cert.pem` en el

repositorio viola la integridad del software: cualquiera con acceso al repo puede modificar

estos archivos o usarlos fuera de contexto.

#### 🟡 A08-2: Deserialización de JSONB Sin Validación

Múltiples columnas JSONB aceptan cualquier estructura JSON:

- `pacientes.datos_extra`
- `consultas.indicadores`
- `citas.datos_extra`
- `eventos_consulta.datos`

Estos campos se serializan/deserializan sin verificar que la estructura sea la esperada.

**Explicación OWASP:** La deserialización insegura puede llevar a:

- Manipulación de datos por parte del cliente
- Inyección de lógica de negocio maliciosa
- Corrupción de datos que afecta a otros usuarios o al frontend

#### 🟢 A08-3: Sin Verificación de Integridad de Dependencias

No hay hashes de verificación para las dependencias (sin poetry.lock o requirements.txt

con hashes).

### Recomendación A08

```python
# Validación de esquema JSONB con Pydantic
from pydantic import BaseModel, ValidationError

class DatosExtraPaciente(BaseModel):
    ocupacion: Optional[str] = None
    escolaridad: Optional[str] = None
    grupo_etnico: Optional[str] = None
    religion: Optional[str] = None

# Al guardar:
try:
    datos_validados = DatosExtraPaciente(**datos_extra)
    paciente.datos_extra = datos_validados.model_dump()
except ValidationError:
    raise HTTPException(400, "Estructura de datos_extra inválida")
```

---

## A09 — Security Logging & Monitoring Failures (Fallos de Registro y Monitoreo)

### ¿Qué es?

Ocurre cuando la aplicación no registra eventos de seguridad, no monitorea actividad

sospechosa, o no alerta sobre incidentes. Esta es la categoría más común en aplicaciones

reales y una de las más infravaloradas.

### Hallazgos en el Proyecto

#### 🟠 A09-1: No hay Logging en Absoluto

**En todo el proyecto:** `import logging` no aparece en ningún archivo.

Todo el output es con `print()`:

```python
print("Conexión a PostgreSQL exitosa")  # database/db.py:42
print("❌ Error enviando correo:", str(e))  # routes/user.py:210
```

**Impacto:** Sin logging es imposible:

- Detectar un ataque de fuerza bruta en progreso
- Investigar un incidente de seguridad post-mortem
- Cumplir con requisitos regulatorios (HIPAA, GDPR)
- Diagnosticar errores en producción

**Explicación OWASP:** Un sistema sin logging es ciego. Los atacantes pueden operar sin ser

detectados. El logging de seguridad debe registrar:

| Evento | Qué registrar |
|--------|---------------|
| Inicio de sesión exitoso | Usuario, IP, timestamp, user-agent |
| Inicio de sesión fallido | Usuario (o intento), IP, timestamp |
| Cambio de contraseña | Usuario, IP, timestamp |
| Acceso denegado (403) | Usuario, recurso, IP, timestamp |
| Creación/modificación de datos | Usuario, recurso, valores anteriores/nuevos |
| Eliminación de datos | Usuario, recurso, timestamp |
| Errores del servidor (500) | Stack trace, request ID, usuario, IP |

#### 🟠 A09-2: Sin Auditoría de Operaciones

No hay registro de:

- Quién creó cada paciente
- Quién modificó cada consulta
- Quién accedió a datos sensibles
- Intentos fallidos de acceso

#### 🟠 A09-3: Errores Silenciados

**Archivo:** `routes/pacientes.py:151-152`

```python
except:
    pass  # ⚠️ El error se pierde completamente
```

**Archivo:** `routes/user.py:209-210`

```python
except Exception as e:
    print("❌ Error enviando correo:", str(e))  # Solo a stdout, sin estructura
```

### Recomendación A09

```python
# logging_config.py
import logging
import sys
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("hospsys.security")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def login_success(self, username: str, ip: str):
        self.logger.info(f"LOGIN_OK | user={username} | ip={ip}")
    
    def login_failure(self, username: str, ip: str, reason: str):
        self.logger.warning(f"LOGIN_FAIL | user={username} | ip={ip} | reason={reason}")
    
    def access_denied(self, user_id: int, resource: str, ip: str):
        self.logger.warning(f"ACCESS_DENIED | user={user_id} | resource={resource} | ip={ip}")
    
    def data_mutation(self, user_id: int, action: str, table: str, record_id: int):
        self.logger.info(f"MUTATION | user={user_id} | action={action} | table={table} | id={record_id}")
    
    def error(self, request_id: str, user_id: int, message: str):
        self.logger.error(f"ERROR | request_id={request_id} | user={user_id} | {message}")

# Uso en login:
security_log = SecurityLogger()
security_log.login_failure(form_data.username, request.client.host, "invalid_password")
```

```python
# Middleware de auditoría
class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        start = datetime.now()
        response = await call_next(request)
        elapsed = (datetime.now() - start).total_seconds()
        
        if response.status_code >= 500:
            logger.error(
                f"request_id={request_id} | "
                f"{request.method} {request.url.path} | "
                f"status={response.status_code} | "
                f"elapsed={elapsed:.3f}s | "
                f"ip={request.client.host}"
            )
        
        return response
```

---

## A10 — Server-Side Request Forgery (SSRF)

### ¿Qué es?

Ocurre cuando un atacante puede hacer que el servidor realice peticiones HTTP a destinos

controlados por el atacante. Permite: escaneo de redes internas, acceso a servicios locales,

exfiltración de datos.

### Hallazgos en el Proyecto

#### 🟢 A10-1: SSRF Potencial Bajo

**Archivo:** `app/services/renap_service.py:16`

```python
API_URL = "https://salud-digital.mspas.gob.gt/personas"
```

**Análisis:** La URL del servicio externo RENAP está hardcodeada. El usuario solo proporciona

parámetros de consulta (CUI, nombres), no la URL. Esto hace que el riesgo de SSRF sea **bajo**.

Sin embargo, si en el futuro se permite configurar la URL desde el cliente (por ejemplo, para

entornos de desarrollo), habría que validar estrictamente.

**Explicación OWASP:** El SSRF es particularmente peligroso en entornos cloud donde los

servicios internos (metadata endpoints de AWS/GCP/Azure, bases de datos, servicios internos)

son accesibles desde el servidor pero no desde internet. La mitigación principal es:

1. Hardcodear URLs de servicios externos (como ya se hace)
2. Validar que la URL pertenece a un dominio permitido
3. Usar allow lists de IPs
4. No redirigir basado en input del usuario

#### 🟢 A10-2: Timeout Largo (40s)

**Archivo:** `app/services/renap_service.py:28`

```python
timeout=40.0,
```

Si un atacante puede iniciar muchas peticiones RENAP, podría agotar el pool de conexiones

del servidor manteniendo conexiones abiertas por 40 segundos cada una.

### Recomendación A10

```python
# Si se agrega funcionalidad que permita URLs configurables:
from urllib.parse import urlparse

ALLOWED_HOSTS = {"salud-digital.mspas.gob.gt", "api.mspas.gob.gt"}

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise HTTPException(400, "Host no permitido")
    if parsed.scheme not in ("https",):
        raise HTTPException(400, "Solo HTTPS permitido")
    return True
```

---

## Matriz de Riesgo Consolidada

| # OWASP | Categoría | # Hallazgos | Severidad Máxima | Prioridad |
|---------|-----------|-------------|------------------|-----------|
| A01 | Broken Access Control | 4 | 🔴 CRÍTICA | DÍA 1 |
| A02 | Cryptographic Failures | 7 | 🔴 CRÍTICA | DÍA 1 |
| A03 | Injection | 1 | 🟡 MEDIA | DÍA 3 |
| A04 | Insecure Design | 3 | 🔴 CRÍTICA | DÍA 1 |
| A05 | Security Misconfiguration | 4 | 🟠 ALTA | DÍA 2 |
| A06 | Vulnerable Components | 4 | 🟡 MEDIA | DÍA 3 |
| A07 | Auth Failures | 5 | 🔴 CRÍTICA | DÍA 1 |
| A08 | Integrity Failures | 3 | 🟠 ALTA | DÍA 2 |
| A09 | Logging & Monitoring | 3 | 🟠 ALTA | DÍA 2 |
| A10 | SSRF | 2 | 🟢 BAJA | DÍA 4+ |

### Prioridades por Día

| Día | Categorías OWASP | Acciones |
|-----|------------------|----------|
| **DÍA 1** 🔴 | A01, A02, A04, A07 | Password reset, API keys, TLS keys, .env, CORS |
| **DÍA 2** 🟠 | A05, A08, A09 | Logging, auditoría, cabeceras, debug off |
| **DÍA 3** 🟡 | A03, A06 | SQL injection fix, dependencias, password policy |
| **DÍA 4+** 🟢 | A10 | SSRF hardening, mejoras adicionales |

---

## Glosario OWASP

| Término | Explicación |
|---------|-------------|
| **MITM** (Man-in-the-Middle) | Atacante se interpone en la comunicación entre dos partes, pudiendo leer y modificar los datos |
| **CSRF** (Cross-Site Request Forgery) | El navegador de la víctima hace peticiones no intencionadas a un sitio donde está autenticada |
| **XSS** (Cross-Site Scripting) | Inyección de scripts maliciosos en páginas web vistas por otros usuarios |
| **CORS** (Cross-Origin Resource Sharing) | Mecanismo del navegador que controla qué orígenes pueden acceder a recursos |
| **JWT** (JSON Web Token) | Token de autenticación con formato JSON, firmado digitalmente |
| **Argon2** | Algoritmo moderno de hashing de contraseñas, ganador de la competencia PHC |
| **Rate Limiting** | Límite en la cantidad de peticiones que un cliente puede hacer en un período |
| **Account Enumeration** | Técnica para determinar qué usuarios existen en un sistema |
| **Credential Stuffing** | Ataque que usa contraseñas filtradas de otros sitios para acceder a cuentas |
| **Defense in Depth** | Principio de seguridad que usa múltiples capas de defensa |

---

## Referencias

- [OWASP Top 10 2021 — Documento Oficial](https://owasp.org/Top10/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [OWASP ASVS (Application Security Verification Standard)](https://owasp.org/www-project-application-security-verification-standard/)
- [NIST SP 800-63 — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)

---

*Documento generado mediante análisis estático del código fuente. Las líneas y archivos

corresponden al estado actual del repositorio al momento del análisis.*
