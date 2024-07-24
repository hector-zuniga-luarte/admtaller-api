
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un usuario
class Taller(BaseModel):

    id_taller: Optional[int]
    titulo_preparacion: Optional[str]
    detalle_preparacion: Optional[str]
    semana: int
    sigla: Optional[str]
    nom_asign: Optional[str]
    costo_total: int
    