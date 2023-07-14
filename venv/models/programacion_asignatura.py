
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un producto en un taller específico
class ProgramacionAsignatura(BaseModel):

    ano_academ: int
    cod_periodo_academ: int
    sigla: str
    seccion: int
    cod_carrera: Optional[int]
    nom_carrera: Optional[str]
    nom_asignatura: Optional[str]
    nom_periodo_academ: Optional[str]
