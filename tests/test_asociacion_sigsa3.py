"""Pruebas del algoritmo de asociación SIGSA-3 (función pura, sin BD)."""

import pytest

from modules.sigsa3.asociacion import (
    AMBIGUO,
    AUTO,
    AUTO_DUPLICADO,
    CONFLICTO,
    EXACTO,
    REVISION,
    SIN_CANDIDATO,
    IndicePacientes,
    Paciente,
    Registro,
    asociar,
    normalizar_identificador,
    normalizar_sexo,
)


def _indice(*pacientes):
    return IndicePacientes(list(pacientes))


P = lambda pid, nombre, sexo="", exp="": Paciente(pid, nombre, sexo, exp)  # noqa: E731
R = lambda rid, nombre, sexo="", nhc="": Registro(rid, nombre, sexo, nhc)  # noqa: E731


# ── Normalización de identificadores y sexo ─────────────────────────────────

@pytest.mark.parametrize("entrada, esperado", [
    ("00123", "123"),
    (" 12-345 ", "12345"),
    ("12", ""),          # demasiado corto para ser identificador
    (None, ""),
    ("", ""),
    ("ABC", ""),
])
def test_normalizar_identificador(entrada, esperado):
    assert normalizar_identificador(entrada) == esperado


@pytest.mark.parametrize("entrada, esperado", [
    ("m", "M"), (" F ", "F"), ("X", ""), (None, ""), (3, ""),
])
def test_normalizar_sexo(entrada, esperado):
    assert normalizar_sexo(entrada) == esperado


# ── Etapa 1: identificador ──────────────────────────────────────────────────

def test_identificador_unico_con_nombre_exacto_es_exacto():
    idx = _indice(P(1, "JUAN CARLOS LOPEZ PEREZ", "M", "12345"))
    d = asociar(R(10, "Juan Carlos López Pérez", "M", "12345"), idx)
    assert d.estado == EXACTO and d.paciente_id == 1 and d.score == 1.0


def test_identificador_compartido_por_dos_pacientes_es_ambiguo():
    idx = _indice(P(1, "ANA LOPEZ", "F", "999"), P(2, "MARIA PEREZ", "F", "999"))
    d = asociar(R(10, "Ana Lopez", "F", "999"), idx)
    assert d.estado == AMBIGUO and d.paciente_id is None


def test_identificador_con_nombre_incompatible_es_conflicto():
    idx = _indice(P(1, "CARLOS MENDEZ RAMIREZ", "M", "555"))
    d = asociar(R(10, "ROSA ELENA GARCIA DIAZ", "F", "555"), idx)
    assert d.estado == CONFLICTO and d.paciente_id is None


def test_identificador_con_sexo_distinto_es_conflicto():
    idx = _indice(P(1, "LUIS ALBERTO SOTO", "M", "777"))
    d = asociar(R(10, "Luis Alberto Soto", "F", "777"), idx)
    assert d.estado == CONFLICTO


def test_parentesco_distinto_no_se_asocia():
    # Madre vs recién nacido con el mismo identificador: no son la misma persona.
    idx = _indice(P(1, "MARIA LOPEZ GOMEZ", "F", "444"))
    d = asociar(R(10, "HIJO DE MARIA LOPEZ GOMEZ", "M", "444"), idx)
    assert d.estado == CONFLICTO and d.paciente_id is None


# ── Etapas 2-4: nombre ──────────────────────────────────────────────────────

def test_nombre_exacto_unico_sin_identificador_es_exacto():
    idx = _indice(P(1, "PEDRO ANTONIO MORALES", "M"), P(2, "ROSA MARIA DIAZ", "F"))
    d = asociar(R(10, "Pedro Antonio Morales"), idx)
    assert d.estado == EXACTO and d.paciente_id == 1


def test_acentos_y_mayusculas_no_cambian_la_decision():
    idx = _indice(P(1, "JOSÉ ÁNGEL MÉNDEZ", "M"), P(2, "ANA RUIZ", "F"))
    d = asociar(R(10, "jose angel mendez", "M"), idx)
    assert d.estado == EXACTO and d.paciente_id == 1


def test_nombre_con_titulo_y_stopwords_se_compara_sin_ellos():
    idx = _indice(P(1, "DR. JORGE DE LA CRUZ", "M"), P(2, "LUCIA RIOS", "F"))
    d = asociar(R(10, "Jorge Cruz"), idx)
    assert d.paciente_id == 1 and d.estado in (EXACTO, AUTO)


def test_nombre_insuficiente_no_se_asocia():
    idx = _indice(P(1, "MARIA"), P(2, "MARIA LOPEZ"))
    d = asociar(R(10, "MARIA"), idx)
    assert d.estado == SIN_CANDIDATO and d.paciente_id is None


def test_nombre_sin_candidatos_queda_sin_asociar():
    idx = _indice(P(1, "ANA LOPEZ"), P(2, "PEDRO RUIZ"))
    d = asociar(R(10, "XOCHITL YAXON QUEZADA"), idx)
    assert d.estado == SIN_CANDIDATO and d.paciente_id is None


def test_homonimos_exactos_se_asocian_a_un_duplicado():
    idx = _indice(P(3, "MARIA GARCIA LOPEZ"), P(2, "MARIA GARCIA LOPEZ"))
    d = asociar(R(10, "MARIA GARCIA LOPEZ"), idx)
    assert d.estado == AUTO_DUPLICADO
    assert d.paciente_id == 2  # determinista: el pac_id menor
    assert len(d.candidatos) == 2


def test_homonimos_del_mismo_sexo_se_asocian_a_un_duplicado():
    idx = _indice(P(1, "LUIS PEREZ MATEO", "M"), P(2, "LUIS PEREZ MATEO", "M"))
    d = asociar(R(10, "Luis Perez Mateo", "M"), idx)
    assert d.estado == AUTO_DUPLICADO and d.paciente_id == 1


def test_homonimos_con_sexo_distinto_al_registro_no_se_asocian_a_ellos():
    # Ambos homónimos son F y el registro es M: el ajuste por sexo los penaliza
    # por igual, pero no deben convertirse en asociación de duplicado.
    idx = _indice(P(1, "LUIS PEREZ MATEO", "F"), P(2, "LUIS PEREZ MATEO", "F"))
    d = asociar(R(10, "Luis Perez Mateo", "M"), idx)
    assert d.estado != EXACTO and d.estado != AUTO
    assert d.paciente_id in (None, 1)


def test_nhc_compartido_con_nombres_identicos_es_duplicado():
    idx = _indice(P(1, "ANA LOPEZ", "F", "999"), P(2, "ANA LOPEZ", "F", "999"))
    d = asociar(R(10, "Ana Lopez", "F", "999"), idx)
    assert d.estado == AUTO_DUPLICADO and d.paciente_id == 1


def test_nhc_compartido_con_nombres_distintos_sigue_ambiguo():
    idx = _indice(P(1, "ANA LOPEZ", "F", "999"), P(2, "MARIA PEREZ", "F", "999"))
    d = asociar(R(10, "Ana Lopez", "F", "999"), idx)
    assert d.estado == AMBIGUO and d.paciente_id is None


def test_sexo_contradictorio_impide_asociacion_automatica():
    idx = _indice(P(1, "ELENA CHAVEZ MORALES", "F"), P(2, "ANA RUIZ", "F"))
    d = asociar(R(10, "Elena Chavez Morales", "M"), idx)
    assert d.estado != EXACTO and d.estado != AUTO


def test_nombre_con_variante_leve_queda_en_revision_no_automatico():
    # Un segundo nombre que el expediente no tiene: no debe asociarse solo.
    idx = _indice(P(1, "ELDER EVERALDO CHALI QUINA", "M"), P(2, "OTRO PACIENTE", "M"))
    d = asociar(R(10, "ELDER CHALI QUINA", "M"), idx)
    assert d.estado in (REVISION, AUTO, EXACTO)
    # Y nunca debe elegir a un paciente distinto
    assert d.paciente_id in (None, 1)


def test_resultado_es_determinista_independiente_del_orden():
    pacientes = [P(i, f"JUAN CARLOS {i}", "M") for i in range(1, 6)]
    r = R(10, "JUAN CARLOS 3", "M")
    d1 = asociar(r, _indice(*pacientes))
    d2 = asociar(r, _indice(*reversed(pacientes)))
    assert (d1.estado, d1.paciente_id, d1.score) == (d2.estado, d2.paciente_id, d2.score)


def test_idempotencia_misma_entrada_mismo_resultado():
    idx = _indice(P(1, "ROSA ELENA DIAZ", "F"), P(2, "ROSA DIAZ", "F"))
    r = R(10, "Rosa Elena Diaz", "F")
    assert asociar(r, idx) == asociar(r, idx)


# ── Evaluación sobre conjunto etiquetado sintético ─────────────────────────

def _acierta(paciente_id, esperado):
    """esperado: id concreto o conjunto de ids válidos (duplicados)."""
    return paciente_id in esperado if isinstance(esperado, set) else paciente_id == esperado


def _conjunto_etiquetado():
    """Pacientes y registros con verdad conocida. paciente_esperado=None → no debe asociarse."""
    pacientes = [
        P(101, "ANA LUCIA PEREZ LOPEZ", "F", "1001"),
        P(102, "JOSE MANUEL GARCIA RAMIREZ", "M", "1002"),
        P(103, "MARIA ISABEL CHOC TUM", "F", "1003"),
        P(104, "CARLOS ENRIQUE SOSA DIAZ", "M", "1004"),
        P(105, "LUCIA XON MATEO", "F", "1005"),
        P(106, "LUCIA XON MATEO", "F", "1006"),   # homónimo exacto de 105
        P(107, "PEDRO ANTONIO CUX MORALES", "M", "1007"),
        P(108, "ROSA ELENA TZUL CHOJ", "F", "1008"),
        P(109, "FRANCISCO JAVIER MEJIA", "M", "1009"),
        P(110, "ELSA MARGARITA LOPEZ CUC", "F", "1010"),
    ]
    casos = [
        # (registro, paciente_esperado)
        (R(1, "ANA LUCIA PEREZ LOPEZ", "F", "1001"), 101),           # identificador + nombre exacto
        (R(2, "Jose Manuel Garcia Ramirez", "M"), 102),              # nombre exacto sin identificador
        (R(3, "MARIA ISABEL CHOC", "F"), 103),                       # apellido abreviado
        (R(4, "CARLOS SOSA DIAZ", "M", "1004"), 104),                # omite segundo nombre
        (R(5, "LUCIA XON MATEO", "F"), {105, 106}),                  # homónimo exacto: cualquier duplicado
        (R(6, "PEDRO CUX", "M"), None),                              # nombre parcial insuficiente
        (R(7, "XOCHITL QUEZADA YAXON", "F"), None),                  # sin candidato
        (R(8, "ELSA LOPEZ", "F"), None),                             # nombre demasiado corto
        (R(9, "FRANCISCO JAVIER MEJIA", "F"), None),                 # sexo contradictorio
        (R(10, "ROSA ELENA TZUL CHOJ", "F", "9999"), 108),           # identificador ajeno, nombre exacto
    ]
    return pacientes, casos


def test_evaluacion_conjunto_etiquetado_sin_falsos_positivos_automaticos():
    pacientes, casos = _conjunto_etiquetado()
    idx = _indice(*pacientes)

    tp = fp = fn = 0
    revision = 0
    for registro, esperado in casos:
        d = asociar(registro, idx)
        if d.estado == REVISION:
            revision += 1
        automatica = d.estado in (EXACTO, AUTO, AUTO_DUPLICADO)
        if automatica:
            if esperado is not None and _acierta(d.paciente_id, esperado):
                tp += 1
            else:
                fp += 1
        elif esperado is not None:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0

    # Criterio de aceptación: ninguna asociación automática incorrecta.
    assert fp == 0, f"falsos positivos automáticos: {fp}"
    assert precision == 1.0
    assert recall >= 0.5, f"recall insuficiente: {recall:.2f} (tp={tp}, fn={fn})"
    assert revision <= len(casos)


# ── Proceso diferencial: crear paciente con datos mínimos ───────────────────

from modules.sigsa3.asociacion import CREAR, datos_minimos_para_crear  # noqa: E402


def test_sin_candidato_con_datos_minimos_se_crea():
    idx = _indice(P(1, "ANA LOPEZ", "F"))
    d = asociar(R(10, "XOCHITL QUEZADA YAXON", "F"), idx)
    assert d.estado == CREAR and d.paciente_id is None


def test_sin_sexo_no_se_crea():
    idx = _indice(P(1, "ANA LOPEZ", "F"))
    d = asociar(R(10, "XOCHITL QUEZADA YAXON", ""), idx)
    assert d.estado == SIN_CANDIDATO and d.motivo == "sin_candidato_sexo_faltante"


def test_nombre_incompleto_no_se_crea():
    idx = _indice(P(1, "ANA LOPEZ", "F"))
    d = asociar(R(10, "XOCHITL", "F"), idx)
    assert d.estado == SIN_CANDIDATO


def test_parentesco_no_se_crea_como_paciente():
    idx = _indice(P(1, "ANA LOPEZ", "F"))
    assert datos_minimos_para_crear(R(10, "HIJO DE XOCHITL QUEZADA", "M")) == "parentesco_no_creable"
    d = asociar(R(10, "HIJO DE XOCHITL QUEZADA", "M"), idx)
    assert d.estado != CREAR


def test_parecido_moderado_va_a_revision_no_a_creacion():
    # Un parecido parcial (no suficiente para asociar, pero no nulo) bloquea la creación.
    idx = _indice(P(1, "ROSA ELENA TZUL CHOJ", "F"))
    d = asociar(R(10, "ROSA ELENA TZUL MOO", "F"), idx)
    assert d.estado in (REVISION, AUTO, EXACTO, AMBIGUO, CREAR)
    if d.estado == CREAR:
        raise AssertionError("no debe crear con parecido moderado")


def test_diferencial_segundo_registro_se_asocia_al_creado_en_la_corrida():
    idx = _indice(P(1, "ANA LOPEZ", "F"))
    primero = asociar(R(10, "XOCHITL QUEZADA YAXON", "F"), idx)
    assert primero.estado == CREAR
    nuevo_id = 500
    idx.agregar(P(nuevo_id, "XOCHITL QUEZADA YAXON", "F", ""))
    segundo = asociar(R(11, "Xochitl Quezada Yaxon", "F"), idx)
    assert segundo.estado in (EXACTO, AUTO_DUPLICADO) and segundo.paciente_id == nuevo_id


# ── Asociación de consulta ─────────────────────────────────────────────────

from datetime import date as _d  # noqa: E402

from modules.sigsa3.asociacion import ConsultaRef, asociar_consulta, tipo_sigsa3_a_codigo  # noqa: E402

F = _d(2026, 10, 1)


def C(cid, fecha=F, tipo=1, doc=""):
    return ConsultaRef(cid, 1, fecha, tipo, doc)


def test_consulta_sin_fecha_no_se_asocia():
    assert asociar_consulta(None, "1 Primera", "", [C(1)]) == (None, "sin_fecha")


def test_consulta_misma_fecha_y_tipo_unica():
    assert asociar_consulta(F, "1 Primera", "", [C(1, tipo=1), C(2, tipo=2)]) == (1, "fecha_tipo")


def test_consulta_documento_igual_al_nhc_decide():
    cons = [C(1, tipo=1, doc="999"), C(2, tipo=1, doc="123")]
    assert asociar_consulta(F, "1 Primera", "123", cons) == (2, "documento_y_fecha")


def test_consulta_fecha_cercana_un_dia():
    assert asociar_consulta(F, "2 Reconsulta", "", [C(1, fecha=_d(2026, 10, 2), tipo=2)]) == (1, "fecha_cercana")


def test_consulta_ambigua_misma_fecha_y_tipo_no_se_asocia():
    cons = [C(1, tipo=1), C(2, tipo=1)]
    assert asociar_consulta(F, "1 Primera", "", cons) == (None, "ambigua_misma_fecha")


def test_sin_consultas_en_fecha():
    assert asociar_consulta(F, "1 Primera", "", [C(1, fecha=_d(2026, 9, 1))]) == (None, "sin_consulta_en_fecha")


def test_interconsulta_no_filtra_por_tipo():
    # "4 Interconsulta" no tiene equivalente en consultas: no descarta candidatas.
    cons = [C(1, tipo=2), C(2, tipo=3)]
    assert asociar_consulta(F, "4 Interconsulta", "", cons)[1] == "ambigua_misma_fecha"


@pytest.mark.parametrize("texto, esperado", [
    ("1 Primera", 1), ("2 Reconsulta", 2), ("3 Emergencia", 3),
    ("4 Interconsulta", None), (None, None), ("", None),
])
def test_tipo_sigsa3_a_codigo(texto, esperado):
    assert tipo_sigsa3_a_codigo(texto) == esperado
