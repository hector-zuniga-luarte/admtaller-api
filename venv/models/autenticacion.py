
from pydantic import BaseModel
from typing import Optional


# Modelo para procesar y retornar la autenticación
class Autenticacion(BaseModel):
    login: str
    hash_password: Optional[str]
    autenticado: bool = False


# Modelo para procesar y retornar el cambio de contraseña
class CambioPassword(BaseModel):
    id_usuario: int
    nueva_password: Optional[str]
    confirmacion_nueva_password: Optional[str]
    modificada: bool = False
