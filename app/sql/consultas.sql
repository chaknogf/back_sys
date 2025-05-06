CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,

    paciente_id INTEGER REFERENCES pacientes(id) NOT NULL,
    tipo_consulta INTEGER,
    especialidad INTEGER,
    servicio INTEGER,
    documento VARCHAR(20),
    fecha_consulta DATE,
    hora_consulta TIME,
    ciclo JSONB, -- { 
              --   "activo": "2025-05-06T10:00:00", 
              --   "egreso": "2025-05-06T15:00:00", 
              --   "archivado": "2025-05-07T08:00:00", 
              --   "prestamo": "2025-05-07T10:30:00", 
              --   "reactivado": "2025-05-08T09:00:00"
              -- }

    indicadores JSONB, -- {"prenatal": 4, "lactancia": true, "bomberos": true, "arma_blanca": false, ...}
    detalle_clinico JSONB, -- {"medico": "Dr. Juan", "diagnostico": "Cancer", "tratamiento": "Quimioterapia", ...}
    sistema JSONB, -- {"usuario_creador": "Dr. Juan", "usuario_modificador": "Dr. Juan", ...}
    signos_vitales JSONB, -- {"temperatura": 36.5, "presion_arterial": "120/80", "frecuencia_cardiaca": 60, ...}
    ansigmas JSONB, -- {"sintomas": ["dolor de cabeza", "nauseas", "diarrea"], "examen_fisico": "Normal", ...}
    antecedentes JSONB, -- {"alergias": ["penicilina", "antibiotico"], "enfermedades": ["diabetes", "hipertension"], ...}
    ordenes JSONB, -- {"medicamentos": ["paracetamol", "ibuprofeno"], "examen_fisico": "Normal", ...}
    
    -- 🧾 Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);