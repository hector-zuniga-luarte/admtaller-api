
from pydantic import BaseModel
from typing import Optional


# Modelo que representa la programación de un taller específico
class ProgramacionTaller(BaseModel):

    fecha: str
    ano_academ: int
    cod_periodo_academ: int
    sigla: str
    seccion: int
    id_taller: int
    id_usuario: Optional[int]
    nom_periodo_academ: Optional[str]
    nom_asignatura: Optional[str]
    titulo_preparacion: Optional[str]
    semana: Optional[int]
    login: Optional[str]
    nom_preferido: Optional[str]
    primer_apellido: Optional[str]
    segundo_apellido: Optional[str]
