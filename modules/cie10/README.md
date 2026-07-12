# Módulo CIE-10: Chatbox de Diagnósticos

## ¿Qué hace?

- **Fase 1 (local)**: Busca cualquier código o diagnóstico CIE-10 en español por nombre o código. Usa PostgreSQL con trigram + unaccent. Sin dependencias externas.
- **Fase 2 (LLM)**: Chat con IA para preguntas en lenguaje natural sobre diagnósticos. Requiere API key de OpenAI.

## Endpoints

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/cie10?q=<texto>` | auth | Busca códigos/descripciones |
| `GET` | `/cie10/usados?limit=20` | auth | Códigos más usados en el sistema |
| `POST` | `/cie10/consultar` | auth | Chat LLM (requiere API key) |

## Fase 1 — Búsqueda local (sin LLM)

No necesita configuración. La tabla se crea sola al primer request y el catálogo se descarga automáticamente (~14,500 códigos).

```bash
# Buscar por código o descripción
curl -H "$AUTH" "http://localhost:8000/fah/cie10?q=neumonia"
curl -H "$AUTH" "http://localhost:8000/fah/cie10?q=J15"
curl -H "$AUTH" "http://localhost:8000/fah/cie10?q=abdomen&nivel=3"

# Códigos más frecuentes en el sistema
curl -H "$AUTH" "http://localhost:8000/fah/cie10/usados"
```

## Fase 2 — Chat con LLM

### Opción A (recomendada) — Ollama local

Gratis, offline, sin límites. Corre en tu MacBook Air M2.

```bash
# 1. Instalar Ollama
brew install ollama

# 2. Iniciar el servidor
ollama serve

# 3. En otra terminal, descargar el modelo (2.3GB)
ollama pull phi3:mini
```

Configuración en `.env` (ya está por defecto):
```env
CIE10_LLM_PROVIDER=ollama
CIE10_LLM_MODEL=phi3:mini
```

### Opción B — Gemini (fallback cloud)

```env
CIE10_LLM_API_KEY=AIza_tu_api_key_aqui
CIE10_LLM_MODEL=gemini-flash-latest
CIE10_LLM_PROVIDER=gemini
```

### Opción C — OpenAI

```env
CIE10_LLM_API_KEY=sk-tu_api_key_aqui
CIE10_LLM_MODEL=gpt-4o-mini
CIE10_LLM_PROVIDER=openai
```

> Si `ollama` falla (no está instalado), automáticamente usa el provider configurado con API key como respaldo.

### 3. Usa el chat

```bash
# Pregunta simple
curl -X POST "http://localhost:8000/fah/cie10/consultar" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Qué código CIE-10 se usa para exploración abdominal?"}'

# Con contexto de códigos específicos
curl -X POST "http://localhost:8000/fah/cie10/consultar" \
  -H "$AUTH" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es la diferencia entre estos diagnósticos?",
    "codigos_contexto": ["R10.0", "R10.1", "R10.3"]
  }'
```

El chat tiene rate limit de 5 requests por minuto.

## Despliegue

El deploy.sh ya incluye la descarga automática del catálogo. En producción la tabla se crea sola al primer uso.

Si prefieres crearla manualmente desde SQL:

```sql
CREATE TABLE IF NOT EXISTS cie10_catalogo (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL,
    nivel INTEGER NOT NULL DEFAULT 0,
    codigo_padre VARCHAR(10),
    fuente VARCHAR(20)
);
CREATE INDEX IF NOT EXISTS idx_cie10_codigo ON cie10_catalogo (codigo);
CREATE INDEX IF NOT EXISTS idx_cie10_padre ON cie10_catalogo (codigo_padre);
CREATE INDEX IF NOT EXISTS idx_cie10_descripcion_trgm ON cie10_catalogo USING gin (descripcion gin_trgm_ops);
```

## Frecuencia de actualización del catálogo

El catálogo se descarga UNA SOLA VEZ (al primer request o en deploy). Si quieres forzar una recarga, borra la tabla o los registros:

```sql
TRUNCATE cie10_catalogo;
```

O desde Python:

```bash
python3 -c "
from core.database import SessionLocal
from modules.cie10.service import descargar_catalogo
db = SessionLocal()
try:
    total = descargar_catalogo(db)
    print(f'Recargados {total} códigos')
finally:
    db.close()
"
```
