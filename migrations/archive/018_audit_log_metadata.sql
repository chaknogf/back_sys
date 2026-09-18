-- 018_audit_log_metadata.sql
-- Campos opcionales de contexto del cliente en audit_log (IP, User-Agent, SO y nombre de equipo).

ALTER TABLE audit_log
    ADD COLUMN IF NOT EXISTS ip_address    VARCHAR(45),
    ADD COLUMN IF NOT EXISTS user_agent    TEXT,
    ADD COLUMN IF NOT EXISTS so            VARCHAR(100),
    ADD COLUMN IF NOT EXISTS nombre_equipo VARCHAR(255);