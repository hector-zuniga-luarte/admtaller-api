
from pydantic import BaseModel
from typing import Optional


# Modelos que representan registros de consultas
class RegistroConsultaValorizacionTaller(BaseModel):
    nom_carrera: str
    sigla: str
    nom_asign: str
    semana: int
    id_taller: int
    titulo_preparacion: str
    total_taller: int


class RegistroConsultaPresupuestoEstimadoAsignatura(BaseModel):
    nom_carrera: str
    sigla: str
    nom_asign: str
    total_seccion: int
    total_asign: int
    total: int


class RegistroConsultaAsignacionRegistroTalleresDocente(BaseModel):
    nom_carrera: str
    primer_apellido: str
    segundo_apellido: str
    nom_preferido: str
    sigla: str
    nom_asign: str
    seccion: Optional[int]
    cod_periodo_academ: Optional[int]
    nom_periodo_academ: Optional[str]
    nom_asign: Optional[str]
    total_taller_asignado: int
    total_taller_registrado: int
