
from pydantic import BaseModel
from typing import Optional


# Modelo que representa un usuario
class Usuario(BaseModel):
    id_usuario: Optional[int]
    login: str
    hash_password: Optional[str]
    primer_apellido: str
    segundo_apellido: str
    nom: str
    nom_preferido: Optional[str]
    cod_perfil: int
    cod_carrera: Optional[int]
    nom_perfil: Optional[str]
    nom_carrera: Optional[str]
