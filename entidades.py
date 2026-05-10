"""
entidades.py - Clases base abstractas y clase Cliente
Curso: Programación 213023 - UNAD
"""

import re
from abc import ABC, abstractmethod
from excepciones import ClienteInvalidoError, ParametroFaltanteError


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA BASE
# ─────────────────────────────────────────────────────────────────────────────

class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad gestionada por el sistema.
    Implementa abstracción y define la interfaz común obligatoria.
    """

    def __init__(self, id_entidad: str):
        if not id_entidad or not isinstance(id_entidad, str):
            raise ParametroFaltanteError("id_entidad")
        self._id = id_entidad.strip()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción completa de la entidad."""
        pass

    @abstractmethod
    def validar(self) -> bool:
        """Valida que la entidad sea coherente y esté completa."""
        pass

    def __repr__(self) -> str:
        return self.describir()


# ─────────────────────────────────────────────────────────────────────────────
# CLASE CLIENTE
# ─────────────────────────────────────────────────────────────────────────────

class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.
    Aplica encapsulación estricta y validaciones robustas sobre los datos personales.
    """

    PATRON_EMAIL = re.compile(r"^[\w\.\+\-]+@[\w\-]+(\.[\w\-]+)*\.[a-zA-Z]{2,}$")
    PATRON_TELEFONO = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(self, id_cliente: str, nombre: str, email: str, telefono: str):
        try:
            super().__init__(id_cliente)
        except ParametroFaltanteError:
            raise ClienteInvalidoError("El ID del cliente no puede estar vacío.")

        self._nombre = None
        self._email = None
        self._telefono = None
        self._reservas_ids: list[str] = []

        # Setters con validación
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # ── Propiedades con validación ──────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ClienteInvalidoError("El nombre del cliente no puede estar vacío.")
        if len(valor.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoError("El email no puede estar vacío.")
        valor = valor.strip().lower()
        if not self.PATRON_EMAIL.match(valor):
            raise ClienteInvalidoError(f"El email '{valor}' no tiene un formato válido.")
        self._email = valor

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str):
            raise ClienteInvalidoError("El teléfono no puede estar vacío.")
        valor = valor.strip()
        if not self.PATRON_TELEFONO.match(valor):
            raise ClienteInvalidoError(f"El teléfono '{valor}' no tiene un formato válido.")
        self._telefono = valor

    @property
    def reservas_ids(self) -> list:
        return list(self._reservas_ids)  # copia defensiva

    # ── Métodos ────────────────────────────────────────────────────────────

    def agregar_reserva_id(self, id_reserva: str):
        if id_reserva not in self._reservas_ids:
            self._reservas_ids.append(id_reserva)

    def total_reservas(self) -> int:
        return len(self._reservas_ids)

    def validar(self) -> bool:
        return bool(self._nombre and self._email and self._telefono)

    def describir(self) -> str:
        return (
            f"Cliente[{self._id}] | Nombre: {self._nombre} | "
            f"Email: {self._email} | Tel: {self._telefono} | "
            f"Reservas: {self.total_reservas()}"
        )
