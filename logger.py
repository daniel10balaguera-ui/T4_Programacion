"""
logger.py - Sistema de registro de eventos y errores
Curso: Programación 213023 - UNAD
"""

import datetime
import os


class Logger:
    """
    Clase singleton para el registro centralizado de eventos y errores.
    Escribe en archivo sistema_fj.log y muestra en consola.
    """

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.ruta_log = "sistema_fj.log"
        self._escribir_separador("INICIO DE SESIÓN")

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _escribir(self, nivel: str, mensaje: str):
        linea = f"[{self._timestamp()}] [{nivel:<8}] {mensaje}\n"
        try:
            with open(self.ruta_log, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError as e:
            print(f"[LOGGER] No se pudo escribir en el log: {e}")
        print(linea, end="")

    def _escribir_separador(self, titulo: str = ""):
        sep = "=" * 70
        if titulo:
            linea = f"\n{sep}\n  {titulo} — {self._timestamp()}\n{sep}\n"
        else:
            linea = sep + "\n"
        try:
            with open(self.ruta_log, "a", encoding="utf-8") as f:
                f.write(linea)
        except OSError:
            pass
        print(linea, end="")

    def info(self, mensaje: str):
        self._escribir("INFO", mensaje)

    def advertencia(self, mensaje: str):
        self._escribir("ADVERTENCIA", mensaje)

    def error(self, mensaje: str):
        self._escribir("ERROR", mensaje)

    def exito(self, mensaje: str):
        self._escribir("ÉXITO", mensaje)

    def seccion(self, titulo: str):
        self._escribir_separador(titulo)
