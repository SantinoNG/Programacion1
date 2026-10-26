# AutoPark

Sistema de gestión de cobros para un estacionamiento, desarrollado en Python.

## Integrantes

- Gall Santino Nahuel
- Leiva Thiago Guillermo

## Requisitos

- Python 3
- No requiere instalar paquetes externos. Utiliza `sqlite3`, incluido en la biblioteca estándar de Python.

## Ejecución

Desde la carpeta del proyecto, ejecutar:

```bash
python main.py
```

## Opciones del menú

1. Registrar un cobro manual. Se puede escribir `0` en cualquier campo para volver al menú.
2. Procesar los movimientos de `movimientos.json`.
3. Consultar el historial de una patente.
4. Consultar métricas por tipo de vehículo, almacenadas en SQLite.

Las liquidaciones también se guardan en archivos CSV dentro de `salidas/`. La base de datos local se llama `autopark.db`.
