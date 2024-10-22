
from enum import Enum


# Constantes asociados a tipos de perfil de usuario y otros
class Const(int, Enum):

    # Asociadas a perfil de usuario
    K_ADMINISTRADOR_TI: int = 0
    K_ADMINISTRADOR_CARRERA: int = 1
    K_DOCENTE: int = 2
    K_JEFE_BODEGA: int = 3

    # Asociados a carreras
    K_SIN_CARRERA: int = 0
