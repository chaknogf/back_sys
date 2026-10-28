"""Asociación SIGSA-3 → paciente y consulta sobre la BD.

No existe tabla de auditoría. El rastro vive en los datos:
- `sigsa3.paciente_id` / `sigsa3.consulta_id`: el resultado de la asociación.
- `pacientes.datos_extra.origen = "sigsa3"` (+ `sigsa3_id`, `revisar_nombre`) para
  los pacientes creados desde SIGSA-3.

Es diferencial e idempotente: solo se procesan registros que aún no tienen
paciente o consulta; volver a ejecutar no duplica pacientes ni cambia lo ya asociado.

`dry_run=True` ejecuta la misma lógica, incluidas las creaciones en el índice,
sin escribir. Por eso sus conteos coinciden con los de la aplicación.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from modules.sigsa3.asociacion import (
    CREAR,
    ESTADOS_ASOCIAN,
    VERSION,
    ConsultaRef,
    IndicePacientes,
    Paciente,
    Registro,
    asociar,
    asociar_consulta,
    normalizar_identificador,
    normalizar_sexo,
)

LOTE = 500
_LOCK_CLAVE = "sigsa3_asociacion_aplicar"
ORIGEN_SIGSA3 = "sigsa3"


def _cargar_pacientes(db: Session) -> list[Paciente]:
    out: list[Paciente] = []
    filas = db.execute(text(
        "SELECT id, nombre_completo, sexo, expediente FROM pacientes "
        "WHERE nombre_completo IS NOT NULL AND TRIM(nombre_completo) <> ''"
    )).fetchall()
    for f in filas:
        out.append(Paciente(
            pac_id=int(f.id), nombre=f.nombre_completo,
            sexo=normalizar_sexo(f.sexo),
            expediente=normalizar_identificador(f.expediente),
            creado=False,
        ))
    filas = db.execute(text(
        "SELECT id, nombre, sexo, expediente FROM pacientes_sigsa3 "
        "WHERE estado = 'A' AND nombre IS NOT NULL"
    )).fetchall()
    for f in filas:
        out.append(Paciente(
            pac_id=int(f.id), nombre=f.nombre,
            sexo=normalizar_sexo(f.sexo),
            expediente=normalizar_identificador(f.expediente),
            creado=True,
        ))
    return out


def _cargar_consultas(db: Session) -> dict[int, list[ConsultaRef]]:
    """Consultas activas agrupadas por paciente."""
    por_paciente: dict[int, list[ConsultaRef]] = defaultdict(list)
    filas = db.execute(text(
        "SELECT id, paciente_id, fecha_consulta, tipo_consulta, documento FROM consultas "
        "WHERE activo = TRUE AND fecha_consulta IS NOT NULL"
    )).fetchall()
    for f in filas:
        por_paciente[int(f.paciente_id)].append(ConsultaRef(
            consulta_id=int(f.id),
            paciente_id=int(f.paciente_id),
            fecha=f.fecha_consulta,
            tipo=int(f.tipo_consulta) if f.tipo_consulta is not None else None,
            documento=normalizar_identificador(f.documento),
        ))
    return por_paciente


def _partir_nombre(nombre: str) -> dict:
    """Heurística: 1º nombre, 1º apellido, resto como segundo apellido.
    El orden de SIGSA no siempre es fiable; por eso se marca revisar_nombre."""
    toks = nombre.strip().split()
    return {
        "primer_nombre": toks[0],
        "segundo_nombre": None,
        "primer_apellido": toks[1] if len(toks) > 1 else None,
        "segundo_apellido": " ".join(toks[2:]) or None,
        "otro_nombre": None,
        "apellido_casada": None,
    }


def _crear_paciente(db: Session, nombre: str, sexo: str, nhc: str, sigsa3_id: int) -> int:
    datos = {"origen": ORIGEN_SIGSA3, "sigsa3_id": sigsa3_id, "revisar_nombre": True}
    sp = db.begin_nested()
    try:
        pid = db.execute(text(
            "INSERT INTO pacientes_sigsa3 (nombre, sexo, expediente, sigsa3_id_origen, datos_extra, estado) "
            "VALUES (:nombre, :sexo, :exp, :origen, CAST(:datos AS jsonb), 'A') RETURNING id"
        ), {
            "nombre": nombre,
            "sexo": sexo,
            "exp": nhc or None,
            "origen": sigsa3_id,
            "datos": json.dumps(datos),
        }).scalar()
        sp.commit()
        return int(pid)
    except IntegrityError:
        sp.rollback()
        raise


def _pendientes(db: Session, limit: Optional[int]) -> list:
    sql = (
        "SELECT s.id, s.nombre_paciente, s.sexo, s.no_historia_clinica, s.fecha_consulta, "
        "       s.tipo_consulta, s.paciente_id, s.consulta_id "
        "FROM sigsa3 s "
        "WHERE (s.paciente_id IS NULL AND s.nombre_paciente IS NOT NULL) "
        "   OR (s.paciente_id IS NOT NULL AND s.consulta_id IS NULL) "
        "ORDER BY s.id"
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    return db.execute(text(sql)).fetchall()


def aplicar_asociacion(db: Session, dry_run: bool = True, limit: Optional[int] = None,
                       usuario: Optional[str] = None, commit: bool = True) -> dict:
    """Asocia paciente y consulta a los registros SIGSA-3 pendientes.

    - Paciente: `asociar` (identificador, nombre, duplicados idénticos, creación con
      datos mínimos si no existe nadie parecido).
    - Consulta: `asociar_consulta` sobre las consultas del paciente.
    - Solo escribe cuando la decisión está en ESTADOS_ASOCIAN; el resto queda sin tocar.
    - commit=False deja la transacción abierta (pruebas con rollback).
    """
    bloqueado = db.execute(text("SELECT pg_try_advisory_lock(hashtext(:k))"),
                           {"k": _LOCK_CLAVE}).scalar()
    if not bloqueado:
        raise RuntimeError("Ya hay una aplicación de asociación SIGSA-3 en curso")
    try:
        indice = IndicePacientes(_cargar_pacientes(db))
        consultas = _cargar_consultas(db)
        filas = _pendientes(db, limit)

        conteo: Counter = Counter()           # estado de paciente
        motivo_consulta: Counter = Counter()  # resultado de consulta
        creados = pacientes_asignados = consultas_asignadas = 0
        cambios_lote = 0
        siguiente_virtual = -1                # ids provisionales en dry_run

        for f in filas:
            ya_paciente = f.paciente_id is not None
            if ya_paciente:
                pid = int(f.paciente_id)
                estado_pac = None
            else:
                reg = Registro(
                    rid=int(f.id), nombre=f.nombre_paciente,
                    sexo=normalizar_sexo(f.sexo),
                    nhc=normalizar_identificador(f.no_historia_clinica),
                )
                d = asociar(reg, indice)
                estado_pac = d.estado
                conteo[d.estado] += 1
                if d.estado not in ESTADOS_ASOCIAN:
                    continue
                if d.estado == CREAR:
                    if dry_run:
                        pid = siguiente_virtual
                        siguiente_virtual -= 1
                    else:
                        pid = _crear_paciente(db, reg.nombre, reg.sexo, reg.nhc, reg.rid)
                    indice.agregar(Paciente(pid, reg.nombre, reg.sexo, reg.nhc, creado=True))
                    consultas.setdefault(pid, [])
                    creados += 1
                else:
                    pid = d.paciente_id

            cid = None
            if f.consulta_id is None:
                cid, motivo = asociar_consulta(
                    f.fecha_consulta, f.tipo_consulta,
                    normalizar_identificador(f.no_historia_clinica),
                    consultas.get(pid, []),
                )
                motivo_consulta[motivo] += 1

            if not dry_run:
                creado_flag = (pid >= 0 and any(p.pac_id == pid and p.creado for p in indice.pacientes))
                db.execute(text(
                    "INSERT INTO sigsa3_asociacion (sigsa3_id, estado, paciente_id, pacientes_sigsa3_id, "
                    "metodo, motivo, score, margen, version, aplicado, usuario) "
                    "VALUES (:s, :e, :p, :ps, :m, :mo, :sc, :mg, :v, TRUE, :u) "
                    "ON CONFLICT (sigsa3_id) DO UPDATE SET estado=EXCLUDED.estado, "
                    "paciente_id=EXCLUDED.paciente_id, pacientes_sigsa3_id=EXCLUDED.pacientes_sigsa3_id, "
                    "metodo=EXCLUDED.metodo, motivo=EXCLUDED.motivo, score=EXCLUDED.score, "
                    "margen=EXCLUDED.margen, version=EXCLUDED.version, aplicado=EXCLUDED.aplicado, "
                    "usuario=EXCLUDED.usuario, creado_en=CURRENT_TIMESTAMP"
                ), {
                    "s": int(f.id), "e": estado_pac or ("ya_asociado" if ya_paciente else "pendiente"),
                    "p": pid if (not creado_flag and pid >= 0) else None,
                    "ps": pid if creado_flag else None,
                    "m": None, "mo": None, "sc": None, "mg": None, "v": VERSION, "u": usuario,
                })
                if pid < 0:
                    # dry_run: pid virtual, no se escribe
                    pass
                else:
                    creado = any(p.pac_id == pid and p.creado for p in indice.pacientes) if hasattr(indice, "pacientes") else False
                    if creado:
                        db.execute(text(
                            "UPDATE sigsa3 SET pacientes_sigsa3_id = COALESCE(pacientes_sigsa3_id, :p), "
                            "                  consulta_id = COALESCE(consulta_id, :c) WHERE id = :s"
                        ), {"p": pid, "c": cid, "s": int(f.id)})
                    else:
                        db.execute(text(
                            "UPDATE sigsa3 SET paciente_id = COALESCE(paciente_id, :p), "
                            "                  consulta_id = COALESCE(consulta_id, :c) WHERE id = :s"
                        ), {"p": pid, "c": cid, "s": int(f.id)})
                cambios_lote += 1
                if commit and cambios_lote >= LOTE:
                    db.commit()
                    cambios_lote = 0

            if estado_pac is not None:
                pacientes_asignados += 1
            if cid is not None:
                consultas_asignadas += 1

        if not dry_run and commit:
            db.commit()

        return {
            "version": VERSION,
            "modo": "dry_run" if dry_run else "aplicado",
            "registros_pendientes": len(filas),
            "pacientes_creados": creados,
            "pacientes_asignados": pacientes_asignados,
            "consultas_asignadas": consultas_asignadas,
            "estados_paciente": dict(conteo),
            "resultado_consulta": dict(motivo_consulta),
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.execute(text("SELECT pg_advisory_unlock(hashtext(:k))"), {"k": _LOCK_CLAVE})
