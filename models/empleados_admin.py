from datetime import date
from typing import List, Optional
from models.usuario import Usuario
from models.departamento import Departamento
from models.proyecto import Proyecto
from models.registro_tiempo import RegistroTiempo

class Administrador(Usuario):
    """Representa el rol de Administrador."""
    
    def __init__(self, id_usuario: str, email: str):
        super().__init__(id_usuario, email)
        self.departamentos_gestionados: List[Departamento] = []

    def registrar_empleado(self, empleado: 'Empleado') -> None:
        print(f"Administrador {self.id_usuario} registró al empleado {empleado.id_usuario}.")

    def gestionar_departamento(self, departamento: Departamento) -> None:
        if departamento not in self.departamentos_gestionados:
            self.departamentos_gestionados.append(departamento)
            print(f"Departamento '{departamento.nombre}' agregado a la gestión.")


class Empleado(Usuario):
    """Representa el rol de Empleado."""
    
    def __init__(self, id_usuario: str, email: str, fecha_inicio: date, salario: float):
        super().__init__(id_usuario, email)
        self._fecha_inicio: date = fecha_inicio
        self._salario: float = salario
        self.departamento: Optional[Departamento] = None
        self.registros_tiempo: List[RegistroTiempo] = []
        self.proyectos: List[Proyecto] = []

    @property
    def fecha_inicio(self) -> date:
        return self._fecha_inicio

    @property
    def salario(self) -> float:
        return self._salario

    def registrar_hora(self, proyecto_id: str, fecha: date, horas: int, descripcion: str = "") -> None:
        id_reg = f"REG-{len(self.registros_tiempo) + 1}"
        nuevo_registro = RegistroTiempo(id_reg, fecha, horas, descripcion)
        
        if nuevo_registro.validar_horas():
            self.registros_tiempo.append(nuevo_registro)
            print(f"Éxito: Se registraron {horas} hrs en el proyecto '{proyecto_id}'.")
        else:
            print("Error: Las horas deben ser mayores a 0 y como máximo 24.")