
from pydantic import BaseModel
from datetime import date
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


class RegistroConsultaResumenProductoRangoFechas(BaseModel):
    nom_carrera: str
    nom_categ_producto: str
    nom_producto: str
    cantidad_total_productos: float
    nom_unidad_medida: str
    precio_producto: int
    precio_total_productos: int


class RegistroDetalleProductoTallerRangoFechas(BaseModel):
    nom_carrera: str
    nom_categ_producto: str
    nom_producto: str
    cantidad: float
    nom_unidad_medida: str
    precio: int
    precio_total: float
    fecha: date
    nom_periodo_academ: str
    sigla: str
    nom_asign: str
    seccion: int
    semana: int
    titulo_preparacion: str
