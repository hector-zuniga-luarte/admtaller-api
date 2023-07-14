
from typing import Optional
from models.programacion_taller import ProgramacionTaller


class RegistroTaller(ProgramacionTaller):
    indicador_usuario: Optional[int]
    indicador_registro: Optional[int]
    obs: Optional[str]
