"""Cálculo de tarifas (incluye la función recursiva obligatoria)."""


def calcular_estacionamiento_recursivo(minutos_restantes, tipo_vehiculo, tarifas, cfg):
    """Costo por tramos:
    - caso base: minutos <= 0 -> 0
    - minutos > límite del primer tramo (120): cobra 1 hora y sigue con minutos - 60
    - minutos <= límite: cobra 1 bloque de 30 min y sigue con minutos - 30
    """
    if minutos_restantes <= 0:
        return 0
    t = tarifas[tipo_vehiculo]
    if minutos_restantes > cfg["minutos_limite_primer_tramo"]:
        return t["precio_hora_adicional"] + calcular_estacionamiento_recursivo(
            minutos_restantes - cfg["minutos_hora_adicional"], tipo_vehiculo, tarifas, cfg)
    return t["precio_bloque_30min"] + calcular_estacionamiento_recursivo(
        minutos_restantes - cfg["minutos_bloque_inicial"], tipo_vehiculo, tarifas, cfg)


def liquidar(mov, tarifas, cfg, fecha, origen):
    """Convierte un movimiento validado en una fila lista para el CSV."""
    t = tarifas[mov["tipo_vehiculo"]]
    costo = calcular_estacionamiento_recursivo(mov["minutos"], mov["tipo_vehiculo"], tarifas, cfg)
    if mov["minutos"] >= cfg["minutos_dia_completo"]:
        costo = t["tope_dia"]
    costo = min(costo, t["tope_dia"])
    lavado = t["precio_lavado"] if mov["lavado"] else 0
    return {"id": mov["id"], "fecha": fecha, "patente": mov["patente"],
            "tipo_vehiculo": mov["tipo_vehiculo"], "entrada": mov["entrada"],
            "salida": mov["salida"], "minutos": mov["minutos"],
            "estacionamiento": costo, "lavado": lavado,
            "total_cobrado": costo + lavado, "origen": origen}
