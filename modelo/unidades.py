from enum import Enum


class SistemaUnidades(Enum):
  SI = "SI"
  INGLES = "INGLES"


def longitud_a_m(valor, sistema):
  """Convierte mm o in a metros."""
  if sistema == SistemaUnidades.SI:
    return valor / 1000

  return valor * 0.0254


def longitud_desde_m(valor, sistema):
  """Convierte metros a mm o in."""
  if sistema == SistemaUnidades.SI:
    return valor * 1000

  return valor / 0.0254


def fuerza_a_n(valor, sistema):
  """Convierte N o lbf a Newtons."""
  if sistema == SistemaUnidades.SI:
    return valor

  return valor * 4.448221615


def fuerza_desde_n(valor, sistema):
  if sistema == SistemaUnidades.SI:
    return valor

  return valor / 4.448221615


def momento_a_nm(valor, sistema):
  """Convierte N·mm o lbf·in a N·m."""
  if sistema == SistemaUnidades.SI:
    return valor / 1000

  return valor * 0.112984829


def momento_desde_nm(valor, sistema):
  if sistema == SistemaUnidades.SI:
    return valor * 1000

  return valor / 0.112984829


def obtener_unidades(sistema):
  if sistema == SistemaUnidades.SI:
    return {
      "longitud": "mm",
      "fuerza": "N",
      "momento": "N·mm"
    }

  return {
    "longitud": "in",
    "fuerza": "lbf",
    "momento": "lbf·in"
  }
