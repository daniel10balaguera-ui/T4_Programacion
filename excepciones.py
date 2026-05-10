"""
excepciones.py - Excepciones personalizadas del sistema Software FJ
Curso: Programación 213023 - UNAD
"""


class SistemaFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


class ClienteInvalidoError(SistemaFJError):
    """Error al registrar o validar un cliente."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ServicioInvalidoError(SistemaFJError):
    """Error al crear o configurar un servicio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ReservaInvalidaError(SistemaFJError):
    """Error al procesar una reserva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class ServicioNoDisponibleError(SistemaFJError):
    """Servicio no disponible para reserva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_NO_DISPONIBLE")


class ParametroFaltanteError(SistemaFJError):
    """Parámetro requerido no proporcionado."""
    def __init__(self, parametro: str):
        super().__init__(f"Parámetro obligatorio faltante: '{parametro}'", "ERR_PARAMETRO")


class CalculoCostoError(SistemaFJError):
    """Error en el cálculo de costos."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CALCULO")


class OperacionNoPermitidaError(SistemaFJError):
    """Operación no permitida en el estado actual."""
    def __init__(self, operacion: str, estado: str):
        super().__init__(
            f"Operación '{operacion}' no permitida cuando el estado es '{estado}'",
            "ERR_OPERACION"
        )
