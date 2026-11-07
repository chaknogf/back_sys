-- 089_indices_citas_prestamos_defunciones_audit_log.sql
-- Índices faltantes detectados en la auditoría de rendimiento.
-- Aditiva e idempotente: usa CREATE INDEX IF NOT EXISTS.
-- Tablas afectadas: citas, prestamos, defunciones, audit_log.

-- citas: búsquedas por paciente y por fecha de cita (listados/filtros del frontend).
CREATE INDEX IF NOT EXISTS idx_citas_paciente_id
    ON public.citas (paciente_id);

CREATE INDEX IF NOT EXISTS idx_citas_fecha_cita
    ON public.citas (fecha_cita);

CREATE INDEX IF NOT EXISTS idx_citas_paciente_fecha
    ON public.citas (paciente_id, fecha_cita);

-- prestamos: préstamos pendientes por paciente y por fecha de devolución.
CREATE INDEX IF NOT EXISTS idx_prestamos_id_paciente_activo
    ON public.prestamos (id_paciente, activo);

CREATE INDEX IF NOT EXISTS idx_prestamos_fecha_devolucion
    ON public.prestamos (fecha_devolucion);

-- defunciones: búsquedas por paciente, registrador y fecha.
CREATE INDEX IF NOT EXISTS idx_defunciones_registrador_id
    ON public.defunciones (registrador_id);

CREATE INDEX IF NOT EXISTS idx_defunciones_paciente_fecha
    ON public.defunciones (paciente_id, fecha_defuncion);

-- audit_log: filtros de la UI (username, tabla, rango de fecha).
CREATE INDEX IF NOT EXISTS idx_audit_log_username
    ON public.audit_log (username);

CREATE INDEX IF NOT EXISTS idx_audit_log_tabla
    ON public.audit_log (tabla);

CREATE INDEX IF NOT EXISTS idx_audit_log_fecha_hora
    ON public.audit_log (fecha_hora);

CREATE INDEX IF NOT EXISTS idx_audit_log_tabla_fecha
    ON public.audit_log (tabla, fecha_hora);

CREATE INDEX IF NOT EXISTS idx_audit_log_username_fecha
    ON public.audit_log (username, fecha_hora);