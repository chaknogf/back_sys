"""Auto-fusión de pacientes duplicados (sin intervención humana)."""
from __future__ import annotations
from typing import Dict, List, Set, Tuple, Generator

from sqlalchemy import text
from sqlalchemy.orm import Session

from modules.pacientes.duplicados_service import buscar_pares_duplicados
from modules.pacientes.merge_router import (
    merge_telefonos, merge_campos_unicos, _fill_campos_vacios,
    merge_datos_extra, merge_referencias, merge_expedientes_anteriores,
    merge_nombre,
)
from modules.pacientes.models import PacienteModel
from modules.pacientes.service import agregar_evento


_DEPENDIENTES: List[Tuple[str, str]] = [
    ("consultas", "paciente_id"),
    ("citas", "paciente_id"),
    ("constancias_nacimiento", "paciente_id"),
    ("constancias_nacimiento", "madre_id"),
    ("nacimientos", "paciente_id"),
    ("nacimientos", "madre_id"),
    ("defunciones", "paciente_id"),
    ("defunciones", "madre_id"),
    ("sigsa3", "paciente_id"),
    ("sigsa3_registros", "paciente_id"),
    ("quirofano", "paciente_id"),
    ("prestamos", "id_paciente"),
]


def _union_find(pares: List[Tuple[int, int]]) -> Dict[int, int]:
    parent: Dict[int, int] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in pares:
        union(a, b)
    for x in list(parent.keys()):
        parent[x] = find(x)
    return parent


def _completitud(p: PacienteModel) -> int:
    score = 0
    if p.cui is not None:
        score += 2
    if p.expediente:
        score += 2
    if p.fecha_nacimiento is not None:
        score += 1
    if p.contacto:
        score += 1
    if p.datos_extra:
        score += 1
    if p.referencias:
        score += 1
    if p.sexo:
        score += 1
    return score


def _reasignar_dependientes(db: Session, dup_id: int, master_id: int) -> None:
    for tabla, col in _DEPENDIENTES:
        try:
            db.execute(
                text(f"UPDATE {tabla} SET {col} = :m WHERE {col} = :d"),
                {"m": master_id, "d": dup_id},
            )
        except Exception:
            pass


def auto_merge_duplicados(
    db: Session,
    umbral: float = 0.90,
    incluir_fecha: bool = True,
    usuario: str = "sistema",
) -> Generator[dict, None, None]:
    yield {"step": "load", "progress": 0, "message": "Detectando pacientes duplicados..."}

    pares = buscar_pares_duplicados(db, incluir_fecha, umbral)
    yield {"step": "pairs", "progress": 10, "message": f"Pares duplicados encontrados: {len(pares)}", "pares": len(pares)}

    if not pares:
        yield {"step": "done", "progress": 100, "message": "No hay duplicados para fusionar.",
               "grupos": 0, "fusionados": 0, "maestros": [], "pares": 0}
        return

    parent = _union_find(pares)
    grupos: Dict[int, List[int]] = {}
    for node in parent:
        grupos.setdefault(parent[node], []).append(node)
    clusters = [g for g in grupos.values() if len(g) > 1]

    yield {"step": "clusters", "progress": 20, "message": f"Grupos a fusionar: {len(clusters)}", "grupos": len(clusters)}

    maestros: List[int] = []
    total_fusionados = 0
    procesados: Set[int] = set()
    total_clusters = len(clusters) or 1

    for idx, cluster in enumerate(clusters):
        if any(x in procesados for x in cluster):
            continue
        pacs = (
            db.query(PacienteModel)
            .filter(PacienteModel.id.in_(cluster), PacienteModel.estado != "I")
            .all()
        )
        if len(pacs) < 2:
            continue
        master = sorted(pacs, key=lambda p: (-_completitud(p), p.id))[0]
        duplicados = [p for p in pacs if p.id != master.id]

        progress = 20 + int((idx / total_clusters) * 70)
        yield {"step": "merge", "progress": progress,
               "message": f"Fusionando grupo {idx + 1}/{total_clusters} (maestro {master.id}, {len(duplicados)} duplicados)",
               "maestro": master.id, "duplicados": [d.id for d in duplicados]}

        try:
            for dup in duplicados:
                if dup.estado == "I":
                    continue

                # Snapshot de los campos únicos ANTES de liberarlos.
                valores_dup = {
                    "cui": dup.cui,
                    "expediente": dup.expediente,
                    "pasaporte": dup.pasaporte,
                }

                # Liberar el UNIQUE del duplicado y persistir (flush) antes de
                # copiar su cui/expediente/pasaporte al maestro.
                if dup.cui is not None:
                    if dup.datos_extra is None:
                        dup.datos_extra = {}
                    if "personaid" not in dup.datos_extra:
                        dup.datos_extra["personaid"] = str(dup.cui)
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(dup, "datos_extra")

                dup.cui = None
                dup.expediente = None
                dup.pasaporte = None
                db.flush()

                merge_telefonos(master, dup)
                merge_nombre(master, dup)
                merge_campos_unicos(master, dup, db, valores_dup)
                _fill_campos_vacios(master, dup)
                merge_datos_extra(master, dup)
                merge_referencias(master, dup)
                merge_expedientes_anteriores(master, dup, valores_dup.get("expediente"))

                _reasignar_dependientes(db, dup.id, master.id)

                dup.estado = "I"

                agregar_evento(dup, usuario=usuario, accion="AUTO_MERGE",
                              expediente_duplicado=True,
                              detalle=f"Fusionado automáticamente en paciente {master.id}")
                agregar_evento(master, usuario=usuario, accion="AUTO_MERGE",
                              expediente_duplicado=False,
                              detalle=f"Fusionado paciente {dup.id}")

            db.commit()
            db.refresh(master)
            maestros.append(master.id)
            total_fusionados += len(duplicados)
            procesados.update(cluster)
        except Exception as e:
            db.rollback()
            yield {"step": "error", "progress": progress,
                   "message": f"Error en grupo {master.id}: {str(e)}"}
            continue

    yield {"step": "done", "progress": 100,
           "message": f"Auto-merge completado: {total_fusionados} fusionados en {len(maestros)} maestros.",
           "grupos": len(clusters), "fusionados": total_fusionados,
           "maestros": maestros, "pares": len(pares)}