"""Catálogo de entidades/dimensiones para el agente estadístico.

Define, por cada tabla del hospital, las columnas reales que el intérprete
puede usar, sus joins, la dimensión de fecha y los sinónimos en lenguaje
natural. Nada que diga el usuario se inyecta directo en SQL: solo se resuelven
identificadores de este catálogo y los valores van como parámetros ligados.
"""

TIPO_CONSULTA_MAPA = {1: "COEX", 2: "Hospitalizacion", 3: "Emergencia"}
TIPO_CONSULTA_POR_NOMBRE = {
    "externa": 1, "coex": 1, "ambulatoria": 1, "consultas externas": 1,
    "hospitalizacion": 2, "hospitalaria": 2, "ingresos": 2, "internos": 2,
    "emergencia": 3, "emergencias": 3, "urgencias": 3,
}

ENTIDADES = {
    "pacientes": {
        "tabla": "pacientes p",
        "sinonimos": [
            "paciente", "pacientes", "persona", "personas", "expediente",
            "expedientes", "usuarios", "usuario",
        ],
        "fecha_col": "p.creado_en",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "estado": ("CASE WHEN COALESCE(p.estado,'V')='V' THEN 'Vivo' "
                       "WHEN p.estado='F' THEN 'Fallecido' ELSE 'Inactivo' END",
                       "estado"),
            "dia": ("DATE(p.creado_en)", "dia"),
            "mes": ("TO_CHAR(p.creado_en,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM p.creado_en)::int", "anio"),
            "municipio": ("COALESCE(p.lugar_nacimiento,'S/D')", "municipio"),
        },
        "medidas": {
            "edad": "EXTRACT(YEAR FROM age(p.fecha_nacimiento))",
        },
        "alias_sql": {"sexo": "p.sexo",
                      "estado": "COALESCE(p.estado,'V')"},
    },
    "consultas": {
        "tabla": "consultas c",
        "sinonimos": [
            "consulta", "consultas", "atencion", "atenciones",
            "cita medica", "citas medicas", "registro de consultas",
        ],
        "fecha_col": "c.fecha_consulta",
        "join_paciente": "LEFT JOIN pacientes p ON p.id = c.paciente_id",
        "join_especialidad": "LEFT JOIN especialidades e ON e.id = c.especialidad_id",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "tipo_consulta": ("c.tipo_consulta::int", "tipo_consulta"),
            "especialidad": ("COALESCE(e.nombre,c.especialidad,'S/D')", "especialidad"),
            "servicio": ("COALESCE(c.servicio,'S/D')", "servicio"),
            "dia": ("DATE(c.fecha_consulta)", "dia"),
            "mes": ("TO_CHAR(c.fecha_consulta,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM c.fecha_consulta)::int", "anio"),
        },
    },
    "citas": {
        "tabla": "citas ci",
        "sinonimos": ["cita", "citas", "citas programadas", "agenda"],
        "fecha_col": "ci.fecha_cita",
        "join_paciente": "LEFT JOIN pacientes p ON p.id = ci.paciente_id",
        "join_especialidad": "LEFT JOIN especialidades e ON e.id = ci.especialidad_id",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "especialidad": ("COALESCE(e.nombre,ci.especialidad,'S/D')", "especialidad"),
            "dia": ("DATE(ci.fecha_cita)", "dia"),
            "mes": ("TO_CHAR(ci.fecha_cita,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM ci.fecha_cita)::int", "anio"),
        },
    },
    "medicos": {
        "tabla": "medicos m",
        "sinonimos": ["medico", "medicos", "doctor", "doctores", "galeno"],
        "fecha_col": None,
        "join_especialidad": "LEFT JOIN especialidades e ON e.id = m.especialidad_id",
        "agrupaciones": {
            "especialidad": ("COALESCE(e.nombre,'S/D')", "especialidad"),
            "estado": ("CASE WHEN m.activo THEN 'Activo' ELSE 'Inactivo' END", "estado"),
            "sexo": ("COALESCE(m.sexo,'S/D')", "sexo"),
        },
    },
    "nacimientos": {
        "tabla": "nacimientos n",
        "sinonimos": ["nacimiento", "nacimientos", "nacidos", "partos"],
        "fecha_col": "n.created_at",
        "join_paciente": "LEFT JOIN pacientes p ON p.id = n.paciente_id",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "clasificacion": ("COALESCE(n.clasificacion_nacimiento,'S/D')", "clasificacion"),
            "trabajo_parto": ("COALESCE(n.trabajo_parto,'S/D')", "trabajo_parto"),
            "mes": ("TO_CHAR(n.created_at,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM n.created_at)::int", "anio"),
            "dia": ("DATE(n.created_at)", "dia"),
        },
    },
    "defunciones": {
        "tabla": "defunciones d",
        "sinonimos": ["defuncion", "defunciones", "muerte", "muertes",
                      "fallecidos", "fallecimiento"],
        "fecha_col": "d.fecha_defuncion",
        "join_paciente": "LEFT JOIN pacientes p ON p.id = d.paciente_id",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "fetal": ("CASE WHEN d.es_fetal THEN 'Fetal' ELSE 'No fetal' END", "fetal"),
            "mes": ("TO_CHAR(d.fecha_defuncion,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM d.fecha_defuncion)::int", "anio"),
            "dia": ("DATE(d.fecha_defuncion)", "dia"),
        },
    },
    "censo_camas": {
        "tabla": "censo_camas cc",
        "sinonimos": ["censo", "censo camas", "camas", "ocupacion de camas"],
        "fecha_col": "cc.fecha",
        "join_servicio": "LEFT JOIN encamamiento s ON s.id = cc.servicio_id",
        "agrupaciones": {
            "servicio": ("COALESCE(s.nombre_servicio,'S/D')", "servicio"),
            "sexo": ("COALESCE(cc.sexo,'S/D')", "sexo"),
            "dia": ("DATE(cc.fecha)", "dia"),
        },
        "medidas": {
            "cantidad": "COALESCE(cc.ocupados,0)",
            "ocupados": "COALESCE(cc.ocupados,0)",
            "egresos": "COALESCE(cc.egresos,0)",
            "ingresos": "COALESCE(cc.ingresos,0)",
        },
    },
    "prestamos": {
        "tabla": "prestamos pr",
        "sinonimos": ["prestamo", "prestamos", "expediente prestado",
                      "prestamo de expediente"],
        "fecha_col": "pr.fecha_prestamo",
        "agrupaciones": {
            "tipo_documento": ("COALESCE(pr.tipo_documento,'EXPEDIENTE')",
                               "tipo_documento"),
            "estado": ("CASE WHEN pr.activo THEN 'Activo' ELSE 'Inactivo' END",
                       "estado"),
            "dia": ("DATE(pr.fecha_prestamo)", "dia"),
            "mes": ("TO_CHAR(pr.fecha_prestamo,'YYYY-MM')", "mes"),
        },
    },
    "proce_medicos": {
        "tabla": "proce_medicos pm",
        "sinonimos": ["procedimiento", "procedimientos",
                      "procedimientos realizados", "proce"],
        "fecha_col": "pm.fecha",
        "join_procedimiento": "LEFT JOIN procedimientos pr ON pr.id = pm.id_procedimiento",
        "join_especialidad": "LEFT JOIN especialidades e ON e.id = pm.especialidad_id",
        "agrupaciones": {
            "procedimiento": ("COALESCE(pr.nombre,pm.id_procedimiento::text)",
                              "procedimiento"),
            "especialidad": ("COALESCE(e.nombre,'S/D')", "especialidad"),
            "sexo": ("COALESCE(pm.sexo,'S/D')", "sexo"),
            "dia": ("DATE(pm.fecha)", "dia"),
            "mes": ("TO_CHAR(pm.fecha,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM pm.fecha)::int", "anio"),
        },
        "medidas": {"cantidad": "COALESCE(pm.cantidad,0)"},
    },
    "sigsa3": {
        "tabla": "sigsa3 sg",
        "sinonimos": ["sigsa3", "sigsa", "consulta sigsa", "registros sigsa"],
        "fecha_col": "sg.fecha_consulta",
        "join_especialidad": "LEFT JOIN especialidades e ON e.id = sg.especialidad_id",
        "agrupaciones": {
            "sexo": ("COALESCE(sg.sexo,'S/D')", "sexo"),
            "especialidad": ("COALESCE(e.nombre,'S/D')", "especialidad"),
            "tipo_consulta": ("COALESCE(sg.tipo_consulta,'S/D')", "tipo_consulta"),
            "diagnostico": ("COALESCE(sg.dx, sg.codigo_cie_10, 'S/D')", "diagnostico"),
            "dia": ("DATE(sg.fecha_consulta)", "dia"),
            "mes": ("TO_CHAR(sg.fecha_consulta,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM sg.fecha_consulta)::int", "anio"),
        },
    },
    "constancia_nacimiento": {
        "tabla": "constancia_nacimiento cn",
        "sinonimos": ["constancia de nacimiento", "constancia", "constancias",
                      "certificado de nacimiento", "partida de nacimiento"],
        "fecha_col": "cn.fecha_registro",
        "join_paciente": "LEFT JOIN pacientes p ON p.id = cn.paciente_id",
        "agrupaciones": {
            "sexo": ("COALESCE(p.sexo,'S/D')", "sexo"),
            "dia": ("DATE(cn.fecha_registro)", "dia"),
            "mes": ("TO_CHAR(cn.fecha_registro,'YYYY-MM')", "mes"),
            "anio": ("EXTRACT(YEAR FROM cn.fecha_registro)::int", "anio"),
        },
    },
}