from math import isclose


def ranura_en(eje, posicion, lado=0):
  """
  Devuelve la ranura con geometría activa en la posición indicada.
  """
  tolerancia = 1e-9 * max(eje.longitud, 1.0)

  for ranura in eje.ranuras:
    if not ranura.con_geometria:
      continue

    if (
      ranura.inicio + tolerancia < posicion < ranura.fin - tolerancia
    ):
      return ranura

    if abs(posicion - ranura.inicio) <= tolerancia and lado > 0:
      return ranura

    if abs(posicion - ranura.fin) <= tolerancia and lado < 0:
      return ranura

  return None


def diametro_local(eje, posicion, lado=0):
  """
  Diámetro local considerando tramos y ranuras con geometría.
  """
  d = eje.diametro_local(posicion, lado)

  ranura = ranura_en(eje, posicion, lado)

  if ranura is not None:
    tramo = eje.tramo_en(ranura.posicion)
    return tramo.d - 2 * ranura.profundidad

  return d


def segmento_continuo(eje, posicion):
  """
  Devuelve (inicio, fin) del intervalo continuo de diámetro que
  contiene la posición.
  """
  tramo = eje.tramo_en(posicion)

  if tramo is None:
    return None

  inicio = tramo.x_inicio
  fin = tramo.x_fin

  for ranura in eje.ranuras:
    if not ranura.con_geometria:
      continue

    if ranura.inicio <= posicion <= ranura.fin:
      inicio = max(inicio, ranura.inicio)
      fin = min(fin, ranura.fin)

  return inicio, fin


def posiciones_de_tramos(eje):
  posiciones = set()

  for tramo in eje.tramos:
    posiciones.add(tramo.x_inicio)
    posiciones.add(tramo.x_fin)

  return sorted(posiciones)


def adyacentes(a, b, tolerancia=1e-9):
  return isclose(a, b, abs_tol=tolerancia)
