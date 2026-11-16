from enum import Enum


class SistemaUnidades(Enum):
  SI = "SI"
  INGLES = "INGLES"


def validar_sistema(sistema):
  """Comprueba que el sistema de unidades sea válido."""
  if not isinstance(sistema, SistemaUnidades):
    raise TypeError(
      "El sistema de unidades debe ser una instancia de "
      "SistemaUnidades."
    )


def longitud_a_m(valor, sistema):
  """Convierte mm o in a metros."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor / 1000

  return valor * 0.0254


def longitud_desde_m(valor, sistema):
  """Convierte metros a mm o in."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor * 1000

  return valor / 0.0254


def fuerza_a_n(valor, sistema):
  """Convierte N o lbf a Newtons."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor * 4.448221615


def fuerza_desde_n(valor, sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor / 4.448221615


def momento_a_nm(valor, sistema):
  """Convierte N·mm o lbf·in a N·m."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor / 1000

  return valor * 0.112984829


def momento_desde_nm(valor, sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor * 1000

  return valor / 0.112984829


def masa_a_kg(valor, sistema):
  """Convierte kg o lb a kilogramos."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor * 0.45359237


def masa_desde_kg(valor, sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor / 0.45359237


def temperatura_a_c(valor, sistema):
  """Convierte °C o °F a grados Celsius."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return (valor - 32.0) * 5.0 / 9.0


def temperatura_desde_c(valor, sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor * 9.0 / 5.0 + 32.0


# Factores de conversión constantes.
PSI_A_PA = 6894.757293168361
LB_IN3_A_KG_M3 = 27679.904710191


def presion_a_pa(valor, sistema):
  """Convierte MPa o ksi a Pascales."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor * 1e6

  return valor * PSI_A_PA * 1000


def presion_desde_pa(valor, sistema):
  """Convierte Pascales a MPa o ksi."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor / 1e6

  return valor / (PSI_A_PA * 1000)


def modulo_a_pa(valor, sistema):
  """Convierte GPa o Mpsi a Pascales."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor * 1e9

  return valor * PSI_A_PA * 1e6


def modulo_desde_pa(valor, sistema):
  """Convierte Pascales a GPa o Mpsi."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor / 1e9

  return valor / (PSI_A_PA * 1e6)


def densidad_a_kg_m3(valor, sistema):
  """Convierte kg/m³ o lb/in³ a kg/m³."""
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor * LB_IN3_A_KG_M3


def densidad_desde_kg_m3(valor, sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return valor

  return valor / LB_IN3_A_KG_M3


def obtener_unidades(sistema):
  validar_sistema(sistema)

  if sistema == SistemaUnidades.SI:
    return {
      "longitud": "mm",
      "fuerza": "N",
      "momento": "N·mm",
      "presion": "MPa",
      "modulo": "GPa",
      "densidad": "kg/m³"
    }

  return {
    "longitud": "in",
    "fuerza": "lbf",
    "momento": "lbf·in",
    "presion": "ksi",
    "modulo": "Mpsi",
    "densidad": "lb/in³"
  }
