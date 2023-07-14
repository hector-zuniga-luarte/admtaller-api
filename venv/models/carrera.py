
from pydantic import BaseModel


class Carrera(BaseModel):
    cod_carrera: int
    nom_carrera: str
    nom_carrera_abrev: str
