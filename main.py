"""
main.py - Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Curso: Programación 213023 - UNAD

Simula más de 10 operaciones completas (válidas e inválidas),
demostrando manejo robusto de excepciones y POO completa.
"""

import sys
import os

# Asegurar que el directorio actual esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import Logger
from entidades import Cliente
from servicios import ReservaSala, AlquilerEquipo, AsesoriaTecnica
from reservas import Reserva
from excepciones import (
    SistemaFJError,
    ClienteInvalidoError,
    ServicioInvalidoError,
    ReservaInvalidaError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError,
    CalculoCostoError,
)

log = Logger()


# ─────────────────────────────────────────────────────────────────────────────
# REPOSITORIOS EN MEMORIA
# ─────────────────────────────────────────────────────────────────────────────

clientes: dict[str, Cliente] = {}
servicios: dict[str, object] = {}
reservas: dict[str, Reserva] = {}


def registrar_cliente(id_c, nombre, email, telefono) -> Cliente | None:
    """Intenta crear y registrar un cliente. Maneja errores sin interrumpir."""
    try:
        cliente = Cliente(id_c, nombre, email, telefono)
        if not cliente.validar():
            raise ClienteInvalidoError("El cliente no pasó la validación interna.")
        clientes[id_c] = cliente
        log.exito(f"Cliente registrado: {cliente.describir()}")
        return cliente
    except ClienteInvalidoError as e:
        log.error(f"REGISTRO DE CLIENTE FALLIDO → {e}")
        return None
    except Exception as e:
        log.error(f"Error inesperado al registrar cliente '{id_c}': {e}")
        return None


def registrar_servicio(servicio_obj) -> bool:
    """Registra un servicio ya instanciado."""
    try:
        if not servicio_obj.validar():
            raise ServicioInvalidoError("El servicio no pasó la validación interna.")
        servicios[servicio_obj.id] = servicio_obj
        log.exito(f"Servicio registrado: {servicio_obj.describir()}")
        return True
    except SistemaFJError as e:
        log.error(f"REGISTRO DE SERVICIO FALLIDO → {e}")
        return False


def hacer_reserva(
    id_cliente: str,
    id_servicio: str,
    horas: float,
    descuento: float = 0.0,
    **params_servicio,
) -> Reserva | None:
    """
    Flujo completo: busca cliente y servicio, crea, confirma y procesa la reserva.
    Demuestra try/except, try/except/else y try/except/finally.
    """
    # Buscar entidades
    cliente = clientes.get(id_cliente)
    servicio = servicios.get(id_servicio)

    if not cliente:
        log.error(f"Cliente '{id_cliente}' no encontrado. Reserva abortada.")
        return None
    if not servicio:
        log.error(f"Servicio '{id_servicio}' no encontrado. Reserva abortada.")
        return None

    reserva = None
    try:
        # Crear reserva (try/except interno en Reserva.__init__)
        reserva = Reserva(cliente, servicio, horas, params_servicio)
        log.info(f"Reserva creada (PENDIENTE): {reserva}")

        # Confirmar (try/except/else en Reserva.confirmar)
        costo = reserva.confirmar(descuento=descuento)
        log.info(f"Reserva CONFIRMADA | Costo: ${costo:,.2f} COP | {reserva}")

        # Procesar (try/except/finally en Reserva.procesar)
        resultado = reserva.procesar()
        log.exito(resultado)
        reservas[reserva.id] = reserva
        print(reserva.resumen())

    except ServicioNoDisponibleError as e:
        log.error(f"Servicio no disponible → {e}")
        if reserva:
            reservas[reserva.id] = reserva  # guardar aunque sea fallida

    except ReservaInvalidaError as e:
        log.error(f"Reserva inválida → {e}")
        if reserva:
            reservas[reserva.id] = reserva

    except OperacionNoPermitidaError as e:
        log.error(f"Operación no permitida → {e}")

    except SistemaFJError as e:
        log.error(f"Error del sistema → {e}")

    except Exception as e:
        log.error(f"Error inesperado en reserva → {type(e).__name__}: {e}")

    return reserva


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN: 10+ OPERACIONES COMPLETAS
# ─────────────────────────────────────────────────────────────────────────────

def main():
    log.seccion("SOFTWARE FJ — SISTEMA DE GESTIÓN")

    # ══════════════════════════════════════════════════════════════════════════
    # BLOQUE 1: REGISTRO DE CLIENTES (válidos e inválidos)
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("BLOQUE 1 — Registro de Clientes")

    # OP 1: Cliente válido
    registrar_cliente("C001", "Ana Gómez",    "ana.gomez@email.com",    "3101234567")
    # OP 2: Cliente válido
    registrar_cliente("C002", "Luis Martínez","luis.m@empresa.co",      "+57 310 9876543")
    # OP 3: Cliente válido
    registrar_cliente("C003", "Sara Reyes",   "sara.reyes@unad.edu.co", "3209876543")

    # OP 4: Cliente inválido — email malformado
    registrar_cliente("C004", "Error Email",  "correo-sin-arroba",      "3001112222")
    # OP 5: Cliente inválido — nombre muy corto
    registrar_cliente("C005", "AB",           "ab@test.com",            "3001112222")
    # OP 6: Cliente inválido — teléfono incorrecto
    registrar_cliente("C006", "Pedro Pérez",  "pedro@test.com",         "abc")

    # ══════════════════════════════════════════════════════════════════════════
    # BLOQUE 2: CREACIÓN DE SERVICIOS (válidos e inválidos)
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("BLOQUE 2 — Creación de Servicios")

    # OP 7: Sala válida
    try:
        sala_a = ReservaSala("S001", "Sala Innovación", 80_000, capacidad_max=10, tiene_proyector=True)
        registrar_servicio(sala_a)
    except ServicioInvalidoError as e:
        log.error(f"Error creando sala: {e}")

    # OP 8: Sala válida (sin proyector)
    try:
        sala_b = ReservaSala("S002", "Sala Ejecutiva", 60_000, capacidad_max=6, tiene_proyector=False)
        registrar_servicio(sala_b)
    except ServicioInvalidoError as e:
        log.error(f"Error creando sala: {e}")

    # OP 9: Equipo válido
    try:
        laptop = AlquilerEquipo("E001", "Laptop HP ProBook", 25_000, "Laptop", cantidad_disponible=5)
        registrar_servicio(laptop)
    except ServicioInvalidoError as e:
        log.error(f"Error creando equipo: {e}")

    # OP 10: Asesoría válida
    try:
        asesoria_ia = AsesoriaTecnica(
            "A001", "Asesoría en Inteligencia Artificial",
            120_000, "Inteligencia Artificial", "Dr. Carlos Mendoza"
        )
        registrar_servicio(asesoria_ia)
    except ServicioInvalidoError as e:
        log.error(f"Error creando asesoría: {e}")

    # OP 11: Servicio inválido — precio negativo
    try:
        malo = ReservaSala("S003", "Sala Inválida", -5000, capacidad_max=4)
        registrar_servicio(malo)
    except ServicioInvalidoError as e:
        log.error(f"Servicio inválido detectado correctamente → {e}")

    # OP 12: Servicio inválido — capacidad cero
    try:
        malo2 = ReservaSala("S004", "Sala Sin Capacidad", 50_000, capacidad_max=0)
        registrar_servicio(malo2)
    except ServicioInvalidoError as e:
        log.error(f"Servicio inválido detectado correctamente → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # BLOQUE 3: RESERVAS (exitosas y fallidas)
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("BLOQUE 3 — Gestión de Reservas")

    # OP 13: Reserva exitosa — sala con proyector, 2 h, 5 asistentes, 10% descuento
    log.info("OP13: Reserva válida sala con proyector")
    hacer_reserva("C001", "S001", horas=2, descuento=0.10, asistentes=5)

    # OP 14: Reserva exitosa — alquiler de equipo, 3 h, 2 unidades
    log.info("OP14: Reserva válida alquiler de equipo")
    hacer_reserva("C002", "E001", horas=3, cantidad=2)

    # OP 15: Reserva exitosa — asesoría, 4 h, sin descuento
    log.info("OP15: Reserva válida asesoría IA")
    hacer_reserva("C003", "A001", horas=4)

    # OP 16: Reserva fallida — asistentes superan capacidad
    log.info("OP16: Reserva fallida — demasiados asistentes")
    hacer_reserva("C001", "S002", horas=2, asistentes=20)

    # OP 17: Reserva fallida — stock insuficiente de equipos
    log.info("OP17: Reserva fallida — stock insuficiente")
    hacer_reserva("C002", "E001", horas=2, cantidad=99)

    # OP 18: Reserva fallida — asesoría con duración inferior al mínimo
    log.info("OP18: Reserva fallida — duración inferior al mínimo en asesoría")
    hacer_reserva("C003", "A001", horas=0.3)

    # OP 19: Reserva fallida — cliente inexistente
    log.info("OP19: Reserva fallida — cliente no existe")
    hacer_reserva("C999", "S001", horas=1)

    # OP 20: Reserva fallida — horas = 0 (parámetro inválido)
    log.info("OP20: Reserva fallida — horas inválidas")
    hacer_reserva("C001", "S001", horas=0)

    # ══════════════════════════════════════════════════════════════════════════
    # BLOQUE 4: OPERACIÓN NO PERMITIDA — cancelar reserva ya procesada
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("BLOQUE 4 — Operaciones No Permitidas")

    if reservas:
        primera = next(iter(reservas.values()))
        log.info(f"OP21: Intentar cancelar reserva en estado '{primera.estado}'")
        try:
            primera.cancelar()
        except OperacionNoPermitidaError as e:
            log.error(f"Operación bloqueada correctamente → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # BLOQUE 5: CÁLCULO DE COSTOS CON VARIANTES (métodos sobrecargados)
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("BLOQUE 5 — Variantes de Cálculo de Costos")

    if "S001" in servicios:
        sala = servicios["S001"]
        log.info("Comparativa de cálculo de costos para Sala Innovación (3h):")
        try:
            c1 = sala.calcular_costo_total(3)
            log.info(f"  Con IVA (19%):                     ${c1:>12,.2f} COP")
            c2 = sala.calcular_costo_total(3, aplicar_impuesto=False)
            log.info(f"  Sin IVA:                           ${c2:>12,.2f} COP")
            c3 = sala.calcular_costo_total(3, descuento=0.15)
            log.info(f"  Con IVA + 15% descuento:           ${c3:>12,.2f} COP")
            c4 = sala.calcular_costo_total(3, impuesto_personalizado=0.05)
            log.info(f"  Con IVA personalizado (5%):        ${c4:>12,.2f} COP")
        except CalculoCostoError as e:
            log.error(f"Error en cálculo de costos: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════════════════
    log.seccion("RESUMEN FINAL DEL SISTEMA")
    log.info(f"Clientes registrados exitosamente : {len(clientes)}")
    log.info(f"Servicios registrados exitosamente: {len(servicios)}")
    log.info(f"Reservas gestionadas              : {len(reservas)}")

    procesadas = sum(1 for r in reservas.values() if r.estado == "PROCESADA")
    canceladas = sum(1 for r in reservas.values() if r.estado == "CANCELADA")
    log.info(f"  → Procesadas exitosamente       : {procesadas}")
    log.info(f"  → Canceladas / Fallidas         : {canceladas}")
    log.info(f"Log completo guardado en          : sistema_fj.log")
    log.seccion("FIN DE EJECUCIÓN")


if __name__ == "__main__":
    main()
