from datetime import date

import pytest

from modules.common.vector_similarity import (
    CONFIANZA_ALTA,
    CONFIANZA_MEDIA,
    tokenizar,
    idf_por_token,
    mejor_candidato,
    coseno,
)


class TestVectorSimilarity:
    def test_tokenizar_normaliza_titulos_y_sinonimos(self):
        # Títulos y stopwords no son características discriminantes de identidad
        a = tokenizar("Dra. Ana María de la Cruz López")
        b = tokenizar("doctor ana maria cruz lopez")
        assert a == b
        assert a == ["ana", "maria", "cruz", "lopez"]
        assert "doctor" not in a
        assert "de" not in a and "la" not in a

    def test_tokenizar_ignora_stopwords_y_acentos(self):
        assert tokenizar("El Hospital Nacional") == ["nacional"]

    def test_idf_pondera_tokens_discriminantes(self):
        corpus = [tokenizar("Juan Perez"), tokenizar("Maria Lopez"), tokenizar("Rosa Lopez")]
        idf = idf_por_token(corpus)
        # 'juan' aparece en 1 documento (más discrim) que 'lopez' (en 2)
        assert idf.get("lopez", 0) < idf.get("juan", 0)

    def test_match_exacto_confianza_1(self):
        idf = idf_por_token([tokenizar("Ana Perez"), tokenizar("Juan Gomez")])
        r = mejor_candidato("Ana Pérez de la Cruz", ["Ana Perez Cruz", "Juan Gomez"])
        # 3 de 3 tokens → confianza alta (>=0.9), nunca certeza exacta aquí
        assert r is not None
        assert r["confianza"] >= CONFIANZA_ALTA
        assert r["nivel"] in ("similitud_alta", "exacto")

    def test_match_exacto_normalizado(self):
        r = mejor_candidato("Dra. Ana Maria Perez", ["Ana Maria Perez", "Juan Lopez"])
        assert r["confianza"] == 1.0
        assert r["nivel"] == "exacto"

    def test_sin_candidato_suficiente_devuelve_none(self):
        idf = idf_por_token([tokenizar("Rosa Maldonado"), tokenizar("Carlos Solis")])
        r = mejor_candidato("Pedro Altamirano", ["Rosa Maldonado", "Carlos Solis"], idf=idf)
        assert r is None

    def test_similitud_media_quedo_por_debajo_de_umbral_auto(self):
        base = ["Delfina Suchite Peralta", "Oscar Aguilar Mendez"]
        idf = idf_por_token([tokenizar(x) for x in base])
        r = mejor_candidato("Delvina Suchité Peralta", base, idf=idf, umbral=CONFIANZA_ALTA)
        # Inventado con una letra cambiada: vecinos cercanos pero no idénticos.
        assert r is None or r["confianza"] < CONFIANZA_ALTA

    def test_margen_minimo_bloquea_candidatos_ambiguos(self):
        r = mejor_candidato(
            "Ana Maria", ["Ana Maria Lopez", "Ana Maria Perez"],
            umbral=CONFIANZA_MEDIA, margen_minimo=0.08,
        )
        assert r is None

    def test_coseno_mayor_con_conjunto_completo_de_caracteristicas(self):
        import math
        from modules.common.vector_similarity import coseno
        a = {"juan": 1.0, "perez": 1.0, "lopez": 1.0}
        b = {"juan": 1.0, "perez": 1.0}
        c = {"roberto": 1.0, "gomez": 1.0}
        assert coseno(a, b) > coseno(a, c)


class TestResolverPersonalSaludVectorizado:
    def _mapa(self):
        return {
            "delfina suchite peralta": (1, 10, 20),
            "marta leticia choy": (2, 11, 21),
            "oswald miguel lopez": (3, 12, 22),
        }

    def test_directo_normalizado_es_exacto(self):
        from modules.sigsa3.service import _resolver_personal_salud_vectorizado, _idf_personal_salud
        mapa = self._mapa()
        idf = _idf_personal_salud(mapa)
        r = _resolver_personal_salud_vectorizado(mapa, idf, "Delfina M. Peralta", umbral_auto=CONFIANZA_ALTA)
        # tokens compartidos: delfina, peralta (2 de 3): similitud, sin certeza
        assert r is None or r.get("asociar") is False

    def test_exacto_por_clave_normalizada_asocia(self):
        from modules.sigsa3.service import _resolver_personal_salud_vectorizado, _idf_personal_salud
        mapa = {"delfina m. peralta": (1, "m1", 20)}
        r = _resolver_personal_salud_vectorizado(mapa, {}, "DELFINA M. PERALTA")
        assert r["asociar"] is True
        assert r["confianza"] == 1.0

    def test_sin_candidato_devuelve_none(self):
        from modules.sigsa3.service import _resolver_personal_salud_vectorizado, _idf_personal_salud
        mapa = self._mapa()
        idf = _idf_personal_salud(mapa)
        assert _resolver_personal_salud_vectorizado(mapa, idf, "zolti sebastian mo") is None


class TestAsociarPacientesPorNombreVectorial:
    def test_asocia_nombre_inequivoco(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "Dra. Ana María López", "sexo": "F"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "ANA MARIA LOPEZ", "sexo": "F"},
            {"pac_id": 2, "nombre_completo": "ANA MARIA PEREZ", "sexo": "F"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 1}
        assert rev == []

    def test_no_asocia_homonimos(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "Ana Maria Lopez", "sexo": "F"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "ANA MARIA LOPEZ", "sexo": "F"},
            {"pac_id": 2, "nombre_completo": "ANA MARIA LOPEZ", "sexo": "F"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {}
        assert len(rev) == 1
        assert rev[0]["tipo"] == "homonimo"

    def test_asocia_identidad_unica_pese_a_sexo_distinto(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "SALOME MORALES CUY", "sexo": "F"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "SALOME MORALES CUY", "sexo": "M"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 1}
        assert len(rev) == 1
        assert rev[0]["tipo"] == "sexo_discrepante"
        assert rev[0]["sexo_sigsa"] == "F"
        assert rev[0]["sexo_paciente"] == "M"

    def test_asocia_submatch_apellido_de_casada(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "ERIKA ALEJANDRA MELENDEZ DE LEON", "sexo": "F"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "ERIKA ALEJANDRA MELENDEZ DE LEON DE CABRERA", "sexo": "F"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 1}
        assert rev == []

    def test_rechaza_submatch_hijo_de_madre(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "LAURA CATALINA BALA SERECH", "sexo": "F"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "HIJO DE LAURA CATALINA BALA SERECH", "sexo": "M"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {}
        assert rev == []

    def test_homonimo_se_desambigua_por_sexo(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "MARIA DE LA CRUZ CHOGUAJ SOCOP", "sexo": "M"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "MARIA DE LA CRUZ CHOGUAJ SOCOP", "sexo": "M"},
            {"pac_id": 2, "nombre_completo": "MARIA DE LA CRUZ CHOGUAJ SOCOP", "sexo": "F"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 1}
        assert rev == []

    def test_homonimo_prefiere_al_vivo(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "BAUDILIO COJ ZAPETA", "sexo": "M"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "BAUDILIO COJ ZAPETA", "sexo": None, "estado": "I"},
            {"pac_id": 2, "nombre_completo": "BAUDILIO COJ ZAPETA", "sexo": "M", "estado": "V"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 2}
        assert rev == []

    def test_homonimo_sin_vivo_prefiere_fallecido(self):
        import pandas as pd
        from modules.sigsa3.service import _asociar_pacientes_por_nombre_vectorial

        sigsa = pd.DataFrame([
            {"id": 10, "paciente_id": None, "nombre_paciente": "BAUDILIO COJ ZAPETA", "sexo": "M"},
        ])
        pacientes = pd.DataFrame([
            {"pac_id": 1, "nombre_completo": "BAUDILIO COJ ZAPETA", "sexo": None, "estado": "I"},
            {"pac_id": 2, "nombre_completo": "BAUDILIO COJ ZAPETA", "sexo": "M", "estado": "F"},
        ])
        asoc, rev = _asociar_pacientes_por_nombre_vectorial(sigsa, pacientes)
        assert asoc == {10: 2}
        assert rev == []


class TestNacimientosEvidencia:
    def test_confianza_evidencias_completas(self):
        from modules.nacimientos.service import confianza_evidencias_neonatales, _computar
        neonatales = {"peso_nacimiento": "6 lb", "edad_gestacional": "39"}
        ev = confianza_evidencias_neonatales(neonatales, _computar(neonatales))
        assert ev["nivel"] == "alta"

    def test_confianza_evidencias_parcial(self):
        from modules.nacimientos.service import confianza_evidencias_neonatales, _computar
        ev = confianza_evidencias_neonatales({"peso_nacimiento": "6 lb"}, {})
        assert ev["nivel"] == "media"
        assert ev["trabajo_parto_evidence"] is False

    def test_trabajo_parto_necesita_eg(self):
        from modules.nacimientos.service import trabajo_parto
        assert trabajo_parto("39") == "a Termino"
        assert trabajo_parto(None) is None

    def test_peso_lb_onz(self):
        from modules.nacimientos.service import peso_lb_onz_a_gramos
        assert float(peso_lb_onz_a_gramos("7 lb 8 onz")) == pytest.approx(3409, abs=2)

    def test_madre_candidata_por_nombre(self):
        from modules.nacimientos.service import _madre_candidata_por_nombre
        madres = {5: {"id": 5, "nombre_completo": "Delfina Suchite Pérez"}, 
                  6: {"id": 6, "nombre_completo": "Rosa Choy López"}}
        r = _madre_candidata_por_nombre("Delfina Suchite Pérez", madres)
        assert r and r["madre_id"] == 5
        assert r["confianza"] == 1.0
        assert r["asociar"] is True


class TestEndpointSincronizarMedicoVectorial:
    def test_respuesta_incluye_analisis_voclu_vector(self, client, auth_headers):
        r = client.post("/sigsa3/sincronizar-medico-especialidad", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        # compat con el frontend: nuevas claves de análisis
        assert "personal_salud_sin_match" in data
        assert "personal_salud_baja_confianza" in data


class TestEndpointRecomputar:
    def test_recomputar_reporta_analisis_y_evidencia(self, client, auth_headers):
        r = client.post("/nacimientos/recomputar", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert "consistentes" in data
        assert "sin_evidencia" in data
        assert "analisis" in data
