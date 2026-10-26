"""AutoPark - menú principal."""
from datetime import date, datetime

from almacenamiento import guardar_csv, leer_registros
from base_datos import (consultar_metricas, guardar_liquidaciones, guardar_tarifas,
                        migrar_csv_a_sqlite)
from calculos import liquidar
from config import (ARCHIVO_MANUAL, PREFIJO_LOTE, RUTA_MOVIMIENTOS,
                    RUTA_TARIFAS, cargar_json)
from historial import consultar_historial
from validaciones import validar_movimiento


def dinero(n):
    return f"${n:,}".replace(",", ".")


def cargar_tarifas():
    datos = cargar_json(RUTA_TARIFAS)
    if not datos or "configuracion" not in datos or "tarifas" not in datos:
        print("[ERROR] tarifas.json inválido o incompleto.")
        return None, None
    guardar_tarifas(datos["tarifas"])
    return datos["configuracion"], datos["tarifas"]


def pedir_dato_cobro(mensaje):
    """Solicita un dato; permite cancelar el cobro escribiendo 0."""
    valor = input(f"{mensaje} (0 para volver al menú): ").strip()
    return None if valor == "0" else valor


def cobro_manual():
    cfg, tarifas = cargar_tarifas()
    if not tarifas:
        return
    print(f"Tipos disponibles: {', '.join(tarifas)}")
    while True:
        patente = pedir_dato_cobro("Patente (AA123BB o ABC123, sin espacios)")
        if patente is None:
            print("Cobro cancelado. Volviendo al menú principal.")
            return
        tipo = pedir_dato_cobro("Tipo de vehículo")
        if tipo is None:
            print("Cobro cancelado. Volviendo al menú principal.")
            return
        entrada = pedir_dato_cobro("Hora de entrada (HH:MM)")
        if entrada is None:
            print("Cobro cancelado. Volviendo al menú principal.")
            return
        salida = pedir_dato_cobro("Hora de salida (HH:MM)")
        if salida is None:
            print("Cobro cancelado. Volviendo al menú principal.")
            return
        lavado = pedir_dato_cobro("¿Lavado? (s/n)")
        if lavado is None:
            print("Cobro cancelado. Volviendo al menú principal.")
            return
        mov = {"id": "MAN-" + datetime.now().strftime("%Y%m%d%H%M%S"),
               "patente": patente, "tipo_vehiculo": tipo,
               "entrada": entrada, "salida": salida,
               "solicito_lavado": lavado.lower() in ("s", "si", "sí")}
        limpio, error = validar_movimiento(mov, tarifas)
        if not error:
            break
        print(f"[ERROR] {error}. Intente de nuevo.\n")
    fila = liquidar(limpio, tarifas, cfg, date.today().isoformat(), "manual")
    guardar_csv(ARCHIVO_MANUAL, [fila], agregar=True)
    guardar_liquidaciones([fila])
    print(f"Estacionamiento {dinero(fila['estacionamiento'])} + lavado {dinero(fila['lavado'])} "
          f"= TOTAL {dinero(fila['total_cobrado'])}")


def procesar_lote():
    cfg, tarifas = cargar_tarifas()
    datos = cargar_json(RUTA_MOVIMIENTOS)
    if not tarifas or datos is None:
        return
    movimientos = datos.get("movimientos") if isinstance(datos, dict) else None
    if not isinstance(movimientos, list):
        print("[ERROR] movimientos.json debe tener una lista 'movimientos'.")
        return
    try:
        fecha = datetime.strptime(str(datos.get("fecha_operacion")), "%Y-%m-%d").date().isoformat()
    except ValueError:
        fecha = date.today().isoformat()
        print(f"[AVISO] fecha_operacion inválida; se usa {fecha}.")

    liquidados, rechazados, ids_vistos = [], [], set()
    for i, mov in enumerate(movimientos, 1):
        limpio, error = validar_movimiento(mov, tarifas)
        if not error and limpio["id"] in ids_vistos:
            error = "id duplicado"
        if error:
            id_mov = mov.get("id", f"#{i}") if isinstance(mov, dict) else f"#{i}"
            rechazados.append({"id": id_mov, "motivo": error})
            continue
        ids_vistos.add(limpio["id"])
        liquidados.append(liquidar(limpio, tarifas, cfg, fecha, "lote"))

    guardar_csv(f"{PREFIJO_LOTE}{fecha}.csv", liquidados)
    guardar_liquidaciones(liquidados)
    if rechazados:
        guardar_csv(f"rechazados_{fecha}.csv", rechazados, campos=["id", "motivo"])

    print(f"\nLote {fecha}: {len(liquidados)} liquidados, {len(rechazados)} rechazados.")
    for r in rechazados:
        print(f"  - {r['id']}: {r['motivo']}")
    print(f"Total recaudado: {dinero(sum(f['total_cobrado'] for f in liquidados))}")


def mostrar_metricas_sql():
    """Migra liquidaciones históricas y muestra el resumen calculado por SQL."""
    migrar_csv_a_sqlite(leer_registros())
    filas = consultar_metricas()
    if not filas:
        print("Todavía no hay liquidaciones para consultar.")
        return
    print("\n--- Métricas por tipo de vehículo (SQLite) ---")
    for fila in filas:
        print(f"{fila['tipo_vehiculo'].capitalize():12} | operaciones: {fila['cantidad']:>3} | "
              f"recaudación: {dinero(round(fila['recaudacion'] or 0))} | "
              f"estadía promedio: {fila['promedio_minutos']:.1f} min")


def menu():
    opciones = {"1": cobro_manual, "2": procesar_lote, "3": consultar_historial,
                "4": mostrar_metricas_sql}
    while True:
        print("\n=== AUTOPARK ===\n1. Cobro manual\n2. Procesar lote (movimientos.json)\n"
              "3. Historial por patente\n4. Métricas por tipo (SQLite)\n0. Salir")
        op = input("Opción: ").strip()
        if op == "0":
            break
        opciones.get(op, lambda: print("Opción inválida."))()


if __name__ == "__main__":
    menu()