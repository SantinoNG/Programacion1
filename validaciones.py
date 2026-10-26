"""Normalización y validación de los datos de entrada."""
import re

PATRON_PATENTE = re.compile(r"^([A-Z]{2}\d{3}[A-Z]{2}|[A-Z]{3}\d{3})$")  # AA123BB o ABC123
PATRON_HORA = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
CAMPOS_OBLIGATORIOS = ("id", "patente", "tipo_vehiculo", "entrada", "salida", "solicito_lavado")


def normalizar_patente(valor):
    """' bf 901 gg ' -> 'BF901GG'."""
    return "".join(str(valor).split()).upper()


def hora_a_minutos(valor):
    """'08:25' -> 505. Devuelve None si el formato no es HH:MM válido."""
    if not isinstance(valor, str):
        return None
    m = PATRON_HORA.match(valor.strip())
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None


def validar_movimiento(mov, tipos_validos):
    """Devuelve (movimiento_limpio, None) o (None, motivo_de_rechazo)."""
    if not isinstance(mov, dict):
        return None, "registro con formato inválido"
    faltan = [c for c in CAMPOS_OBLIGATORIOS if c not in mov]
    if faltan:
        return None, "faltan campos: " + ", ".join(faltan)

    patente = normalizar_patente(mov["patente"])
    if not PATRON_PATENTE.match(patente):
        return None, f"patente inválida ({mov['patente']!r})"

    tipo = str(mov["tipo_vehiculo"]).strip().lower()
    if tipo not in tipos_validos:
        return None, f"tipo de vehículo no reconocido ({mov['tipo_vehiculo']!r})"

    entrada, salida = hora_a_minutos(mov["entrada"]), hora_a_minutos(mov["salida"])
    if entrada is None or salida is None:
        return None, "hora con formato inválido (se espera HH:MM)"
    if salida <= entrada:
        return None, "la salida no es posterior a la entrada"

    if not isinstance(mov["solicito_lavado"], bool):
        return None, "solicito_lavado debe ser true/false"

    return {"id": str(mov["id"]).strip(), "patente": patente, "tipo_vehiculo": tipo,
            "entrada": mov["entrada"].strip(), "salida": mov["salida"].strip(),
            "minutos": salida - entrada, "lavado": mov["solicito_lavado"]}, None
