"""Rutas, campos de los CSV y carga de archivos JSON."""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_TARIFAS = os.path.join(BASE, "tarifas.json")
RUTA_MOVIMIENTOS = os.path.join(BASE, "movimientos.json")
DIR_SALIDAS = os.path.join(BASE, "salidas")

ARCHIVO_MANUAL = "cobros_manuales.csv"
PREFIJO_LOTE = "liquidacion_"  # liquidacion_<fecha>.csv

CAMPOS_CSV = ["id", "fecha", "patente", "tipo_vehiculo", "entrada", "salida",
              "minutos", "estacionamiento", "lavado", "total_cobrado", "origen"]


def cargar_json(ruta):
    """Devuelve el contenido del JSON o None si no existe / está mal formado."""
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {ruta}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON mal formado en {ruta}: {e}")
    return None
