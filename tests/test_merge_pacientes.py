"""Tests unitarios del merge de pacientes (merge_router).

Cubren la semántica de fusión: saneo de basura (nan/0/''), preferir el contacto
más completo, completar teléfonos en referencias existentes y CUI alternativo.
No requieren BD: operan sobre instancias de PacienteModel en memoria.
"""

import pytest

from modules.pacientes.models import PacienteModel
from modules.pacientes.merge_router import (
    _es_vacio,
    merge_contacto,
    merge_referencias,
    merge_campos_unicos,
    merge_datos_extra,
    merge_expedientes_anteriores,
    _fill_campos_vacios,
)


def _pac(**kw) -> PacienteModel:
    p = PacienteModel(nombre={})
    for k, v in kw.items():
        setattr(p, k, v)
    return p


class TestEsVacio:
    def test_basura_es_vacia(self):
        for v in [None, "", "  ", "nan", "NaN", "null", "N/A", "0"]:
            assert _es_vacio(v), f"{v!r} debería ser vacío"
        assert _es_vacio(0)

    def test_valores_reales_no_vacios(self):
        for v in ["50448445", "0406", 123, "ANTHONY"]:
            assert not _es_vacio(v), f"{v!r} NO debería ser vacío"


class TestContacto:
    def test_prefiere_el_mas_completo(self):
        pri = _pac(contacto={"domicilio": "ALDE APACORRAL", "telefonos": "50448445"})
        dup = _pac(contacto={"domicilio": "ALDEA APACORRAL, SECTOR 2", "telefonos": "55667788"})

        merge_contacto(pri, dup)

        assert pri.contacto["domicilio"] == "ALDEA APACORRAL, SECTOR 2"
        assert set(pri.contacto["telefonos"]) == {"50448445", "55667788"}

    def test_rellena_basura(self):
        pri = _pac(contacto={"domicilio": "nan", "municipio": ""})
        dup = _pac(contacto={"domicilio": "2-21 zona 4", "municipio": "0405"})

        merge_contacto(pri, dup)

        assert pri.contacto["domicilio"] == "2-21 zona 4"
        assert pri.contacto["municipio"] == "0405"


class TestReferencias:
    def test_completa_telefono_en_referencia_existente(self):
        pri = _pac(referencias=[
            {"nombre": "pedro garcia", "telefono": None, "parentesco": "padre"}
        ])
        dup = _pac(referencias=[
            {"nombre": "PEDRO GARCIA", "telefono": "46730042", "parentesco": "Padre"}
        ])

        merge_referencias(pri, dup)

        assert len(pri.referencias) == 1
        assert pri.referencias[0]["telefono"] == "46730042"

    def test_agrega_referencia_nueva(self):
        pri = _pac(referencias=[{"nombre": "ana", "parentesco": "madre"}])
        dup = _pac(referencias=[{"nombre": "luis", "parentesco": "padre"}])

        merge_referencias(pri, dup)

        assert len(pri.referencias) == 2


class TestCamposUnicos:
    def test_cui_basura_se_reemplaza(self, db_session):
        pri = _pac(cui=0)
        dup = _pac(cui=2543219870101)
        setattr(pri, "expediente", None)
        setattr(dup, "expediente", None)

        merge_campos_unicos(pri, dup, db_session)

        assert pri.cui == 2543219870101

    def test_cui_se_copia_tras_liberar_dup(self, db_session):
        """El flujo del endpoint captura el snapshot de los campos únicos, libera
        el UNIQUE del duplicado (cui=None) y copia desde el snapshot al principal,
        evitando la violación de pacientes_cui_key."""
        pri = _pac(cui=None)
        dup = _pac(cui=2543219870500)
        setattr(pri, "expediente", None)
        setattr(dup, "expediente", None)
        setattr(pri, "pasaporte", None)
        setattr(dup, "pasaporte", None)

        valores_dup = {
            "cui": dup.cui,
            "expediente": dup.expediente,
            "pasaporte": dup.pasaporte,
        }
        dup.cui = None
        merge_campos_unicos(pri, dup, db_session, valores_dup)

        assert pri.cui == 2543219870500
        assert dup.cui is None

    def test_cui_duplicado_va_a_personaid(self, db_session):
        """Si el principal ya tiene CUI, el CUI del duplicado se guarda en
        datos_extra.personaid (string) en vez de sobrescribir."""
        pri = _pac(cui=2543219870101)
        dup = _pac(cui=3596692999005)
        setattr(pri, "expediente", None)
        setattr(dup, "expediente", None)
        setattr(pri, "pasaporte", None)
        setattr(dup, "pasaporte", None)

        merge_campos_unicos(pri, dup, db_session)

        assert pri.cui == 2543219870101
        assert pri.datos_extra["personaid"] == "3596692999005"

    def test_cui_alterno_extra_se_agrega_con_espacio(self, db_session):
        """Si el principal ya tiene personaid, un CUI alterno adicional se agrega
        al final separado por espacio."""
        pri = _pac(cui=2543219870101, datos_extra={"personaid": "1111111111111"})
        dup = _pac(cui=3596692999005)
        setattr(pri, "expediente", None)
        setattr(dup, "expediente", None)
        setattr(pri, "pasaporte", None)
        setattr(dup, "pasaporte", None)

        merge_campos_unicos(pri, dup, db_session)

        assert pri.datos_extra["personaid"] == "1111111111111 3596692999005"


class TestExpedientesAnteriores:
    def test_expediente_dup_va_a_anteriores(self):
        pri = _pac(expediente="26A-100")
        dup = _pac(expediente="26A-200")

        merge_expedientes_anteriores(pri, dup)

        assert pri.datos_extra["expedientes_anteriores"] == ["26A-200"]

    def test_expediente_desde_snapshot_tras_liberar(self):
        """El endpoint libera dup.expediente=None antes de llamar la función; el
        valor original se pasa por snapshot."""
        pri = _pac(expediente="26A-100")
        dup = _pac(expediente=None)

        merge_expedientes_anteriores(pri, dup, "26A-200")

        assert pri.datos_extra["expedientes_anteriores"] == ["26A-200"]

    def test_no_duplica_expediente_igual_al_principal(self):
        pri = _pac(expediente="26A-100")
        dup = _pac(expediente="26A-100")

        merge_expedientes_anteriores(pri, dup)

        assert not (pri.datos_extra or {}).get("expedientes_anteriores")


class TestFillCamposVacios:
    def test_rellena_basura(self):
        pri = _pac(sexo="", ocupacion="nan", fecha_nacimiento=None)
        dup = _pac(sexo="F", ocupacion="AMA DE CASA", fecha_nacimiento="1990-01-01")

        _fill_campos_vacios(pri, dup)

        assert pri.sexo == "F"
        assert pri.ocupacion == "AMA DE CASA"
        assert str(pri.fecha_nacimiento) == "1990-01-01"

    def test_no_pisa_valor_bueno(self):
        pri = _pac(sexo="M", nacionalidad="GTM")
        dup = _pac(sexo="F", nacionalidad="MEX")

        _fill_campos_vacios(pri, dup)

        assert pri.sexo == "M"
        assert pri.nacionalidad == "GTM"


class TestDatosExtra:
    def test_deep_fill_ignora_basura(self):
        pri = _pac(datos_extra={"demograficos": {"idioma": "nan", "pueblo": None}})
        dup = _pac(datos_extra={"demograficos": {"idioma": "1", "pueblo": "2"}})

        merge_datos_extra(pri, dup)

        assert pri.datos_extra["demograficos"]["idioma"] == "1"
        assert pri.datos_extra["demograficos"]["pueblo"] == "2"


class TestMergeIntegracion:
    """Prueba el endpoint real POST /pacientes/merge contra la BD.

    Cubre el bug de UniqueViolation: el principal no tiene CUI y el duplicado sí;
    al fusionar, el CUI debe copiarse sin violar pacientes_cui_key.
    """

    def _crear_paciente(self, client, auth_headers, sufijo: str, **campos):
        payload = {
            "nombre": {
                "primer_nombre": f"TESTMERGE{sufijo}",
                "primer_apellido": "ZZTEST",
            },
            "sexo": "M",
            "fecha_nacimiento": f"19{int(sufijo[-2:]):02d}-01-01",
        }
        payload.update(campos)
        r = client.post("/pacientes/", json=payload, headers=auth_headers)
        if r.status_code == 409:
            pytest.skip("Residuo de prueba (TESTMERGE...) ya presente en la BD")
        assert r.status_code == 201, r.text
        return r.json()["id"]

    def test_merge_copia_cui_sin_violar_unique(self, client, auth_headers, db_session):
        import time as _time

        stamp = str(int(_time.time()))[-6:]
        cui_dup = 3596692999001
        principal_id = self._crear_paciente(client, auth_headers, f"90{stamp}")
        dup_id = self._crear_paciente(client, auth_headers, f"91{stamp}", cui=cui_dup)

        try:
            r = client.post(
                "/pacientes/merge",
                params={"principal_id": principal_id, "ids": [principal_id, dup_id]},
                headers=auth_headers,
            )
            assert r.status_code == 200, r.text

            detail = client.get(f"/pacientes/{principal_id}", headers=auth_headers).json()
            assert detail["cui"] == cui_dup
        finally:
            self._limpiar(db_session, principal_id, dup_id)

    def _limpiar(self, db_session, *ids):
        """Borra los pacientes de prueba evitando las FKs. Usa
        session_replication_role=replica solo durante el DELETE (BD local de test)."""
        from sqlalchemy import text

        db_session.execute(text("SET session_replication_role = replica"))
        try:
            for pid in ids:
                db_session.execute(
                    text("DELETE FROM pacientes WHERE id = :pid"), {"pid": pid}
                )
        finally:
            db_session.execute(text("SET session_replication_role = origin"))
        db_session.commit()
