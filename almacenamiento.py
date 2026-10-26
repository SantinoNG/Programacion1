"""Lectura y escritura de los archivos CSV."""
import csv
import glob
import os

from config import ARCHIVO_MANUAL, CAMPOS_CSV, DIR_SALIDAS, PREFIJO_LOTE


def guardar_csv(nombre, filas, campos=CAMPOS_CSV, agregar=False):
    """Escribe filas en salidas/<nombre>. Con agregar=True añade al final."""
    os.makedirs(DIR_SALIDAS, exist_ok=True)
    ruta = os.path.join(DIR_SALIDAS, nombre)
    escribir_encabezado = not (agregar and os.path.exists(ruta))
    with open(ruta, "a" if agregar else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if escribir_encabezado:
            w.writeheader()
        w.writerows(filas)
    return ruta


def archivos_liquidacion():
    """Todos los CSV de cobros: los lotes diarios y los cobros manuales."""
    lotes = sorted(glob.glob(os.path.join(DIR_SALIDAS, PREFIJO_LOTE + "*.csv")))
    manual = os.path.join(DIR_SALIDAS, ARCHIVO_MANUAL)
    return lotes + ([manual] if os.path.exists(manual) else [])


def leer_registros():
    """Consolida todos los CSV de cobros en una sola lista de diccionarios."""
    registros = []
    for ruta in archivos_liquidacion():
        with open(ruta, newline="", encoding="utf-8") as f:
            registros.extend(csv.DictReader(f))
    return registros
