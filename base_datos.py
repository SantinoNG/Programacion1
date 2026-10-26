"""Persistencia relacional de AutoPark usando la biblioteca sqlite3."""
import sqlite3
import os
from contextlib import contextmanager

from config import BASE

RUTA_BASE_DATOS = os.path.join(BASE, "autopark.db")


def conectar():
    """Abre la base y garantiza que existan las tablas del sistema."""
    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    with conexion:
        conexion.execute("""CREATE TABLE IF NOT EXISTS liquidaciones (
            id TEXT PRIMARY KEY, fecha TEXT NOT NULL, patente TEXT NOT NULL,
            tipo_vehiculo TEXT NOT NULL, entrada TEXT NOT NULL, salida TEXT NOT NULL,
            minutos INTEGER NOT NULL, estacionamiento REAL NOT NULL, lavado REAL NOT NULL,
            total_cobrado REAL NOT NULL, origen TEXT NOT NULL)""")
        conexion.execute("""CREATE TABLE IF NOT EXISTS tarifas (
            tipo_vehiculo TEXT PRIMARY KEY, precio_bloque_30min REAL NOT NULL,
            precio_hora_adicional REAL NOT NULL, tope_dia REAL NOT NULL,
            precio_lavado REAL NOT NULL)""")
    return conexion


@contextmanager
def sesion():
    """Administra commit/rollback y cierre de una conexión."""
    db = conectar()
    try:
        with db:
            yield db
    finally:
        db.close()


def guardar_liquidaciones(filas):
    """Inserta o actualiza las liquidaciones recibidas (id es único)."""
    if not filas:
        return
    with sesion() as db:
        db.executemany("""INSERT INTO liquidaciones VALUES
            (:id, :fecha, :patente, :tipo_vehiculo, :entrada, :salida,
             :minutos, :estacionamiento, :lavado, :total_cobrado, :origen)
            ON CONFLICT(id) DO UPDATE SET fecha=excluded.fecha, patente=excluded.patente,
            tipo_vehiculo=excluded.tipo_vehiculo, entrada=excluded.entrada,
            salida=excluded.salida, minutos=excluded.minutos,
            estacionamiento=excluded.estacionamiento, lavado=excluded.lavado,
            total_cobrado=excluded.total_cobrado, origen=excluded.origen""", filas)


def guardar_tarifas(tarifas):
    """Sincroniza el tarifario JSON con su tabla relacional."""
    filas = [{"tipo_vehiculo": tipo, **valores} for tipo, valores in tarifas.items()]
    with sesion() as db:
        db.executemany("""INSERT INTO tarifas VALUES
            (:tipo_vehiculo, :precio_bloque_30min, :precio_hora_adicional,
             :tope_dia, :precio_lavado)
            ON CONFLICT(tipo_vehiculo) DO UPDATE SET
            precio_bloque_30min=excluded.precio_bloque_30min,
            precio_hora_adicional=excluded.precio_hora_adicional,
            tope_dia=excluded.tope_dia, precio_lavado=excluded.precio_lavado""", filas)


def migrar_csv_a_sqlite(registros):
    """Migra a SQLite filas CSV previamente generadas y validadas."""
    filas = []
    for registro in registros:
        try:
            fila = dict(registro)
            for campo in ("minutos", "estacionamiento", "lavado", "total_cobrado"):
                fila[campo] = float(fila[campo]) if campo != "minutos" else int(float(fila[campo]))
            filas.append(fila)
        except (KeyError, TypeError, ValueError):
            continue
    guardar_liquidaciones(filas)


def consultar_metricas():
    """Devuelve conteo, recaudación y promedio de estadía agrupados por tipo."""
    with sesion() as db:
        return db.execute("""SELECT tipo_vehiculo, COUNT(*) AS cantidad,
            SUM(total_cobrado) AS recaudacion, AVG(minutos) AS promedio_minutos
            FROM liquidaciones GROUP BY tipo_vehiculo ORDER BY tipo_vehiculo""").fetchall()
