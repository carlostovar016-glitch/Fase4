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

class Reserva(EntidadSistema):
    """Integra cliente, servicio, duración y estado con manejo de excepciones y ciclos de vida."""
    
    ESTADOS = ["PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA"]

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio, cantidad_tiempo: int):
        super().__init__(identificador)
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_tiempo = cantidad_tiempo
        self._estado = "PENDIENTE"
        self.costo_total = 0.0

    @property
    def estado(self) -> str:
        return self._estado

    def confirmar_reserva(self, *args, **kwargs):
        """Confirma la reserva aplicando el cálculo del servicio mediante polimorfismo y manejo completo de try/except/else/finally."""
        try:
            logging.info(f"Intentando confirmar reserva {self.identificador}...")
            if not self.servicio.disponible:
                raise OperacionNoPermitidaError(f"El servicio '{self.servicio.nombre_servicio}' no se encuentra disponible.")
            if self._estado != "PENDIENTE":
                raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado '{self._estado}'.")
            
            # Cálculo polimórfico del costo utilizando kwargs o args dinámicos
            self.costo_total = self.servicio.calcular_costo(*args, **kwargs)
            self._estado = "CONFIRMADA"
            
        except (OperacionNoPermitidaError, ServicioNoDisponibleError) as e:
            logging.error(f"Error de negocio al confirmar reserva {self.identificador}: {e}")
            raise
        except Exception as e:
            logging.critical(f"Error inesperado al confirmar reserva {self.identificador}: {e}")
            raise ReservaInvalidaError(f"Error crítico en confirmación: {e}") from e
        else:
            logging.info(f"Reserva {self.identificador} confirmada exitosamente. Costo Total: ${self.costo_total}")
        finally:
            logging.info(f"Finalizó el proceso de intento de confirmación para reserva {self.identificador}.")

    def cancelar_reserva(self):
        """Cancela una reserva activa o pendiente."""
        try:
            if self._estado == "CANCELADA":
                raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
            if self._estado == "PROCESADA":
                raise OperacionNoPermitidaError("No se puede cancelar una reserva que ya fue procesada/ejecutada.")
            
            self._estado = "CANCELADA"
            logging.info(f"Reserva {self.identificador} cancelada correctamente.")
        except Exception as e:
            logging.error(f"Fallo al cancelar la reserva {self.identificador}: {e}")
            raise

    def procesar_reserva(self):
        """Procesa la reserva finalizando su ciclo."""
        try:
            if self._estado != "CONFIRMADA":
                raise OperacionNoPermitidaError(f"Solo se pueden procesar reservas confirmadas. Estado actual: {self._estado}")
            
            self._estado = "PROCESADA"
            logging.info(f"Reserva {self.identificador} procesada y finalizada con éxito.")
        except Exception as e:
            logging.error(f"Error al procesar reserva {self.identificador}: {e}")
            raise

    def obtener_detalles(self) -> str:
        return (f"Reserva [ID: {self.identificador}] | Estado: {self._estado} | "
                f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre_servicio} | "
                f"Costo Total: ${self.costo_total:.2f}")


# ==========================================
# 6. SIMULADOR DE 10 OPERACIONES (Válidas e Inválidas)
# ==========================================

def ejecutar_simulacion():
    print("=" * 70)
    print(" INICIANDO SIMULACIÓN INTEGRAL - SOFTWARE FJ (SIN BASE DE DATOS)")
    print("=" * 70)
    
    # Listas internas para gestión en memoria
    clientes = []
    servicios = []
    reservas = []

    # Operación 1: Registro VÁLIDO de cliente
    print("\n[Operopación 1] Registro Válido de Cliente...")
    try:
        c1 = Cliente("C001", "Ana María Pérez", "ana.perez@email.com", "3104567890")
        clientes.append(c1)
        print(f"Éxito: {c1.obtener_detalles()}")
    except Exception as e:
        print(f"Error capturado: {e}")

    # Operación 2: Registro INVÁLIDO de cliente (Correo incorrecto)
    print("\n[Operación 2] Registro Inválido de Cliente (Correo erróneo)...")
    try:
        c2 = Cliente("C002", "Carlos Gómez", "correo_sin_arroba.com", "3201234567")
        clientes.append(c2)
    except ClienteInvalidoError as e:
        print(f"Excepción controlada correctamente: {e}")
        logging.warning(f"Operación 2 interceptada: {e}")

    # Operación 3: Creación VÁLIDA de Servicio (Sala de Conferencias)
    print("\n[Operación 3] Creación Válida de Servicio de Sala...")
    try:
        s1 = ReservaSala("S001", "Sala Ejecutiva Alpha", 50.0, capacidad=15)
        servicios.append(s1)
        print(f"Éxito: {s1.describir_servicio()}")
    except Exception as e:
        print(f"Error: {e}")

    # Operación 4: Creación INVÁLIDA de Servicio (Costo negativo)
    print("\n[Operación 4] Creación Inválida de Servicio (Costo negativo)...")
    try:
        s_erroneo = AlquilerEquipo("S999", "Servidor Roto", -100.0, "SER-000")
        servicios.append(s_erroneo)
    except ServicioNoDisponibleError as e:
        print(f"Excepción controlada correctamente: {e}")
        logging.warning(f"Operación 4 interceptada: {e}")

    # Operación 5: Creación VÁLIDA de Alquiler de Equipo y Asesoría
    print("\n[Operación 5] Creación Válida de Alquiler de Equipo y Asesoría...")
    try:
        s2 = AlquilerEquipo("S002", "Kit de Realidad Virtual", 35.0, "VR-9982")
        s3 = AsesoriaEspecializada("S003", "Arquitectura Cloud AWS", 120.0, "Cloud Computing")
        servicios.extend([s2, s3])
        print(f"Éxito: {s2.describir_servicio()}")
        print(f"Éxito: {s3.describir_servicio()}")
    except Exception as e:
        print(f"Error: {e}")

    # Operación 6: Creación de Reserva VÁLIDA y Confirmación exitosa (con sobrecarga de parámetros)
    print("\n[Operación 6] Reserva Válida y Confirmación con Cálculo Personalizado...")
    try:
        reserva1 = Reserva("R001", clientes[0], servicios[0], cantidad_tiempo=4)
        reservas.append(reserva1)
        # Confirmando reserva de sala por 4 horas, con 10% de descuento e impuestos
        reserva1.confirmar_reserva(horas=4, incluir_impuesto=True, descuento_porcentaje=10.0)
        print(f"Éxito: {reserva1.obtener_detalles()}")
    except Exception as e:
        print(f"Error: {e}")

    # Operación 7: Intento de Confirmación de Reserva con Servicio No Disponible (Error simulado)
    print("\n[Operación 7] Reserva sobre servicio no disponible...")
    try:
        servicio_inactivo = ReservaSala("S004", "Sala en Mantenimiento", 40.0, 10)
        servicio_inactivo.disponible = False
        reserva_fallida = Reserva("R002", clientes[0], servicio_inactivo, cantidad_tiempo=2)
        reserva_fallida.confirmar_reserva(horas=2, incluir_impuesto=True)
    except (OperacionNoPermitidaError, ServicioNoDisponibleError) as e:
        print(f"Excepción controlada correctamente: {e}")
        logging.warning(f"Operación 7 interceptada: {e}")

    # Operación 8: Confirmación válida de alquiler de equipo con seguro adicional
    print("\n[Operación 8] Confirmación válida de alquiler de equipo...")
    try:
        reserva2 = Reserva("R003", clientes[0], servicios[1], cantidad_tiempo=3)
        reservas.append(reserva2)
        reserva2.confirmar_reserva(dias=3, seguro_adicional=True)
        print(f"Éxito: {reserva2.obtener_detalles()}")
    except Exception as e:
        print(f"Error: {e}")

    # Operación 9: Cancelación válida de una reserva confirmada
    print("\n[Operación 9] Cancelación válida de reserva confirmada...")
    try:
        reserva3 = Reserva("R004", clientes[0], servicios[2], cantidad_tiempo=2)
        reservas.append(reserva3)
        reserva3.confirmar_reserva(sesiones=2, nivel_senior=True)
        reserva3.cancelar_reserva()
        print(f"Éxito: {reserva3.obtener_detalles()}")
    except Exception as e:
        print(f"Error: {e}")

    # Operación 10: Intento de procesar una reserva no confirmada (error controlado)
    print("\n[Operación 10] Procesamiento inválido de reserva...")
    try:
        reserva4 = Reserva("R005", clientes[0], servicios[0], cantidad_tiempo=1)
        reservas.append(reserva4)
        reserva4.procesar_reserva()
    except OperacionNoPermitidaError as e:
        print(f"Excepción controlada correctamente: {e}")
        logging.warning(f"Operación 10 interceptada: {e}")

    print("\n" + "=" * 70)
    print(" SIMULACIÓN FINALIZADA - RESÚMEN")
    print("=" * 70)
    print(f"Clientes registrados: {len(clientes)}")
    print(f"Servicios creados: {len(servicios)}")
    print(f"Reservas gestionadas: {len(reservas)}")
    for item in reservas:
        print(f"- {item.obtener_detalles()}")


if __name__ == "__main__":
    ejecutar_simulacion()
