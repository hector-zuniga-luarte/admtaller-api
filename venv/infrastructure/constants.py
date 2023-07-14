
from enum import Enum


# Constantes asociados a tipos de perfil de usuario
class Const(int, Enum):
    K_ADMINISTRADOR_TI: int = 0
    K_ADMINISTRADOR_CARRERA: int = 1
    K_DOCENTE: int = 2
