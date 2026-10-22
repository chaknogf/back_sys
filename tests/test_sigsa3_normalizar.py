"""Tests de normalizar() de SIGSA-3: migración a sigsa3_registros permitiendo
registros SIN paciente (con datos crudos preservados) y resolución de
paciente_id por cadena expediente -> documento de consulta -> CUI."""

import time as _time
from datetime import date

from core.database import SessionLocal
from modules.sigsa3.models import Sigsa3Model, Sigsa3RegistroModel
from modules.sigsa3.service import normalizar, _nhc_a_entero
from modules.pacientes.models import PacienteModel


def _sufijo():
    return str(int(_time.time() * 1000000))[-6:]


def _cleanup(paciente_id=None, consulta_id=None, sigsa3_ids=None):
    db = SessionLocal()
    try:
        if sigsa3_ids:
            db.query(Sigsa3Model).filter(Sigsa3Model.id.in_(sigsa3_ids)).delete(
                synchronize_session=False
            )
            db.query(Sigsa3RegistroModel).filter(
                Sigsa3RegistroModel.sigsa3_id.in_(sigsa3_ids)
            ).delete(synchronize_session=False)
        if consulta_id is not None:
            db.execute(
                __import__("sqlalchemy").text("DELETE FROM consultas WHERE id = :i"),
                {"i": consulta_id},
            )
        if paciente_id is not None:
            db.query(PacienteModel).filter(PacienteModel.id == paciente_id).delete(
                synchronize_session=False
            )
        db.commit()
    finally:
        db.close()


def test_nhc_a_entero_expande_notacion_cientifica():
    assert _nhc_a_entero("1.78837E+12") == "1788370000000"
    assert _nhc_a_entero("2.37202E+12") == "2372020000000"
    assert _nhc_a_entero("10153") is None
    assert _nhc_a_entero("1.45E-24") is None
    assert _nhc_a_entero(None) is None


def test_normalizar_sin_paciente_preserva_crudos():
    """Un registro sin NH que cruce con nadie se normaliza igual, sin paciente,
    con sin_asociar=True y conservando los valores crudos."""
    s = _sufijo()
    db = SessionLocal()
    sigsa3_id = None
    try:
        reg = Sigsa3Model(
            nombre_paciente=f"PACIENTE SIN MATCH {s}",
            no_historia_clinica="",
            sexo="M",
            edad_anios=33,
            tipo_consulta="3 Emergencia",
            codigo_cie_10="J:18:9",
            personal_salud=f"MEDICO INEXISTENTE {s}",
            fecha_consulta=date.today(),
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)
        sigsa3_id = reg.id
    finally:
        db.close()

    db = SessionLocal()
    try:
        res = normalizar(db, ids=[sigsa3_id], dry_run=False)
    finally:
        db.close()

    assert res["migrados"] == 1
    db = SessionLocal()
    try:
        out = db.query(Sigsa3RegistroModel).filter(
            Sigsa3RegistroModel.sigsa3_id == sigsa3_id
        ).first()
        assert out is not None
        assert out.paciente_id is None
        assert out.sin_asociar is True
        assert out.nombre_paciente == f"PACIENTE SIN MATCH {s}"
        assert out.edad_anios == 33
        assert out.tipo_consulta == "3 Emergencia"
        assert out.codigo_cie_10 == "J:18:9"
        assert out.personal_salud == f"MEDICO INEXISTENTE {s}"
    finally:
        db.close()
        _cleanup(sigsa3_ids=[sigsa3_id])


def test_normalizar_resuelve_paciente_por_documento_de_consulta():
    """Si el no_historia_clinica coincide con consultas.documento, se resuelve el
    paciente aunque no haya coincidencia con expediente ni CUI."""
    s = _sufijo()
    db = SessionLocal()
    paciente_id = None
    consulta_id = None
    sigsa3_id = None
    doc = f"9{s}9"
    try:
        pac = PacienteModel(
            nombre={
                "primer_nombre": "DOC",
                "primer_apellido": f"Match{s}",
            },
            sexo="F",
            fecha_nacimiento=date(1990, 1, 1),
        )
        db.add(pac)
        db.commit()
        db.refresh(pac)
        paciente_id = pac.id

        from modules.consultas.models import ConsultaModel
        from datetime import time as _t
        con = ConsultaModel(
            paciente_id=paciente_id,
            tipo_consulta=3,
            especialidad="MEDICINA GENERAL",
            servicio="EMERGENCIA",
            documento=doc,
            fecha_consulta=date.today(),
            hora_consulta=_t(10, 0),
            activo=True,
        )
        db.add(con)
        db.commit()
        db.refresh(con)
        consulta_id = con.id

        reg = Sigsa3Model(
            nombre_paciente=f"NOMBRE DISTINTO {s}",
            no_historia_clinica=doc,
            sexo="F",
            edad_anios=36,
            tipo_consulta="1 Primera",
            codigo_cie_10="Z:00:0",
            fecha_consulta=date.today(),
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)
        sigsa3_id = reg.id
    finally:
        db.close()

    db = SessionLocal()
    try:
        res = normalizar(db, ids=[sigsa3_id], dry_run=False)
        assert res["resoluciones"]["paciente_resuelto_en_normalizacion"] == 1
    finally:
        db.close()

    db = SessionLocal()
    try:
        out = db.query(Sigsa3RegistroModel).filter(
            Sigsa3RegistroModel.sigsa3_id == sigsa3_id
        ).first()
        assert out.paciente_id == paciente_id
        assert out.sin_asociar is False
    finally:
        db.close()
        _cleanup(paciente_id=paciente_id, consulta_id=consulta_id, sigsa3_ids=[sigsa3_id])
