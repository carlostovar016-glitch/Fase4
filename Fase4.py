import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DEL SISTEMA DE LOGS Y ERRORES
# ==========================================

LOG_FILENAME = "sistema_fj.log"

# Configurar logging para registrar eventos y errores en archivo
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Excepciones Personalizadas
class ErrorSistemaFJ(Exception):
    """Excepción base para todos los errores del sistema Software FJ."""
    pass

class ClienteInvalidoError(ErrorSistemaFJ):
    """Excepción lanzada cuando los datos del cliente no son válidos."""
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Excepción lanzada cuando un servicio no está disponible o tiene parámetros erróneos."""
    pass

class ReservaInvalidaError(ErrorSistemaFJ):
    """Excepción lanzada ante intentos de reserva incorrectos o no permitidos."""
    pass

class OperacionNoPermitidaError(ErrorSistemaFJ):
    """Excepción lanzada cuando se intenta realizar una operación prohibida por estado o lógica."""
    pass


# ==========================================
# 2. CLASE ABSTRACTA BASE
# ==========================================

class EntidadSistema(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    
    def __init__(self, identificador: str):
        self._identificador = identificador
        self._fecha_creacion = datetime.now()

    @property
    def identificador(self) -> str:
        return self._identificador

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Método abstracto para retornar los detalles de la entidad."""
        pass


# ==========================================
# 3. CLASE CLIENTE
# ==========================================

class Cliente(EntidadSistema):
    """Representa a un cliente de Software FJ con validaciones y encapsulación."""
    
    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not valor.strip():
            raise ClienteInvalidoError("El nombre del cliente no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or "@" not in valor or "." not in valor:
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not valor.isdigit() or len(valor) < 7:
            raise ClienteInvalidoError(f"Número de teléfono inválido: '{valor}'. Debe contener solo dígitos (mínimo 7).")
        self._telefono = valor.strip()

    def obtener_detalles(self) -> str:
        return f"Cliente [ID: {self.identificador}] - Nombre: {self.nombre}, Correo: {self.correo}, Teléfono: {self.telefono}"


# ==========================================
# 4. CLASE ABSTRACTA SERVICIO Y DERIVADAS
# ==========================================
