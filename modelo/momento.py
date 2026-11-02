from dataclasses import dataclass
from math import isfinite

from .unidades import (
  SistemaUnidades,
  longitud_a_m,
  momento_a_nm
)


@dataclass
class Momento:
  """
  Momento aplicado directamente sobre el eje.

  Mx, My, Mz se almacenan en N·m.
  """

  nombre: str
  posicion: float

  Mx: float = 0.0
  My: float = 0.0
  Mz: float = 0.0

  @classmethod
  def crear(
    cls,
    nombre,
    posicion,
    sistema,
    Mx=0.0,
    My=0.0,
    Mz=0.0
  ):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),

      Mx=momento_a_nm(Mx, sistema),
      My=momento_a_nm(My, sistema),
      Mz=momento_a_nm(Mz, sistema)
    )

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.posicion,
      self.Mx,
      self.My,
      self.Mz
    )):
      raise ValueError("Los componentes del momento deben ser finitos.")
