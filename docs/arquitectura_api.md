# Arquitectura, inventario y verificación de la API

## Arquitectura recomendada

Mantener `back_sys` como **monolito modular**. El sistema comparte usuarios,
pacientes, consultas y transacciones; separarlo ahora en microservicios agregaría
despliegues, coordinación y consistencia distribuida sin reducir una carga ya
medida que lo justifique.

Para los módulos existentes, usar de manera consistente esta dirección:

```text
HTTP/router → caso de uso/service → consultas/repositorio → SQLAlchemy/PostgreSQL
       ↑                 ↓
   schemas         transacción única
```

- **Router:** path, validación HTTP, autenticación/rol y serialización; sin SQL
  ni reglas de negocio.
- **Service/caso de uso:** reglas, transiciones de estado y una frontera
  transaccional por operación. Una importación/sincronización no debe hacer
  `commit()` por fila.
- **Repositorio:** introducirlo donde reduce SQL repetido o facilita pruebas;
  no crear una capa genérica para CRUD trivial.
- **Schemas:** separar claramente entrada, detalle, lista y respuesta paginada.
- **Pruebas del módulo:** servicio unitario para reglas, TestClient para
  autenticación/contratos y pruebas de integración para consultas/transacciones.

### Contrato de listas

Para registros de negocio que crecen, adoptar un envelope uniforme:

```json
{"items": [], "total": 0, "skip": 0, "limit": 50, "has_more": false}
```

Default sugerido: `limit=50`, máximo 200 (hasta 500 para catálogos pequeños),
`skip >= 0`, orden estable con ID como desempate. El detalle de un documento no
se pagina; sus colecciones anidadas grandes deben tener endpoints paginados.
Los reportes agregados y catálogos estáticos de tamaño fijo son excepciones
documentadas. Para tablas de historial muy grandes, usar keyset/cursor en vez de
offset profundo.

### Seguridad y trabajos largos

- Toda ruta privada declara `get_current_user` en el router o endpoint; las
  operaciones administrativas/destructivas agregan `get_current_admin_user`.
- Mantener una lista explícita y pequeña de endpoints públicos.
- Importaciones y reconciliaciones de miles de filas deben ejecutarse como
  trabajos idempotentes con estado consultable y tamaño de lote; no ocupar un
  worker HTTP por varios minutos.
- Validar límite de archivo y cantidad de elementos en cargas masivas antes de
  procesarlas.

## Inventario de rutas y endpoints

Inventario generado desde `app.openapi()` (rutas publicadas, sin incluir
compatibilidades ocultas de OpenAPI):

| Métrica | Estado actual tras la consolidación |
|---|---:|
| Paths publicados | 220 |
| Operaciones publicadas | 318 |
| Métodos/path duplicados exactos | 0 |
| Aliases `/especialidades` frente a `/especialidades/` publicados | 0 |
| Rutas públicas | 9, limitadas a login/recuperación, salud y catálogos públicos |
| Listados de negocio sin límite | 0 detectados en el inventario revisado |

`/pacientes/buscar` es la única búsqueda paginada para pacientes y recepción;
admite `documento` mediante consulta. Los GET redundantes `/pacientes/` y
`/consultas/buscarpaciente` fueron retirados. `/catalogo-procedimientos/` es la
única API del catálogo maestro; las rutas `/procedimientos/catalogo*` fueron
retiradas. Las consultas de pacientes recientes y consultas recientes son
recursos distintos y tienen rutas propias antes de los handlers `/{id}`.

Los paths de colección de Quirófano también usan la convención canónica sin
slash final; el frontend fue actualizado a esos paths.

## Rutina recomendada de inventario/verificación

1. Generar OpenAPI al iniciar CI y comprobar paths/métodos duplicados, aliases
   normalizados, `operationId` y rutas estáticas que preceden a `/{id}`.
2. Fallar CI si aparece una ruta sin seguridad fuera de la allowlist pública.
3. Revisar cada GET que devuelve una colección: límites validados, orden
   determinista y query de página acotada. Excluir con justificación catálogos
   fijos y reportes agregados.
4. Para cada SQL nuevo/cambiado, medir con `EXPLAIN (ANALYZE, BUFFERS)` en una
   copia representativa de PostgreSQL; revisar `pg_stat_statements` en la
   instancia operativa para priorizar optimización por impacto real.
5. Ejecutar pruebas de router y del dominio tocado, después build del frontend
   cuando se cambie un contrato consumido por Angular.
6. Revisar cambios de schema de base de datos con migración idempotente,
   estrategia de despliegue y actualización simultánea de sus consumidores.

Comandos de base:

```bash
cd back_sys
python -c "from main import app; print(app.openapi()['paths'].keys())"
pytest tests/test_api_route_resolution.py tests/test_insumos.py -q

cd ../hospital3
pnpm build
pnpm test --watch=false --include=src/app/principal/administrador/gestion-procedimientos/gestion-procedimientos.component.spec.ts
```
