"""Tests de integración del módulo de insumos.

Cubre: import CSV del catálogo, CRUD, ingreso/ajuste de lotes + kardex,
flujo requisición → despacho, traslado entre almacenes, atenciones con
consumo y unidosis (preparar/administrar/cancelar).

Los datos de prueba usan códigos con prefijo TI/TP + sufijo único y se
eliminan al final del módulo en orden de dependencias de FK.
"""

import uuid

import pytest

from core.database import SessionLocal
from modules.users.models import UserModel
from modules.insumos.models import (
    Insumo,
    Presentacion,
    Lote,
    KardexMovimiento,
    Requisicion,
    RequisicionDetalle,
    Despacho,
    DespachoDetalle,
    Atencion,
    AtencionInsumo,
    Unidosis,
    UnidosisDetalle,
)
from modules.encamamiento.models import EncamamientoModel
from modules.pacientes.models import PacienteModel


def _suf() -> str:
    return uuid.uuid4().hex[:8].upper()


# IDs creados por los tests; se borran al final en orden inverso de FKs.
_reg = {
    "insumos": [],
    "presentaciones": [],
    "lotes": [],
    "requisiciones": [],
    "despachos": [],
    "atenciones": [],
    "unidosis": [],
    "servicios": [],
    "pacientes": [],
}


@pytest.fixture(scope="module", autouse=True)
def _limpieza(db_session):
    yield
    db = SessionLocal()
    try:
        for uid in _reg["unidosis"]:
            db.query(UnidosisDetalle).filter(UnidosisDetalle.unidosis_id == uid).delete(
                synchronize_session=False
            )
        db.query(Unidosis).filter(Unidosis.id.in_(_reg["unidosis"])).delete(
            synchronize_session=False
        )
        for aid in _reg["atenciones"]:
            db.query(AtencionInsumo).filter(AtencionInsumo.atencion_id == aid).delete(
                synchronize_session=False
            )
        db.query(Atencion).filter(Atencion.id.in_(_reg["atenciones"])).delete(
            synchronize_session=False
        )
        for did in _reg["despachos"]:
            db.query(DespachoDetalle).filter(DespachoDetalle.despacho_id == did).delete(
                synchronize_session=False
            )
        db.query(Despacho).filter(Despacho.id.in_(_reg["despachos"])).delete(
            synchronize_session=False
        )
        db.query(KardexMovimiento).filter(
            KardexMovimiento.lote_id.in_(_reg["lotes"])
        ).delete(synchronize_session=False)
        db.query(Lote).filter(Lote.id.in_(_reg["lotes"])).delete(synchronize_session=False)
        for rid in _reg["requisiciones"]:
            db.query(RequisicionDetalle).filter(
                RequisicionDetalle.requisicion_id == rid
            ).delete(synchronize_session=False)
        db.query(Requisicion).filter(Requisicion.id.in_(_reg["requisiciones"])).delete(
            synchronize_session=False
        )
        db.query(Presentacion).filter(
            Presentacion.id.in_(_reg["presentaciones"])
        ).delete(synchronize_session=False)
        db.query(Insumo).filter(Insumo.id.in_(_reg["insumos"])).delete(
            synchronize_session=False
        )
        db.query(EncamamientoModel).filter(
            EncamamientoModel.id.in_(_reg["servicios"])
        ).delete(synchronize_session=False)
        db.query(PacienteModel).filter(
            PacienteModel.id.in_(_reg["pacientes"])
        ).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def _almacen(client, auth_headers, tipo: str) -> int:
    r = client.get(f"/insumos/almacenes?tipo={tipo}", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert items, f"No hay almacenes de tipo '{tipo}' (seeds de la migración 084)"
    return items[0]["id"]


# =====================================================================
# 1. CATÁLOGO: import CSV + CRUD
# =====================================================================
class TestCatalogo:
    def test_importar_csv(self, client, auth_headers):
        s1, s2, s3 = _suf(), _suf(), _suf()
        csv = (
            "RENGLÓN\tCÓDIGO DE INSUMO\tNOMBRE\tCARACTERÍSTICAS\t"
            "NOMBRE DE LA PRESENTACIÓN\tCANTIDAD Y UNIDAD DE MEDIDA DE LA PRESENTACIÓN\t"
            "CÓDIGO DE PRESENTACIÓN\n"
            f"261\tTI{s1}\tTest Insumo Import\t Estado: Líquido;  Grado: Reactivo; \t"
            f"Envase\t250 Mililitro\tTP{s1}\n"
            f"261\tTI{s1}\tTest Insumo Import\t Estado: Líquido;  Grado: Reactivo; \t"
            f"Envase\t1 Gramos\tTP{s2}\n"
            f"261\t\tTest Sin Código\tX\tEnvase\t1 Unidad\tTP{s3}\n"
        )
        r = client.post(
            "/insumos/importar-csv",
            headers=auth_headers,
            files={"file": ("catalogo.csv", csv, "text/csv")},
        )
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["filas"] == 3
        assert data["insumos_creados"] == 1
        assert data["presentaciones_creadas"] == 2
        assert len(data["errores"]) == 1
        assert data["errores"][0]["fila"] == 4

        # Idempotencia: reimportar sin cambios no duplica ni "actualiza".
        r2 = client.post(
            "/insumos/importar-csv",
            headers=auth_headers,
            files={"file": ("catalogo.csv", csv, "text/csv")},
        )
        assert r2.status_code == 200
        data2 = r2.json()
        assert data2["insumos_creados"] == 0
        assert data2["insumos_actualizados"] == 0
        assert data2["presentaciones_creadas"] == 0
        assert data2["filas"] == 3

        r3 = client.get(f"/insumos/?codigo=TI{s1}", headers=auth_headers)
        items = r3.json()["items"]
        assert len(items) == 1
        _reg["insumos"].append(items[0]["id"])
        for p in client.get(
            f"/insumos/presentaciones?insumo_id={items[0]['id']}", headers=auth_headers
        ).json()["items"]:
            _reg["presentaciones"].append(p["id"])

        # Características quedan CRUDAS (con sus espacios del Excel).
        detalle = client.get(f"/insumos/{items[0]['id']}", headers=auth_headers).json()
        assert detalle["caracteristicas"].startswith(" Estado:")

    def test_crear_insumo_y_duplicado(self, client, auth_headers):
        s = _suf()
        payload = {
            "renglon": "011",
            "codigo_insumo": f"TI{s}",
            "nombre": "Test Insumo Manual",
            "caracteristicas": " Estado: Sólido; ",
        }
        r = client.post("/insumos/", headers=auth_headers, json=payload)
        assert r.status_code == 201, r.text
        insumo_id = r.json()["id"]
        _reg["insumos"].append(insumo_id)
        # renglon conserva el cero a la izquierda
        assert r.json()["renglon"] == "011"

        r2 = client.post("/insumos/", headers=auth_headers, json=payload)
        assert r2.status_code == 409

        r3 = client.put(
            f"/insumos/{insumo_id}",
            headers=auth_headers,
            json={"nombre": "Test Insumo Renombrado"},
        )
        assert r3.status_code == 200
        assert r3.json()["nombre"] == "Test Insumo Renombrado"

    def test_presentaciones_crud(self, client, auth_headers):
        s = _suf()
        r = client.post(
            "/insumos/",
            headers=auth_headers,
            json={"renglon": "261", "codigo_insumo": f"TI{s}", "nombre": "Test Pres Base"},
        )
        assert r.status_code == 201
        insumo_id = r.json()["id"]
        _reg["insumos"].append(insumo_id)

        r2 = client.post(
            "/insumos/presentaciones",
            headers=auth_headers,
            json={
                "insumo_id": insumo_id,
                "codigo_presentacion": f"TP{s}",
                "nombre": "Envase",
                "cantidad_unidad": "100 Mililitro",
            },
        )
        assert r2.status_code == 201, r2.text
        pres_id = r2.json()["id"]
        _reg["presentaciones"].append(pres_id)

        r3 = client.get(f"/insumos/presentaciones/{pres_id}", headers=auth_headers)
        assert r3.status_code == 200
        assert r3.json()["codigo_presentacion"] == f"TP{s}"

        r4 = client.put(
            f"/insumos/presentaciones/{pres_id}",
            headers=auth_headers,
            json={"cantidad_unidad": "200 Mililitro"},
        )
        assert r4.status_code == 200
        assert r4.json()["cantidad_unidad"] == "200 Mililitro"

        r5 = client.post(
            "/insumos/presentaciones",
            headers=auth_headers,
            json={"insumo_id": insumo_id, "codigo_presentacion": f"TP{s}"},
        )
        assert r5.status_code == 409


# =====================================================================
# 2. ALMACÉN: lotes, kardex, requisición → despacho, traslado
# =====================================================================
class TestAlmacenFlujos:
    lote_id = None
    presentacion_id = None
    bodega_id = None
    farmacia_id = None
    servicio_id = None

    @classmethod
    def _preparar_base(cls, client, auth_headers):
        """Insumo+presentación con lote de 100 en bodega (creado una vez)."""
        s = _suf()
        r = client.post(
            "/insumos/",
            headers=auth_headers,
            json={"renglon": "261", "codigo_insumo": f"TI{s}", "nombre": "Test Flujo"},
        )
        _reg["insumos"].append(r.json()["id"])
        cls.presentacion_id = r.json()["id"]
        r2 = client.post(
            "/insumos/presentaciones",
            headers=auth_headers,
            json={
                "insumo_id": r.json()["id"],
                "codigo_presentacion": f"TP{s}",
                "nombre": "Envase",
                "cantidad_unidad": "250 Mililitro",
            },
        )
        _reg["presentaciones"].append(r2.json()["id"])
        cls.presentacion_id = r2.json()["id"]

        cls.bodega_id = _almacen(client, auth_headers, "bodega")
        cls.farmacia_id = _almacen(client, auth_headers, "farmacia")

        r3 = client.post(
            "/insumos/lotes/ingreso",
            headers=auth_headers,
            json={
                "presentacion_id": cls.presentacion_id,
                "almacen_id": cls.bodega_id,
                "numero_lote": f"L{s}",
                "cantidad": 100,
                "costo_unitario": 5.5,
                "observacion": "Ingreso test",
            },
        )
        assert r3.status_code == 201, r3.text
        cls.lote_id = r3.json()["id"]
        _reg["lotes"].append(cls.lote_id)
        assert float(r3.json()["cantidad_actual"]) == 100.0

    def test_01_ingreso_y_kardex(self, client, auth_headers):
        self._preparar_base(client, auth_headers)
        r = client.get(f"/insumos/kardex/lote/{self.lote_id}", headers=auth_headers)
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 1
        assert items[0]["tipo_movimiento"] == "entrada"
        assert float(items[0]["saldo_resultante"]) == 100.0

        # Recarga del mismo lote (upsert por presentación+almacén+número)
        r2 = client.post(
            "/insumos/lotes/ingreso",
            headers=auth_headers,
            json={
                "presentacion_id": self.presentacion_id,
                "almacen_id": self.bodega_id,
                "numero_lote": f"L{_suf()}",  # número distinto → lote nuevo
                "cantidad": 50,
            },
        )
        assert r2.status_code == 201
        _reg["lotes"].append(r2.json()["id"])

    def test_02_ajuste(self, client, auth_headers):
        r = client.post(
            "/insumos/lotes/ajuste",
            headers=auth_headers,
            json={"lote_id": self.lote_id, "cantidad_nueva": 90, "observacion": "Conteo"},
        )
        assert r.status_code == 200, r.text
        assert float(r.json()["cantidad_actual"]) == 90.0

        k = client.get(f"/insumos/kardex/lote/{self.lote_id}", headers=auth_headers).json()
        assert k["items"][0]["tipo_movimiento"] == "ajuste"
        assert float(k["items"][0]["saldo_resultante"]) == 90.0

    def test_03_requisicion_y_despacho(self, client, auth_headers):
        r = client.post(
            "/encamamiento/",
            json={"nombre_servicio": f"TEST-INSUMOS-{_suf()}", "camas_censables": 5},
        )
        assert r.status_code in (200, 201), r.text
        self.servicio_id = r.json()["id"]
        _reg["servicios"].append(self.servicio_id)

        r2 = client.post(
            "/insumos/requisiciones",
            headers=auth_headers,
            json={
                "servicio_solicitante_id": self.servicio_id,
                "detalles": [{"presentacion_id": self.presentacion_id, "cantidad_solicitada": 10}],
            },
        )
        assert r2.status_code == 201, r2.text
        req = r2.json()
        _reg["requisiciones"].append(req["id"])
        assert req["estado"] == "pendiente"
        assert req["numero"].startswith("REQ-")

        r3 = client.post(
            f"/insumos/requisiciones/{req['id']}/aprobar",
            headers=auth_headers,
            json={"observaciones": "Autorizado test"},
        )
        assert r3.status_code == 200
        assert r3.json()["estado"] == "aprobada"

        # Despachar sin aprobar no aplica (ya aprobada), ahora el despacho:
        r4 = client.post(
            "/insumos/despachos",
            headers=auth_headers,
            json={
                "tipo": "servicio",
                "almacen_origen_id": self.bodega_id,
                "requisicion_id": req["id"],
                "servicio_destino_id": self.servicio_id,
                "detalles": [{"lote_id": self.lote_id, "cantidad": 10}],
            },
        )
        assert r4.status_code == 201, r4.text
        desp = r4.json()
        _reg["despachos"].append(desp["id"])
        assert desp["estado"] == "borrador"
        assert desp["numero"].startswith("DES-")

        r5 = client.post(
            f"/insumos/despachos/{desp['id']}/despachar", headers=auth_headers
        )
        assert r5.status_code == 200, r5.text
        assert r5.json()["estado"] == "despachado"

        lote = client.get(
            f"/insumos/lotes?presentacion_id={self.presentacion_id}",
            headers=auth_headers,
        ).json()["items"]
        stock_bod = next(
            (float(l["cantidad_actual"]) for l in lote if l["id"] == self.lote_id), None
        )
        assert stock_bod == 80.0  # 90 ajustados - 10 despachados

        req_final = client.get(
            f"/insumos/requisiciones/{req['id']}", headers=auth_headers
        ).json()
        assert req_final["estado"] == "despachada"
        assert float(req_final["detalles"][0]["cantidad_despachada"]) == 10.0

    def test_04_despacho_stock_insuficiente(self, client, auth_headers):
        r = client.post(
            "/insumos/despachos",
            headers=auth_headers,
            json={
                "tipo": "servicio",
                "almacen_origen_id": self.bodega_id,
                "servicio_destino_id": self.servicio_id,
                "detalles": [{"lote_id": self.lote_id, "cantidad": 999999}],
            },
        )
        assert r.status_code == 400, f"{r.status_code}: {r.text}"

    def test_05_traslado_bodega_a_farmacia(self, client, auth_headers):
        r = client.post(
            "/insumos/despachos",
            headers=auth_headers,
            json={
                "tipo": "traslado",
                "almacen_origen_id": self.bodega_id,
                "almacen_destino_id": self.farmacia_id,
                "detalles": [{"lote_id": self.lote_id, "cantidad": 20}],
            },
        )
        assert r.status_code == 201, r.text
        desp_id = r.json()["id"]
        _reg["despachos"].append(desp_id)

        r2 = client.post(f"/insumos/despachos/{desp_id}/despachar", headers=auth_headers)
        assert r2.status_code == 200, r2.text

        lotes_far = client.get(
            f"/insumos/lotes?almacen_id={self.farmacia_id}&presentacion_id={self.presentacion_id}",
            headers=auth_headers,
        ).json()["items"]
        assert lotes_far, "El traslado debe crear el lote en farmacia"
        lote_far = lotes_far[0]
        _reg["lotes"].append(lote_far["id"])
        assert float(lote_far["cantidad_actual"]) == 20.0

        k = client.get(f"/insumos/kardex/lote/{lote_far['id']}", headers=auth_headers).json()
        assert k["items"][0]["tipo_movimiento"] == "entrada"

        # Origen quedó en 80 - 20 = 60
        lote_bod = next(
            l for l in client.get(
                f"/insumos/lotes?presentacion_id={self.presentacion_id}", headers=auth_headers
            ).json()["items"]
            if l["id"] == self.lote_id
        )
        assert float(lote_bod["cantidad_actual"]) == 60.0


# =====================================================================
# 3. ATENCIONES Y UNIDOSIS
# =====================================================================
class TestAtencionUnidosis:
    paciente_id = None

    @classmethod
    def _paciente(cls, client, auth_headers):
        if cls.paciente_id:
            return
        r = client.post(
            "/pacientes/",
            headers=auth_headers,
            json={
                "nombre": {
                    "primer_nombre": "Test",
                    "segundo_nombre": "Insumos",
                    "primer_apellido": "Paciente",
                    "segundo_apellido": _suf(),
                },
                "sexo": "F",
                "fecha_nacimiento": "2000-05-10",
            },
        )
        assert r.status_code == 201, r.text
        cls.paciente_id = r.json()["id"]
        _reg["pacientes"].append(cls.paciente_id)

    def test_01_atencion_consumo(self, client, auth_headers):
        self._paciente(client, auth_headers)
        r = client.post(
            "/insumos/atenciones",
            headers=auth_headers,
            json={"paciente_id": self.paciente_id, "observaciones": "Test atención"},
        )
        assert r.status_code == 201, r.text
        atencion_id = r.json()["id"]
        _reg["atenciones"].append(atencion_id)
        assert r.json()["estado"] == "abierta"

        lote_id = TestAlmacenFlujos.lote_id
        stock_antes = next(
            float(l["cantidad_actual"])
            for l in client.get(
                f"/insumos/lotes?presentacion_id={TestAlmacenFlujos.presentacion_id}",
                headers=auth_headers,
            ).json()["items"]
            if l["id"] == lote_id
        )

        r2 = client.post(
            f"/insumos/atenciones/{atencion_id}/insumos",
            headers=auth_headers,
            json={"lote_id": lote_id, "cantidad": 2, "origen": "directo"},
        )
        assert r2.status_code == 201, r2.text

        stock_despues = next(
            float(l["cantidad_actual"])
            for l in client.get(
                f"/insumos/lotes?presentacion_id={TestAlmacenFlujos.presentacion_id}",
                headers=auth_headers,
            ).json()["items"]
            if l["id"] == lote_id
        )
        assert stock_despues == stock_antes - 2

        k = client.get(f"/insumos/kardex/lote/{lote_id}", headers=auth_headers).json()
        assert k["items"][0]["tipo_movimiento"] == "consumo"

        r3 = client.post(
            f"/insumos/atenciones/{atencion_id}/finalizar", headers=auth_headers
        )
        assert r3.status_code == 200
        assert r3.json()["estado"] == "finalizada"

        # Consumo sobre atención finalizada → 400
        r4 = client.post(
            f"/insumos/atenciones/{atencion_id}/insumos",
            headers=auth_headers,
            json={"lote_id": lote_id, "cantidad": 1},
        )
        assert r4.status_code == 400

    def test_02_unidosis_preparar_y_cancelar(self, client, auth_headers):
        self._paciente(client, auth_headers)
        lote_id = TestAlmacenFlujos.lote_id

        def stock():
            return next(
                float(l["cantidad_actual"])
                for l in client.get(
                    f"/insumos/lotes?presentacion_id={TestAlmacenFlujos.presentacion_id}",
                    headers=auth_headers,
                ).json()["items"]
                if l["id"] == lote_id
            )

        antes = stock()
        r = client.post(
            "/insumos/unidosis",
            headers=auth_headers,
            json={
                "paciente_id": self.paciente_id,
                "almacen_origen_id": TestAlmacenFlujos.bodega_id,
                "detalles": [
                    {"lote_id": lote_id, "cantidad": 3, "dosis": "1 cada 8 horas"}
                ],
            },
        )
        assert r.status_code == 201, r.text
        uni_id = r.json()["id"]
        _reg["unidosis"].append(uni_id)
        assert r.json()["estado"] == "preparada"
        assert r.json()["numero"].startswith("UNI-")
        assert stock() == antes - 3

        r2 = client.post(f"/insumos/unidosis/{uni_id}/cancelar", headers=auth_headers)
        assert r2.status_code == 200, r2.text
        assert r2.json()["estado"] == "cancelada"
        assert stock() == antes  # devuelto a farmacia/bodega

        k = client.get(f"/insumos/kardex/lote/{lote_id}", headers=auth_headers).json()
        assert k["items"][0]["tipo_movimiento"] == "entrada"

    def test_03_unidosis_administrar(self, client, auth_headers):
        self._paciente(client, auth_headers)
        lote_id = TestAlmacenFlujos.lote_id
        r = client.post(
            "/insumos/unidosis",
            headers=auth_headers,
            json={
                "paciente_id": self.paciente_id,
                "almacen_origen_id": TestAlmacenFlujos.bodega_id,
                "detalles": [{"lote_id": lote_id, "cantidad": 1, "dosis": "única"}],
            },
        )
        assert r.status_code == 201, r.text
        uni_id = r.json()["id"]
        _reg["unidosis"].append(uni_id)

        r2 = client.post(f"/insumos/unidosis/{uni_id}/administrar", headers=auth_headers)
        assert r2.status_code == 200, r2.text
        assert r2.json()["estado"] == "administrada"

        # Cancelar ya administrada → 400
        r3 = client.post(f"/insumos/unidosis/{uni_id}/cancelar", headers=auth_headers)
        assert r3.status_code == 400
