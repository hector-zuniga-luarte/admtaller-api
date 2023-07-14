
from pydantic import BaseModel


# Modelo que representa un agrupador
class Agrupador(BaseModel):

    cod_agrupador: int
    nom_agrupador: str
