"""
servicios.py - Clase abstracta Servicio y servicios especializados
Curso: Programación 213023 - UNAD

Servicios implementados:
  - ReservaSala      → reserva de salas de reunión
  - AlquilerEquipo   → alquiler de equipos tecnológicos
  - AsesoriaTecnica  → asesorías especializadas con consultor
"""

from abc import abstractmethod
from entidades import EntidadBase
from excepciones import (
    ServicioInvalidoError,
    ServicioNoDisponibleError,
    CalculoCostoError,
    ParametroFaltanteError,
)


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA SERVICIO
# ─────────────────────────────────────────────────────────────────────────────

class Servicio(EntidadBase):
    """
    Clase abstracta que define el contrato para todos los servicios de Software FJ.
    Implementa abstracción, herencia y polimorfismo.
    """

    IMPUESTO_BASE = 0.19  # IVA Colombia 19 %

    def __init__(self, id_servicio: str, nombre: str, precio_hora: float, disponible: bool = True):
        try:
            super().__init__(id_servicio)
        except ParametroFaltanteError:
            raise ServicioInvalidoError("El ID del servicio no puede estar vacío.")

        if not nombre or not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El nombre del servicio no puede estar vacío.")
        if not isinstance(precio_hora, (int, float)) or precio_hora <= 0:
            raise ServicioInvalidoError(
                f"El precio por hora debe ser un número positivo (recibido: {precio_hora})."
            )

        self._nombre = nombre.strip()
        self._precio_hora = float(precio_hora)
        self._disponible = bool(disponible)

    # ── Propiedades ────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = bool(valor)

    # ── Métodos abstractos (polimorfismo) ───────────────────────────────────

    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """Costo base sin impuestos."""
        pass

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida parámetros específicos del servicio antes de reservar."""
        pass

    @abstractmethod
    def tipo_servicio(self) -> str:
        """Retorna el tipo de servicio como cadena."""
        pass

    # ── Métodos sobrecargados (simulado con parámetros opcionales) ──────────

    def calcular_costo_total(
        self,
        horas: float,
        aplicar_impuesto: bool = True,
        descuento: float = 0.0,
        impuesto_personalizado: float = None,
    ) -> float:
        """
        Calcula el costo total con variantes:
          - calcular_costo_total(horas)                        → con IVA
          - calcular_costo_total(horas, False)                 → sin IVA
          - calcular_costo_total(horas, descuento=0.10)        → con 10% descuento
          - calcular_costo_total(horas, impuesto_personalizado=0.05) → IVA especial
        """
        if horas <= 0:
            raise CalculoCostoError(f"Las horas deben ser positivas (recibido: {horas}).")
        if not (0.0 <= descuento < 1.0):
            raise CalculoCostoError(f"El descuento debe estar entre 0 y 1 (recibido: {descuento}).")

        costo_base = self.calcular_costo(horas)
        costo_con_descuento = costo_base * (1 - descuento)

        if aplicar_impuesto:
            tasa = impuesto_personalizado if impuesto_personalizado is not None else self.IMPUESTO_BASE
            if tasa < 0:
                raise CalculoCostoError(f"La tasa de impuesto no puede ser negativa (recibido: {tasa}).")
            total = costo_con_descuento * (1 + tasa)
        else:
            total = costo_con_descuento

        return round(total, 2)

    def verificar_disponibilidad(self):
        """Lanza excepción si el servicio no está disponible."""
        if not self._disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' (ID: {self._id}) no está disponible actualmente."
            )

    def validar(self) -> bool:
        return bool(self._nombre and self._precio_hora > 0)

    def describir(self) -> str:
        estado = "✔ Disponible" if self._disponible else "✘ No disponible"
        return (
            f"{self.tipo_servicio()}[{self._id}] | {self._nombre} | "
            f"${self._precio_hora:,.0f}/h | {estado}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 1: RESERVA DE SALA
# ─────────────────────────────────────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de salas de reunión.
    Precio varía según capacidad y equipamiento de la sala.
    """

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_hora: float,
        capacidad_max: int,
        tiene_proyector: bool = False,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_hora, disponible)
        if not isinstance(capacidad_max, int) or capacidad_max < 1:
            raise ServicioInvalidoError(
                f"La capacidad máxima debe ser un entero positivo (recibido: {capacidad_max})."
            )
        self._capacidad_max = capacidad_max
        self._tiene_proyector = bool(tiene_proyector)

    @property
    def capacidad_max(self) -> int:
        return self._capacidad_max

    @property
    def tiene_proyector(self) -> bool:
        return self._tiene_proyector

    def tipo_servicio(self) -> str:
        return "ReservaSala"

    def calcular_costo(self, horas: float) -> float:
        """Costo base: precio_hora × horas. Proyector agrega 15 %."""
        if horas <= 0:
            raise CalculoCostoError("Las horas deben ser un valor positivo.")
        extra_proyector = 0.15 if self._tiene_proyector else 0.0
        return round(self._precio_hora * horas * (1 + extra_proyector), 2)

    def validar_parametros(self, **kwargs) -> bool:
        """Valida que el número de asistentes no supere la capacidad."""
        asistentes = kwargs.get("asistentes", 1)
        if not isinstance(asistentes, int) or asistentes < 1:
            raise ServicioInvalidoError("El número de asistentes debe ser un entero positivo.")
        if asistentes > self._capacidad_max:
            raise ServicioInvalidoError(
                f"La sala '{self._nombre}' tiene capacidad para {self._capacidad_max} personas, "
                f"pero se solicitaron {asistentes} asistentes."
            )
        return True

    def describir(self) -> str:
        proyector = "con proyector" if self._tiene_proyector else "sin proyector"
        return (
            f"{super().describir()} | Cap. {self._capacidad_max} personas | {proyector}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 2: ALQUILER DE EQUIPO
# ─────────────────────────────────────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos.
    Incluye cargo adicional por seguro obligatorio.
    """

    SEGURO_PORCENTAJE = 0.05  # 5 % sobre el costo base

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_hora: float,
        tipo_equipo: str,
        cantidad_disponible: int,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_hora, disponible)
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ServicioInvalidoError("El tipo de equipo no puede estar vacío.")
        if not isinstance(cantidad_disponible, int) or cantidad_disponible < 0:
            raise ServicioInvalidoError("La cantidad disponible debe ser un entero no negativo.")
        self._tipo_equipo = tipo_equipo.strip()
        self._cantidad_disponible = cantidad_disponible

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def cantidad_disponible(self) -> int:
        return self._cantidad_disponible

    def reducir_stock(self, cantidad: int = 1):
        if cantidad > self._cantidad_disponible:
            raise ServicioNoDisponibleError(
                f"Stock insuficiente: se solicitaron {cantidad} unidades de "
                f"'{self._nombre}', pero solo hay {self._cantidad_disponible}."
            )
        self._cantidad_disponible -= cantidad
        if self._cantidad_disponible == 0:
            self._disponible = False

    def tipo_servicio(self) -> str:
        return "AlquilerEquipo"

    def calcular_costo(self, horas: float) -> float:
        """Costo base + seguro (5 %)."""
        if horas <= 0:
            raise CalculoCostoError("Las horas deben ser un valor positivo.")
        base = self._precio_hora * horas
        seguro = base * self.SEGURO_PORCENTAJE
        return round(base + seguro, 2)

    def validar_parametros(self, **kwargs) -> bool:
        """Valida que haya stock suficiente para la cantidad solicitada."""
        cantidad = kwargs.get("cantidad", 1)
        if not isinstance(cantidad, int) or cantidad < 1:
            raise ServicioInvalidoError("La cantidad solicitada debe ser un entero positivo.")
        if cantidad > self._cantidad_disponible:
            raise ServicioNoDisponibleError(
                f"No hay suficientes unidades de '{self._nombre}'. "
                f"Disponibles: {self._cantidad_disponible}, solicitadas: {cantidad}."
            )
        return True

    def describir(self) -> str:
        return (
            f"{super().describir()} | Tipo: {self._tipo_equipo} | "
            f"Stock: {self._cantidad_disponible} uds."
        )


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 3: ASESORÍA TÉCNICA
# ─────────────────────────────────────────────────────────────────────────────

class AsesoriaTecnica(Servicio):
    """
    Servicio de asesorías especializadas con consultor asignado.
    Tiene duración mínima obligatoria de 1 hora.
    """

    DURACION_MINIMA_HORAS = 1.0

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        precio_hora: float,
        area_especialidad: str,
        consultor: str,
        disponible: bool = True,
    ):
        super().__init__(id_servicio, nombre, precio_hora, disponible)
        if not area_especialidad or not isinstance(area_especialidad, str):
            raise ServicioInvalidoError("El área de especialidad no puede estar vacía.")
        if not consultor or not isinstance(consultor, str):
            raise ServicioInvalidoError("El nombre del consultor no puede estar vacío.")
        self._area_especialidad = area_especialidad.strip()
        self._consultor = consultor.strip().title()

    @property
    def area_especialidad(self) -> str:
        return self._area_especialidad

    @property
    def consultor(self) -> str:
        return self._consultor

    def tipo_servicio(self) -> str:
        return "AsesoriaTecnica"

    def calcular_costo(self, horas: float) -> float:
        """Costo base con duración mínima garantizada."""
        if horas <= 0:
            raise CalculoCostoError("Las horas deben ser un valor positivo.")
        horas_facturables = max(horas, self.DURACION_MINIMA_HORAS)
        return round(self._precio_hora * horas_facturables, 2)

    def validar_parametros(self, **kwargs) -> bool:
        """Valida que la duración cumpla el mínimo requerido."""
        horas = kwargs.get("horas", 0)
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise ServicioInvalidoError("La duración de la asesoría debe ser un número positivo.")
        if horas < self.DURACION_MINIMA_HORAS:
            raise ServicioInvalidoError(
                f"La asesoría requiere mínimo {self.DURACION_MINIMA_HORAS} hora(s). "
                f"Se solicitaron {horas} hora(s)."
            )
        return True

    def describir(self) -> str:
        return (
            f"{super().describir()} | Área: {self._area_especialidad} | "
            f"Consultor: {self._consultor}"
        )
