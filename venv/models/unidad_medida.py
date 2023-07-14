
from pydantic import BaseModel


# Modelo que representa un agrupador
class UnidadMedida(BaseModel):

    cod_unidad_medida: int
    nom_unidad_medida: str
    nom_unidad_medida_abrev: str
