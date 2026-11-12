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

class Servicio(EntidadSistema, ABC):
    """Clase abstracta Servicio que implementa polimorfismo."""
    
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, disponible: bool = True):
        super().__init__(identificador)
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base
        self.disponible = disponible

    @property
    def costo_base(self) -> float:
        return self._costo_base

    @costo_base.setter
    def costo_base(self, valor: float):
        if valor < 0:
            raise ServicioNoDisponibleError("El costo base no puede ser negativo.")
        self._costo_base = float(valor)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Método polimórfico para calcular costos (admite sobrecarga simulada)."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Método polimórfico para describir el servicio."""
        pass

    def obtener_detalles(self) -> str:
        estado = "Disponible" if self.disponible else "No Disponible"
        return f"Servicio: {self.nombre_servicio} | Costo Base: ${self.costo_base:.2f} | Estado: {estado}"


class ReservaSala(Servicio):
    """Servicio especializado de reserva de salas."""
    
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, capacidad: int):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.capacidad = capacidad

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor: int):
        if valor <= 0:
            raise ServicioNoDisponibleError("La capacidad de la sala debe ser mayor a 0.")
        self._capacidad = valor

    # Demostración de métodos sobrecargados (argumentos opcionales)
    def calcular_costo(self, horas: int = 1, incluir_impuesto: bool = True, descuento_porcentaje: float = 0.0) -> float:
        """Calcula costo de sala con horas, impuestos opcionales y descuentos."""
        try:
            if horas <= 0:
                raise ValueError("Las horas de reserva deben ser mayores a cero.")
            
            subtotal = self.costo_base * horas
            if descuento_porcentaje > 0:
                subtotal -= subtotal * (descuento_porcentaje / 100.0)
            
            if incluir_impuesto:
                subtotal *= 1.19  # IVA 19%
            
            return round(subtotal, 2)
        except Exception as e:
            raise ServicioNoDisponibleError(f"Error al calcular costo de sala: {e}") from e

    def describir_servicio(self) -> str:
        return f"[Reserva de Sala] {self.nombre_servicio} - Capacidad: {self.capacidad} personas. Costo base/hora: ${self.costo_base}"


class AlquilerEquipo(Servicio):
    """Servicio especializado de alquiler de equipos tecnológicos o de oficina."""
    
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, serial_equipo: str):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.serial_equipo = serial_equipo

    def calcular_costo(self, dias: int = 1, seguro_adicional: bool = False) -> float:
        """Calcula costo de alquiler por días con opción de seguro."""
        try:
            if dias <= 0:
                raise ValueError("Los días de alquiler deben ser mayores a cero.")
            
            total = self.costo_base * dias
            if seguro_adicional:
                total += 15.0 * dias  # Tarifa fija de seguro por día
            
            return round(total, 2)
        except Exception as e:
            raise ServicioNoDisponibleError(f"Error al calcular costo de equipo: {e}") from e

    def describir_servicio(self) -> str:
        return f"[Alquiler de Equipo] {self.nombre_servicio} (Serial: {self.serial_equipo}). Costo base/día: ${self.costo_base}"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de asesorías profesionales."""
    
    def __init__(self, identificador: str, nombre_servicio: str, costo_base: float, area_experticia: str):
        super().__init__(identificador, nombre_servicio, costo_base)
        self.area_experticia = area_experticia

    def calcular_costo(self, sesiones: int = 1, nivel_senior: bool = False) -> float:
        """Calcula costo de asesorías según número de sesiones y nivel del experto."""
        try:
            if sesiones <= 0:
                raise ValueError("El número de sesiones debe ser mayor a cero.")
            
            multiplicador = 1.5 if nivel_senior else 1.0
            total = self.costo_base * sesiones * multiplicador
            return round(total, 2)
        except Exception as e:
            raise ServicioNoDisponibleError(f"Error al calcular costo de asesoría: {e}") from e

    def describir_servicio(self) -> str:
        return f"[Asesoría Especializada] {self.nombre_servicio} en área {self.area_experticia}. Costo base/sesión: ${self.costo_base}"


# ==========================================
# 5. CLASE RESERVA
# ==========================================
