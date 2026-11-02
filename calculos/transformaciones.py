from dataclasses import dataclass
from math import radians, sin, cos

from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)


@dataclass
class Accion:
  """
  Acción equivalente aplicada en una posición longitudinal.

  Todas las magnitudes están en unidades SI:
  - Fuerzas: N
  - Momentos: N·m
  - Posición: m
  """

  nombre: str
  posicion: float

  Fx: float = 0.0
  Fy: float = 0.0
  Fz: float = 0.0

  Mx: float = 0.0
  My: float = 0.0
  Mz: float = 0.0


def transformar_carga(carga):
  """
  Transforma una carga puntual a una acción equivalente
  aplicada sobre el eje central.
  """

  if isinstance(carga, CargaCartesiana):
    Fx = carga.Fx
    Fy = carga.Fy
    Fz = carga.Fz

  elif isinstance(carga, CargaCilindrica):
    theta = radians(carga.angulo_aplicacion)

    Fx = carga.F_axial

    Fy = (
      carga.F_radial * cos(theta)
      - carga.F_tangencial * sin(theta)
    )

    Fz = (
      carga.F_radial * sin(theta)
      + carga.F_tangencial * cos(theta)
    )

  else:
    raise TypeError(
      f"Tipo de carga no reconocido: {type(carga).__name__}"
    )

  # Coordenadas del punto de aplicación respecto al eje central.
  radio = carga.radio_aplicacion
  theta = radians(carga.angulo_aplicacion)

  ry = radio * cos(theta)
  rz = radio * sin(theta)

  # Producto vectorial r x F.
  Mx = ry * Fz - rz * Fy
  My = rz * Fx
  Mz = -ry * Fx

  return Accion(
    nombre=carga.nombre,
    posicion=carga.posicion,

    Fx=Fx,
    Fy=Fy,
    Fz=Fz,

    Mx=Mx,
    My=My,
    Mz=Mz
  )


def transformar_momento(momento):
  """
  Convierte un momento definido directamente
  en una acción equivalente sobre el eje.
  """

  return Accion(
    nombre=momento.nombre,
    posicion=momento.posicion,

    Mx=momento.Mx,
    My=momento.My,
    Mz=momento.Mz
  )


def obtener_acciones_puntuales(eje):
  """
  Obtiene las acciones puntuales del eje.

  Incluye:
  - Cargas independientes.
  - Cargas de elementos.
  - Momentos independientes.
  - Momentos de elementos.
  """

  acciones = []

  for carga in eje.obtener_todas_las_cargas():
    acciones.append(transformar_carga(carga))

  for momento in eje.obtener_todos_los_momentos():
    acciones.append(transformar_momento(momento))

  return acciones


def transformar_carga_distribuida(carga):
  """
  Sustituye una carga distribuida uniforme por su resultante.

  La resultante se encuentra en el centro del intervalo.
  """

  longitud = carga.fin - carga.inicio

  return Accion(
    nombre=carga.nombre,
    posicion=(carga.inicio + carga.fin) / 2,

    Fx=carga.qx * longitud,
    Fy=carga.qy * longitud,
    Fz=carga.qz * longitud
  )


def obtener_acciones_externas(eje):
  """
  Obtiene todas las acciones equivalentes del eje.

  Las cargas distribuidas se convierten en resultantes
  para el cálculo del equilibrio global.
  """

  acciones = obtener_acciones_puntuales(eje)

  for carga in eje.obtener_todas_las_cargas_distribuidas():
    acciones.append(
      transformar_carga_distribuida(carga)
    )

  return acciones