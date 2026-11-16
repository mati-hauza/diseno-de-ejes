from math import isclose

from modelo.unidades import (
  momento_desde_nm,
  obtener_unidades
)

from .transformaciones import obtener_acciones_externas


def validar_entradas(eje):
  """
  Valida la estructura del eje y el equilibrio torsional global.

  Devuelve las acciones externas equivalentes para reutilizarlas en
  las etapas siguientes, de modo que las cargas se transformen una
  sola vez.
  """
  eje.validar()

  acciones = obtener_acciones_externas(eje)

  suma_mx = sum(a.Mx for a in acciones)

  if not isclose(suma_mx, 0.0, abs_tol=1e-8, rel_tol=1e-9):
    momento_resultante = momento_desde_nm(
      suma_mx,
      eje.sistema
    )

    unidad = obtener_unidades(eje.sistema)["momento"]

    raise ValueError(
      "El sistema no está en equilibrio torsional. "
      "Los apoyos no pueden absorber el momento torsor "
      f"resultante ({momento_resultante:.6g} {unidad})."
    )

  return acciones
