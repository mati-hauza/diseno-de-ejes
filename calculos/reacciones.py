import numpy as np

from .transformaciones import (
  Accion,
  obtener_acciones_externas
)

from modelo.unidades import (
  momento_desde_nm,
  obtener_unidades
)


def calcular_reacciones(eje, acciones=None):
  """
  Calcula las reacciones de los dos apoyos.

  Devuelve:
  - Lista de acciones de reacción.
  - Lista de advertencias de equilibrio.
  """

  if acciones is None:
    acciones = obtener_acciones_externas(eje)

  if len(eje.apoyos) != 2:
    raise ValueError("Se necesitan exactamente dos apoyos.")

  apoyo_a, apoyo_b = eje.apoyos

  xa = apoyo_a.posicion
  xb = apoyo_b.posicion

  if np.isclose(xa, xb):
    raise ValueError(
      "Los centros de los apoyos no pueden coincidir."
    )

  # Sumas de fuerzas externas.
  suma_fx = sum(a.Fx for a in acciones)
  suma_fy = sum(a.Fy for a in acciones)
  suma_fz = sum(a.Fz for a in acciones)

  # Momentos externos respecto al origen.
  # Se incluyen los momentos equivalentes de las fuerzas.
  suma_my = sum(-a.posicion * a.Fz + a.My for a in acciones)
  suma_mz = sum(a.posicion * a.Fy + a.Mz for a in acciones)
  suma_mx = sum(a.Mx for a in acciones)

  # Reacción axial: solamente el apoyo fijo la genera.
  reacciones_axiales = {}

  for apoyo in eje.apoyos:
    if apoyo.fijo_axial:
      reacciones_axiales[apoyo.nombre] = -suma_fx

  # Reacciones verticales.
  matriz_y = np.array([
    [1.0, 1.0],
    [xa, xb]
  ])

  vector_y = np.array([
    -suma_fy,
    -suma_mz
  ])

  ray, rby = np.linalg.solve(matriz_y, vector_y)

  # Reacciones horizontales.
  matriz_z = np.array([
    [1.0, 1.0],
    [xa, xb]
  ])

  vector_z = np.array([
    -suma_fz,
    suma_my
  ])

  raz, rbz = np.linalg.solve(matriz_z, vector_z)

  # Organizar las reacciones.
  valores = {
    apoyo_a.nombre: {
      "Fx": reacciones_axiales.get(apoyo_a.nombre, 0.0),
      "Fy": ray,
      "Fz": raz
    },

    apoyo_b.nombre: {
      "Fx": reacciones_axiales.get(apoyo_b.nombre, 0.0),
      "Fy": rby,
      "Fz": rbz
    }
  }

  reacciones = []

  for apoyo in eje.apoyos:
    r = valores[apoyo.nombre]

    reacciones.append(
      Accion(
        nombre=f"Reacción {apoyo.nombre}",
        posicion=apoyo.posicion,
        Fx=r["Fx"],
        Fy=r["Fy"],
        Fz=r["Fz"]
      )
    )

  # Comprobar equilibrio torsional.
  advertencias = []

  if not np.isclose(suma_mx, 0.0, atol=1e-8, rtol=1e-9):
    momento_resultante = momento_desde_nm(
      suma_mx,
      eje.sistema
    )

    unidad = obtener_unidades(eje.sistema)["momento"]

    advertencias.append(
      "El sistema no está en equilibrio torsional. "
      "Los apoyos definidos no pueden absorber el momento "
      f"torsor resultante ({momento_resultante:.6g} {unidad})."
    )

  return reacciones, advertencias
