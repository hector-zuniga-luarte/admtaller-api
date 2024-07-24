
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un usuario
class Asignatura(BaseModel):

    sigla: str
    nom_asignatura: Optional[str]
    nom_asignatura_abrev: Optional[str]
    cod_carrera: int
    nom_carrera: Optional[str]
    costo_total: int
