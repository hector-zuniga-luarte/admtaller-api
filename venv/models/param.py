
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un parámetro del sistema
class Param(BaseModel):
    cod_param: int
    nom_param: Optional[str]
    valor: str
