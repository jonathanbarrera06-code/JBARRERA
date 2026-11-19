from datetime import date
from typing import List
from models.registro_tiempo import RegistroTiempo

class Proyecto:
    """Representa un proyecto dentro de EcoTech Solutions."""
    
    def __init__(self, id_proyecto: str, nombre: str, descripcion: str, fecha_inicio: date):
        self._id_proyecto: str = id_proyecto
        self._nombre: str = nombre
        self._descripcion: str = descripcion
        self._fecha_inicio: date = fecha_inicio
        self.registros_tiempo: List[RegistroTiempo] = []

    @property
    def id_proyecto(self) -> str:
        return self._id_proyecto

    @property
    def nombre(self) -> str:
        return self._nombre

    def obtener_estado(self) -> str:
        return f"Proyecto '{self._nombre}' [ID: {self._id_proyecto}] - Estado: ACTIVO"