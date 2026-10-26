"""Desafío Nivel 1 - Búsqueda e historial por patente."""
from almacenamiento import archivos_liquidacion, leer_registros
from validaciones import PATRON_PATENTE, normalizar_patente


def resumir_historial(patente, registros):
    """Devuelve (cantidad_ingresos, total_abonado, promedio_minutos) de la patente."""
    propios = []
    for r in registros:
        if r.get("patente") == patente:
            try:
                propios.append((int(float(r["total_cobrado"])), int(float(r["minutos"]))))
            except (KeyError, ValueError):
                continue  # fila dañada: se ignora
    cantidad = len(propios)
    total = sum(t for t, _ in propios)
    promedio = sum(m for _, m in propios) / cantidad if cantidad else 0
    return cantidad, total, promedio


def consultar_historial():
    patente = normalizar_patente(input("Patente a consultar (AA123BB o ABC123): "))
    if not PATRON_PATENTE.match(patente):
        print("[ERROR] Patente inválida (formatos: AA123BB o ABC123).")
        return
    archivos = archivos_liquidacion()
    if not archivos:
        print("Todavía no hay archivos de liquidación. Procese un lote o registre un cobro primero.")
        return

    cantidad, total, promedio = resumir_historial(patente, leer_registros())
    if cantidad == 0:
        print(f"La patente {patente} no tiene ingresos registrados ({len(archivos)} archivos revisados).")
        return
    print(f"\n--- Historial de {patente} ({len(archivos)} archivos revisados) ---")
    print(f"Ingresos históricos : {cantidad}")
    print(f"Total abonado       : ${total:,}".replace(",", "."))
    print(f"Estadía promedio    : {promedio:.1f} minutos")
