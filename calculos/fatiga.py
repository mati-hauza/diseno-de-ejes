from math import inf


def goodman_modificado(esfuerzos, material, Se):
  """
  Factor de seguridad por Goodman modificado.

  Interfaz del registro de criterios: recibe el estado de
  esfuerzos, el material y el límite de fatiga corregido.
  """
  if Se <= 0 or material.Sut <= 0:
    raise ValueError(
      "El punto no es verificable: Se y Sut deben ser positivos."
    )

  denominador = (
    esfuerzos.sigma_prima_a / Se
    + esfuerzos.sigma_prima_m / material.Sut
  )

  if denominador <= 0:
    return inf

  return 1.0 / denominador
