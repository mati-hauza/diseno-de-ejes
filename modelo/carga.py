from dataclasses import dataclass
from math import isfinite

from .unidades import (
  longitud_a_m,
  fuerza_a_n
)


@dataclass
class Carga:
  """
  Clase base para las cargas aplicadas sobre el eje.

  El punto de aplicación se define mediante:
  - posicion: coordenada longitudinal X, en metros.
  - radio_aplicacion: distancia radial, en metros.
  - angulo_aplicacion: ángulo en grados.
  """

  nombre: str
  posicion: float
  radio_aplicacion: float
  angulo_aplicacion: float

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.posicion,
      self.radio_aplicacion,
      self.angulo_aplicacion
    )):
      raise ValueError(
        "Los datos del punto de aplicación deben ser finitos."
      )

    if self.radio_aplicacion < 0:
      raise ValueError(
        "El radio de aplicación no puede ser negativo."
      )


@dataclass
class CargaCartesiana(Carga):
  """
  Carga definida mediante componentes cartesianas.

  Fx, Fy, Fz se almacenan en Newtons.
  """

  Fx: float = 0.0
  Fy: float = 0.0
  Fz: float = 0.0

  @classmethod
  def crear(
    cls,
    nombre,
    posicion,
    sistema,
    radio_aplicacion=0.0,
    angulo_aplicacion=0.0,
    Fx=0.0,
    Fy=0.0,
    Fz=0.0
  ):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),
      radio_aplicacion=longitud_a_m(
        radio_aplicacion, sistema
      ),
      angulo_aplicacion=angulo_aplicacion,

      Fx=fuerza_a_n(Fx, sistema),
      Fy=fuerza_a_n(Fy, sistema),
      Fz=fuerza_a_n(Fz, sistema)
    )
    
  def __post_init__(self):
    super().__post_init__()

    if not all(isfinite(v) for v in (
      self.Fx,
      self.Fy,
      self.Fz
    )):
      raise ValueError(
        "Las componentes de la fuerza deben ser finitas."
      )


@dataclass
class CargaCilindrica(Carga):
  """
  Carga definida mediante componentes cilíndricas.

  F_axial, F_radial y F_tangencial se almacenan en Newtons.
  """

  F_axial: float = 0.0
  F_radial: float = 0.0
  F_tangencial: float = 0.0

  @classmethod
  def crear(
    cls,
    nombre,
    posicion,
    sistema,
    radio_aplicacion=0.0,
    angulo_aplicacion=0.0,
    axial=0.0,
    radial=0.0,
    tangencial=0.0
  ):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),
      radio_aplicacion=longitud_a_m(radio_aplicacion, sistema),
      angulo_aplicacion=angulo_aplicacion,

      F_axial=fuerza_a_n(axial, sistema),
      F_radial=fuerza_a_n(radial, sistema),
      F_tangencial=fuerza_a_n(tangencial, sistema)
    )
    
  def __post_init__(self):
    super().__post_init__()

    if not all(isfinite(v) for v in (
      self.F_axial,
      self.F_radial,
      self.F_tangencial
    )):
      raise ValueError(
        "Las componentes de la fuerza deben ser finitas."
      )


@dataclass
class CargaDistribuida:
  """
  Carga distribuida uniforme sobre un intervalo [inicio, fin].

  qx, qy, qz se almacenan en N/m.

  La carga se aplica sobre el eje central y no genera
  momentos adicionales por excentricidad.
  """

  nombre: str
  inicio: float
  fin: float

  qx: float = 0.0
  qy: float = 0.0
  qz: float = 0.0

  @classmethod
  def crear(
    cls,
    nombre,
    inicio,
    fin,
    sistema,
    qx=0.0,
    qy=0.0,
    qz=0.0
  ):
    longitud_unidad_m = longitud_a_m(1.0, sistema)

    return cls(
      nombre=nombre,

      inicio=longitud_a_m(inicio, sistema),
      fin=longitud_a_m(fin, sistema),

      qx=fuerza_a_n(qx, sistema) / longitud_unidad_m,
      qy=fuerza_a_n(qy, sistema) / longitud_unidad_m,
      qz=fuerza_a_n(qz, sistema) / longitud_unidad_m
    )

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.inicio,
      self.fin,
      self.qx,
      self.qy,
      self.qz
    )):
      raise ValueError(
        "Los datos de la carga distribuida deben ser finitos."
      )

    if self.fin <= self.inicio:
      raise ValueError(
        "El final de la carga distribuida debe ser mayor que el inicio."
      )
    
    if self.inicio < 0:
      raise ValueError(
        "El inicio de la carga distribuida no puede ser negativo."
      )