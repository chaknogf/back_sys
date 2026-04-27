pg_dump -U postgres -d hospital --schema-only --no-owner=false --no-privileges=false > hospital_estructura.sql

pg_dump -U postgres -d hospital --schema-only --no-owner --no-privileges > hospital_estructura.sql
pg_dump -U $(whoami) -d hospital --schema-only --no-owner --no-privileges > hospital_estructura.sql