
from typing import List


class Resumen:
    def __init__(self,
                 concepto: str,
                 valor: int):
        self.concepto = concepto
        self.valor = valor


class Dashboard:
    def __init__(self, 
                 nom_carrera: str,
                 resumen: List[Resumen]):

        self.nom_carrera = nom_carrera
        self.resumen = resumen
