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

