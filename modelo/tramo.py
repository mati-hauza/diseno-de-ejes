from dataclasses import dataclass
from math import isfinite

from .unidades import longitud_a_m


@dataclass
class Tramo:
  """
  Tramo cilíndrico de diámetro constante.

  Internamente:
  - x_inicio, x_fin y d están en metros.
  """

  x_inicio: float
  x_fin: float
  d: float

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.x_inicio,
      self.x_fin,
      self.d
    )):
      raise ValueError(
        "Las dimensiones del tramo deben ser finitas."
      )

  @classmethod
  def crear(cls, x_inicio, x_fin, d, sistema):
    return cls(
      x_inicio=longitud_a_m(x_inicio, sistema),
      x_fin=longitud_a_m(x_fin, sistema),
      d=longitud_a_m(d, sistema)
    )

  @property
  def longitud(self):
    return self.x_fin - self.x_inicio

  def contiene(self, posicion, tolerancia=0.0):
    return (
      self.x_inicio - tolerancia
      <= posicion
      <= self.x_fin + tolerancia
    )
