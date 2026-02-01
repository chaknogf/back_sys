from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.db import get_db
from app.models.pacientes import PacienteModel
from app.database.security import get_current_user
from app.models.user import UserModel

router = APIRouter(
    prefix="/pacientes",
    tags=["duplicados"]
)


@router.get("/duplicados/personaid")
def pacientes_duplicados_por_personaid(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    subquery = (
        db.query(
            PacienteModel.datos_extra["personaid"].astext.label("personaid"),
            func.count().label("total_registros")
        )
        .filter(
            PacienteModel.datos_extra.has_key("personaid"),  # noqa
            PacienteModel.estado != "I"
        )
        .group_by(PacienteModel.datos_extra["personaid"].astext)
        .having(func.count() > 1)
        .subquery()
    )

    query = (
        db.query(
            PacienteModel.id,
            PacienteModel.nombre,
            PacienteModel.expediente,
            PacienteModel.datos_extra["personaid"].astext.label("personaid"),
            subquery.c.total_registros
        )
        .join(
            subquery,
            PacienteModel.datos_extra["personaid"].astext == subquery.c.personaid
        )
        .filter(PacienteModel.estado != "I")
        .order_by(
            subquery.c.total_registros.desc(),
            subquery.c.personaid,
            PacienteModel.id
        )
    )

    resultados = query.all()

    return [
        {
            "id": r.id,
            "nombre": r.nombre,
            "expediente": r.expediente,
            "personaid": r.personaid,
            "total_registros": r.total_registros
        }
        for r in resultados
    ]