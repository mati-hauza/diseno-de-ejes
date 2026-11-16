from dataclasses import dataclass
from math import isfinite

from .unidades import longitud_a_m


@dataclass
class Escalonamiento:
  """
  Cambio de diámetro con filete de redondeo.

  Solo se informa la posición y el radio del filete. Los diámetros
  mayor y menor se deducen de los tramos adyacentes.

  Internamente:
  - x_s y r están en metros.
  """

  x_s: float
  r: float

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.x_s,
      self.r
    )):
      raise ValueError(
        "La posición y el radio del escalonamiento deben ser "
        "finitos."
      )

  @classmethod
  def crear(cls, x_s, r, sistema):
    return cls(
      x_s=longitud_a_m(x_s, sistema),
      r=longitud_a_m(r, sistema)
    )
