
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un producto
class Producto(BaseModel):

    id_producto: Optional[int]
    nom_producto: str
    precio: int
    cod_unidad_medida: int
    cod_categ_producto: int
    nom_unidad_medida: Optional[str]
    nom_categ_producto: Optional[str]
