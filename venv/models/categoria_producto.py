
from pydantic import BaseModel


# Modelo que representa un agrupador
class CategoriaProducto(BaseModel):

    cod_categ_producto: int
    nom_categ_producto: str
