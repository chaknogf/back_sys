from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union
from datetime import datetime


class DefuncionCreate(BaseModel):
    medico_id: Optional[int] = None
    fecha_defuncion: Optional[datetime] = None
    paciente_id: Optional[int] = None
    muerte_gestacion: Optional[str] = None
    causa_a: Optional[str] = None
    causa_b: Optional[str] = None
    causa_c: Optional[str] = None
    causa_d: Optional[str] = None
    causa_intervalo: Optional[str] = None
    causa_otros: Optional[str] = None
    fue_presunto: Optional[str] = None
    lugar_lesion: Optional[str] = None
    ocurrio_trabajo: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma: Optional[str] = None
    madre_id: Optional[int] = None
    es_fetal: Optional[bool] = False
    embarazos_previvos_vivos: Optional[int] = None
    embarazos_previvos_muertos: Optional[int] = None
    fetal_sexo: Optional[str] = None
    fetal_murio_antes_parto: Optional[bool] = None
    fetal_parto_tipo: Optional[str] = None
    fetal_clase_parto: Optional[str] = None
    fetal_via_parto: Optional[str] = None
    fetal_semanas_gestacion: Optional[int] = None
    fetal_causas_fetales: Optional[str] = None
    fetal_causas_maternas: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None


class DefuncionUpdate(BaseModel):
    medico_id: Optional[int] = None
    fecha_defuncion: Optional[datetime] = None
    paciente_id: Optional[int] = None
    muerte_gestacion: Optional[str] = None
    causa_a: Optional[str] = None
    causa_b: Optional[str] = None
    causa_c: Optional[str] = None
    causa_d: Optional[str] = None
    causa_intervalo: Optional[str] = None
    causa_otros: Optional[str] = None
    fue_presunto: Optional[str] = None
    lugar_lesion: Optional[str] = None
    ocurrio_trabajo: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma: Optional[str] = None
    madre_id: Optional[int] = None
    es_fetal: Optional[bool] = None
    embarazos_previvos_vivos: Optional[int] = None
    embarazos_previvos_muertos: Optional[int] = None
    fetal_sexo: Optional[str] = None
    fetal_murio_antes_parto: Optional[bool] = None
    fetal_parto_tipo: Optional[str] = None
    fetal_clase_parto: Optional[str] = None
    fetal_via_parto: Optional[str] = None
    fetal_semanas_gestacion: Optional[int] = None
    fetal_causas_fetales: Optional[str] = None
    fetal_causas_maternas: Optional[str] = None
    observaciones: Optional[str] = None


class PacienteResumen(BaseModel):
    id: int
    expediente: Optional[str] = None
    cui: Optional[Union[str, int]] = None
    nombre_completo: Optional[str] = None
    nombre: Optional[dict] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    estado: Optional[str] = None
    cui_formateado: Optional[str] = None
    defuncion: Optional[str] = None

    @field_validator("cui", mode="before")
    @classmethod
    def coerce_cui(cls, v):
        if isinstance(v, int):
            return str(v)
        return v


class MedicoResumen(BaseModel):
    id: int
    nombre: Optional[str] = None
    colegiado: Optional[int] = None
    especialidad: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DefuncionOut(BaseModel):
    id: int
    medico_id: Optional[int] = None
    fecha_defuncion: Optional[datetime] = None
    paciente_id: Optional[int] = None
    fallecido_edad_horas: Optional[int] = None
    fallecido_edad_dias: Optional[int] = None
    fallecido_edad_meses: Optional[int] = None
    fallecido_edad_anios: Optional[int] = None
    mujer_edad_fertil: bool = False
    muerte_gestacion: Optional[str] = None
    causa_a: Optional[str] = None
    causa_b: Optional[str] = None
    causa_c: Optional[str] = None
    causa_d: Optional[str] = None
    causa_intervalo: Optional[str] = None
    causa_otros: Optional[str] = None
    fue_presunto: Optional[str] = None
    lugar_lesion: Optional[str] = None
    ocurrio_trabajo: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma: Optional[str] = None
    madre_id: Optional[int] = None
    madre_edad: Optional[int] = None
    madre_sabe_leer_escribir: Optional[str] = None
    es_fetal: bool = False
    embarazos_previvos_vivos: Optional[int] = None
    embarazos_previvos_muertos: Optional[int] = None
    fetal_sexo: Optional[str] = None
    fetal_murio_antes_parto: Optional[bool] = None
    fetal_parto_tipo: Optional[str] = None
    fetal_clase_parto: Optional[str] = None
    fetal_via_parto: Optional[str] = None
    fetal_semanas_gestacion: Optional[int] = None
    fetal_causas_fetales: Optional[str] = None
    fetal_causas_maternas: Optional[str] = None
    registrador_id: Optional[int] = None
    observaciones: Optional[str] = None
    estado: str = "A"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    paciente: Optional[PacienteResumen] = None
    madre: Optional[PacienteResumen] = None
    medico: Optional[MedicoResumen] = None

    model_config = ConfigDict(from_attributes=True)


class DefuncionListResponse(BaseModel):
    total: int
    defunciones: list[DefuncionOut]

    model_config = ConfigDict(from_attributes=True)


class DefuncionResumen(BaseModel):
    id: Optional[int] = None
    fecha_defuncion: Optional[datetime] = None
    medico_id: Optional[int] = None
    causa_a: Optional[str] = None
    causa_b: Optional[str] = None
    causa_c: Optional[str] = None
    causa_d: Optional[str] = None
    edad_anios: Optional[int] = None
    muerte_gestacion: Optional[str] = None
    es_fetal: Optional[bool] = None
    mujer_edad_fertil: Optional[bool] = None
    lugar_lesion: Optional[str] = None
    fue_presunto: Optional[str] = None


class PacienteFallecidoOut(BaseModel):
    id: int
    expediente: Optional[str] = None
    cui: Optional[str] = None
    nombre_completo: Optional[str] = None
    nombre: Optional[dict] = None
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    estado: Optional[str] = None
    defuncion: Optional[DefuncionResumen] = None

    model_config = ConfigDict(from_attributes=True)


class PacientesFallecidosResponse(BaseModel):
    total: int
    pacientes: list[PacienteFallecidoOut]

    model_config = ConfigDict(from_attributes=True)


class RegistrarDefuncionRequest(BaseModel):
    medico_id: Optional[int] = None
    fecha_defuncion: Optional[datetime] = None
    muerte_gestacion: Optional[str] = None
    causa_a: Optional[str] = None
    causa_b: Optional[str] = None
    causa_c: Optional[str] = None
    causa_d: Optional[str] = None
    causa_intervalo: Optional[str] = None
    causa_otros: Optional[str] = None
    fue_presunto: Optional[str] = None
    lugar_lesion: Optional[str] = None
    ocurrio_trabajo: Optional[bool] = None
    accidente_transito: Optional[bool] = None
    arma: Optional[str] = None
    madre_id: Optional[int] = None
    es_fetal: Optional[bool] = False
    embarazos_previvos_vivos: Optional[int] = None
    embarazos_previvos_muertos: Optional[int] = None
    fetal_sexo: Optional[str] = None
    fetal_murio_antes_parto: Optional[bool] = None
    fetal_parto_tipo: Optional[str] = None
    fetal_clase_parto: Optional[str] = None
    fetal_via_parto: Optional[str] = None
    fetal_semanas_gestacion: Optional[int] = None
    fetal_causas_fetales: Optional[str] = None
    fetal_causas_maternas: Optional[str] = None
    observaciones: Optional[str] = None
