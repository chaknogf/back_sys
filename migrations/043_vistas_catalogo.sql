-- ============================================================
-- 043_routes_catalogo_procedimientos.sql
-- Vista SQL que sirve como API-friendly para el catálogo maestro.
-- La API backend expone estos endpoints como JSON.
-- ============================================================

-- Vista detalle del catálogo maestro
CREATE OR REPLACE VIEW public.v_catalogo_procedimientos AS
SELECT
    cp.id,
    cp.abreviatura,
    cp.nombre,
    cp.descripcion,
    cp.anestesia,
    cp.especialidad_ref,
    e.nombre AS especialidad_nombre,
    cp.activo,
    cp.created_at,
    cp.updated_at
FROM public.catalogo_procedimientos cp
LEFT JOIN public.especialidades e ON e.id = cp.especialidad_ref;

-- Vista detalle de áreas del cuerpo
CREATE OR REPLACE VIEW public.v_areas_cuerpo AS
SELECT
    a.id, a.codigo, a.nombre, a.region, a.descripcion,
    a.activo, a.created_at, a.updated_at,
    (SELECT COUNT(*) FROM public.procedimientos_area_cuerpo pac WHERE pac.id_area_cuerpo = a.id) AS total_procedimientos
FROM public.area_cuerpo_intervenida a;