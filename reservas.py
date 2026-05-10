"""
reservas.py - Clase Reserva con manejo avanzado de excepciones
Curso: Programación 213023 - UNAD
"""

import datetime
import uuid
from entidades import Cliente
from servicios import Servicio
from excepciones import (
    ReservaInvalidaError,
    OperacionNoPermitidaError,
    CalculoCostoError,
    ParametroFaltanteError,
)


class EstadoReserva:
    """Constantes para los posibles estados de una reserva."""
    PENDIENTE   = "PENDIENTE"
    CONFIRMADA  = "CONFIRMADA"
    CANCELADA   = "CANCELADA"
    PROCESADA   = "PROCESADA"


class Reserva:
    """
    Integra un Cliente con un Servicio para gestionar la reserva.
    Implementa confirmación, cancelación y procesamiento con manejo de excepciones.

    Manejo de excepciones demostrado:
      - try/except             → validación de parámetros en __init__
      - try/except/else        → confirmación de reserva
      - try/except/finally     → procesamiento de reserva
      - encadenamiento         → raise X from Y en cálculo de costo
    """

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        parametros_servicio: dict = None,
    ):
        # ── try/except: validación de todos los parámetros de entrada ──────
        try:
            if cliente is None:
                raise ParametroFaltanteError("cliente")
            if not isinstance(cliente, Cliente):
                raise ReservaInvalidaError("El parámetro 'cliente' debe ser una instancia de Cliente.")
            if servicio is None:
                raise ParametroFaltanteError("servicio")
            if not isinstance(servicio, Servicio):
                raise ReservaInvalidaError("El parámetro 'servicio' debe ser una instancia de Servicio.")
            if not isinstance(horas, (int, float)) or horas <= 0:
                raise ReservaInvalidaError(
                    f"Las horas deben ser un número positivo (recibido: {horas})."
                )

            self._id = str(uuid.uuid4())[:8].upper()
            self._cliente = cliente
            self._servicio = servicio
            self._horas = float(horas)
            self._parametros = parametros_servicio or {}
            self._estado = EstadoReserva.PENDIENTE
            self._costo_total: float = 0.0
            self._fecha_creacion = datetime.datetime.now()
            self._fecha_procesamiento = None

        except (ReservaInvalidaError, ParametroFaltanteError):
            raise
        except Exception as e:
            raise ReservaInvalidaError(f"Error inesperado al crear la reserva: {e}") from e

    # ── Propiedades ────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def costo_total(self) -> float:
        return self._costo_total

    # ── Confirmación con try/except/else ───────────────────────────────────

    def confirmar(self, descuento: float = 0.0) -> float:
        """
        Confirma la reserva validando disponibilidad y parámetros.
        Usa try/except/else: si no hay errores, registra el costo.

        Returns:
            Costo total calculado con IVA y descuento opcional.
        """
        if self._estado != EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError("confirmar", self._estado)

        try:
            # 1. Verificar disponibilidad del servicio
            self._servicio.verificar_disponibilidad()

            # 2. Validar parámetros específicos del servicio
            self._servicio.validar_parametros(
                horas=self._horas,
                **self._parametros,
            )

            # 3. Calcular costo total (método sobrecargado)
            costo = self._servicio.calcular_costo_total(
                self._horas,
                aplicar_impuesto=True,
                descuento=descuento,
            )

        except (CalculoCostoError, ValueError) as e:
            # Encadenamiento de excepciones
            raise ReservaInvalidaError(
                f"No se pudo calcular el costo para la reserva {self._id}: {e}"
            ) from e

        else:
            # Bloque else: se ejecuta solo si NO hubo excepción
            self._costo_total = costo
            self._estado = EstadoReserva.CONFIRMADA
            self._cliente.agregar_reserva_id(self._id)
            return self._costo_total

    # ── Cancelación ────────────────────────────────────────────────────────

    def cancelar(self) -> str:
        """Cancela la reserva si el estado lo permite."""
        if self._estado == EstadoReserva.CANCELADA:
            raise OperacionNoPermitidaError("cancelar", self._estado)
        if self._estado == EstadoReserva.PROCESADA:
            raise OperacionNoPermitidaError("cancelar", self._estado)

        estado_anterior = self._estado
        self._estado = EstadoReserva.CANCELADA
        return (
            f"Reserva {self._id} cancelada. Estado anterior: {estado_anterior}."
        )

    # ── Procesamiento con try/except/finally ───────────────────────────────

    def procesar(self) -> str:
        """
        Procesa la reserva (simula la ejecución del servicio).
        Usa try/except/finally: el bloque finally siempre registra la fecha.
        """
        if self._estado != EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError("procesar", self._estado)

        resultado = None
        try:
            # Simular posible fallo durante el procesamiento
            if self._horas > 24:
                raise ReservaInvalidaError(
                    f"No se puede procesar una reserva de más de 24 horas continuas ({self._horas}h)."
                )
            resultado = (
                f"Reserva {self._id} procesada exitosamente. "
                f"Servicio: {self._servicio.nombre}. "
                f"Duración: {self._horas}h. "
                f"Costo final: ${self._costo_total:,.2f} COP."
            )
            self._estado = EstadoReserva.PROCESADA

        except ReservaInvalidaError:
            self._estado = EstadoReserva.CANCELADA
            raise

        finally:
            # Siempre se registra la fecha de intento de procesamiento
            self._fecha_procesamiento = datetime.datetime.now()

        return resultado

    # ── Resumen ────────────────────────────────────────────────────────────

    def resumen(self) -> str:
        return (
            f"\n{'─'*60}\n"
            f"  RESERVA ID   : {self._id}\n"
            f"  Estado       : {self._estado}\n"
            f"  Cliente      : {self._cliente.nombre} ({self._cliente.email})\n"
            f"  Servicio     : {self._servicio.nombre}\n"
            f"  Horas        : {self._horas}h\n"
            f"  Costo total  : ${self._costo_total:,.2f} COP\n"
            f"  Creada       : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'─'*60}"
        )

    def __repr__(self) -> str:
        return f"Reserva[{self._id}] | {self._cliente.nombre} | {self._servicio.nombre} | {self._estado}"
