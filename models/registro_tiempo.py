from datetime import date

class RegistroTiempo:
    """Representa el tiempo trabajado registrado por un empleado en un proyecto."""
    
    def __init__(self, id_registro: str, fecha: date, horas: int, descripcion: str):
        self._id_registro: str = id_registro
        self._fecha: date = fecha
        self._horas: int = horas
        self._descripcion: str = descripcion

    @property
    def id_registro(self) -> str:
        return self._id_registro

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def horas(self) -> int:
        return self._horas

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def validar_horas(self) -> bool:
        return 0 < self._horas <= 24