
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un usuario
class PeriodoAcademico(BaseModel):

    cod_periodo_academ: Optional[int]
    nom_periodo_academ: Optional[str]
    nom_periodo_academ_abrev: Optional[str]
