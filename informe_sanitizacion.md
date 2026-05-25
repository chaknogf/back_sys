# Informe de Sanitización y Normalización de Datos de Usuario

> Proyecto: **back-sys** — Sistema de Gestión Hospitalaria (FastAPI + PostgreSQL)
> Fecha del análisis: Mayo 2026

---

## Resumen Ejecutivo

El proyecto utiliza **Pydantic v2** para validación de esquemas en endpoints POST/PUT/PATCH, y **SQLAlchemy** con consultas parametrizadas (previniendo SQL injection). Sin embargo, se identificaron **múltiples áreas críticas** donde la sanitización y normalización de datos de usuario es insuficiente o inexistente.

---

## 1. Parámetros de Consulta (Query Parameters) Sin Normalizar

### Archivo: `app/routes/pacientes.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 91 | `nombre` | Se aplica `.strip().upper()` — **solo este está normalizado** |
| 100 | `id` | No se valida que sea entero antes de pasarlo al filtro |
| 105 | `cui` | Tiene `isdigit()` check — correcto |
| 112 | `expediente` | No se normaliza (strip/upper) |
| 117 | `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido` | Pasados directamente a `ilike()` sin `.strip()` |
| 119 | `fecha_nac` | Sin validación de formato antes de parsear |
| 151-152 | `fecha_nac` | `try/except: pass` — traga errores silenciosamente |

### Archivo: `app/routes/consultas.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 83-94 | `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`, `documento`, `cui`, `expediente` | Sin `.strip()` ni normalización antes de pasarlos a `ilike()` |
| 107-111 | `fecha`, `tipo_consulta`, `especialidad` | Sin validación de formato/valores permitidos |

### Archivo: `app/routes/citas.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 96 | `expediente` | Sin `.strip()` ni normalización |
| 101 | `especialidad` | Pasado directamente a filtro sin validación de valores permitidos |
| 105 | `fecha_cita`, `fecha_desde`, `fecha_hasta` | Sin validación de formato de fecha |

### Archivo: `app/routes/medicos.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 100 | `nombre`, `especialidad` | Sin `.strip()` — riesgo de búsquedas con espacios al inicio/final |
| 104 | `colegiado` | Sin normalización |

### Archivo: `app/routes/eventos.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 98 | `responsable` (JSONB) | Sin `.strip()` — pasado directo a `ilike()` sobre JSONB |

### Archivo: `app/routes/nacimientos_legacy.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 77 | `madre`, `doc` | Sin `.strip()` — pasados directo a `ilike()` |

### Archivo: `app/routes/constancia_nacimiento.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 105 | `nombre_madre` | Sin `.strip()` — usado en `ilike(f"%{nombre_madre}%")` |

### Archivo: `app/routes/user.py`

| Línea | Parámetro | Problema |
|-------|-----------|----------|
| 100-104 | `username`, `email` | Sin `.strip()` antes de filtrar |

---

## 2. Campos JSONB Sin Validación de Esquema

Los siguientes campos JSONB en la base de datos aceptan **cualquier estructura JSON** sin validación server-side más allá de lo que defina Pydantic (y algunos son `Dict[str, Any]`):

| Tabla | Columna JSONB | Riesgo |
|-------|---------------|--------|
| `pacientes` | `nombre` | Aunque el modelo tiene `@validates`, la estructura podría ser inconsistente |
| `pacientes` | `contacto` | No se fuerza estructura de teléfonos/direcciones |
| `pacientes` | `referencias` | Sin validación de estructura |
| `pacientes` | `datos_extra` | `Dict[str, Any]` — acepta cualquier cosa |
| `pacientes` | `metadatos` | Sin restricciones de esquema |
| `consultas` | `indicadores` | Sin validación de estructura interna |
| `consultas` | `ciclo` | Sin validación |
| `consultas` | `egreso` | Sin validación |
| `citas` | `datos_extra` | Sin validación |
| `eventos_consulta` | `datos` | Sin validación |
| `eventos_consulta` | `responsable` | Sin validación |
| `ciclos_consulta` | `datos_medicos` | Sin validación |
| `laboratorios` | `resultados`, `metadatos` | Sin validación |
| `rayos_x` | `resultados`, `metadatos` | Sin validación |
| `constancia_nacimiento` | `menor_edad`, `metadatos` | Sin validación |

---

## 3. Vulnerabilidades de Seguridad (XSS)

### Emails sin escape HTML

**Archivo: `app/routes/user.py`** — Construcción de email de bienvenida con f-strings:

```python
html = f"<p>Bienvenido {usuario.nombre}</p>"
```

Si `usuario.nombre` contiene `<script>`, se ejecutará en el cliente de correo. Aplica también a `usuario.username`.

### Datos de pacientes servidos sin sanitizar

Cualquier campo de texto (nombre, dirección, observaciones) almacenado en JSONB y servido a través de las APIs GET podría contener HTML/JS malicioso si un atacante logra insertarlo. No se aplica escape HTML al servir respuestas.

---

## 4. Endpoint de Recuperación de Contraseña Sin Verificación

**Archivo: `app/routes/user.py` — `PATCH /users/recuperar`**

```python
class RecuperarPassword(BaseModel):
    email: EmailStr
    password: str  # min_length=4
```

No requiere:
- Token de verificación
- Código OTP
- Enlace de restablecimiento por correo
- Prueba de posesión del email

Un atacante que conozca o adivine un email válido puede cambiar la contraseña inmediatamente.

---

## 5. API Key Hardcodeada

**Archivo: `app/services/renap_service.py`** (línea 15):

```python
API_KEY = "b6039f4a35ae824f9d7abe6a8bda8f7d5e590cfd9ee53ba87dce37b890588fb3"
```

La clave está hardcodeada en el código fuente. Debería estar en variable de entorno (`.env`).

---

## 6. CORS sin Restricciones

**Archivo: `app/main.py`**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- `allow_origins=["*"]` + `allow_credentials=True` es una combinación inválida según la especificación CORS
- Cualquier sitio web puede hacer peticiones desde el navegador del usuario

---

## 7. Datos de Auditoría Faltantes

No existe:
- Log estructurado de operaciones de creación/actualización/eliminación
- Registro de quién modificó qué y cuándo (más allá de campos sueltos como `created_by`)
- Trazabilidad en modificaciones de datos sensibles

---

## 8. Falta de Rate Limiting

No hay límite de velocidad en:
- `POST /auth/login` — permite fuerza bruta de contraseñas
- `GET /renap/persona` — podría agotar la cuota de la API externa
- `POST /pacientes`, `POST /consultas`, etc. — podría saturar la BD

---

## 9. Validación Inconsistente de Esquemas Pydantic

| Esquema | Problema |
|---------|----------|
| `PacienteUpdate` | `max_length` ausente en la mayoría de campos string |
| `CitaCreate.datos_extra` | `dict[str, Any]` — sin restricciones |
| `EventoConsultaCreate.datos` | `dict[str, Any]` — sin restricciones |
| `CicloConsultaBase` | Campos `contenido`, `datos_medicos` sin validación de estructura |
| `ConsultaUpdate` | Validación insuficiente de tipos en campos JSONB |

---

## 10. Normalización Inconsistente de Nombres

- Algunos endpoints aplican `.strip().upper()` a nombres (pacientes route, renap route)
- Otros no aplican ninguna normalización (citas, médicos, eventos, constancias)
- El modelo `PacienteModel` tiene un `@validates("nombre")` que normaliza, pero esto solo aplica a nivel ORM, no a todos los puntos de entrada

---

## Resumen de Prioridades

| Prioridad | Área | Impacto |
|-----------|------|---------|
| 🔴 Crítica | Password reset sin verificación | Toma de cuentas |
| 🔴 Crítica | API key hardcodeada | Exposición de credenciales |
| 🔴 Crítica | CORS mal configurado | Robo de datos vía CSRF |
| 🟠 Alta | Query params sin `.strip()`/normalizar | Búsquedas inconsistentes, potenciales errores |
| 🟠 Alta | JSONB sin esquema | Inconsistencia de datos, errores en frontend |
| 🟠 Alta | Rate limiting ausente | Fuerza bruta, DoS parcial |
| 🟡 Media | XSS en emails | Ejecución de script en clientes de correo |
| 🟡 Media | XSS en respuestas API | Inyección en frontends que no escapen HTML |
| 🟡 Media | `except: pass` | Dificulta depuración, esconde errores |
| 🟢 Baja | Normalización inconsistente de nombres | Datos duplicados por diferencias de formato |

---

## Recomendaciones Generales

1. **Normalizar todos los query params** con `.strip()` y opcionalmente `.upper()` según el campo
2. **Agregar `max_length`** a todos los campos string en schemas Pydantic
3. **Mover API key a variable de entorno** en `.env`
4. **Implementar rate limiting** con `slowapi` o middleware personalizado
5. **Corregir endpoint de recuperación** con token por email/OTP
6. **Sanitizar HTML** con `bleach` o similar antes de insertar en emails o respuestas
7. **Agregar logging estructurado** de operaciones (create/update/delete con usuario y timestamp)
8. **Usar Pydantic `Field(max_length=...)`** en todos los schemas de entrada
9. **Aplicar normalización de nombres consistente** en todos los endpoints de búsqueda
10. **Corregir CORS** para usar orígenes específicos desde variable de entorno
11. **Evitar `except: pass`** y reemplazar con manejo específico de excepciones
