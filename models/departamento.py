class Departamento:
    """Representa un departamento dentro de la organización EcoTech."""
    
    def __init__(self, id_departamento: str, nombre: str, gerente_id: str):
        self._id_departamento: str = id_departamento
        self._nombre: str = nombre
        self._gerente_id: str = gerente_id

    @property
    def id_departamento(self) -> str:
        return self._id_departamento

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def gerente_id(self) -> str:
        return self._gerente_id

    def obtener_detalles(self) -> str:
        return f"ID: {self._id_departamento} | Nombre: {self._nombre} | Gerente ID: {self._gerente_id}"