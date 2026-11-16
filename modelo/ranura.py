from dataclasses import dataclass
from math import isfinite

from .unidades import longitud_a_m


@dataclass
class Ranura:
  """
  Ranura para anillo de retención.

  La geometría es opcional. Si se informa, deben estar los tres
  valores: ancho, profundidad y radio.

  Internamente:
  - posicion, ancho, profundidad y radio están en metros.
  """

  posicion: float
  ancho: float | None = None
  profundidad: float | None = None
  radio: float | None = None

  def __post_init__(self):
    if not isfinite(self.posicion):
      raise ValueError(
        "La posición de la ranura debe ser finita."
      )

    valores = (self.ancho, self.profundidad, self.radio)
    informados = [v is not None for v in valores]

    if any(informados) and not all(informados):
      raise ValueError(
        "Si se informa la geometría de la ranura, deben estar "
        "el ancho, la profundidad y el radio."
      )

    if all(informados) and not all(
      isfinite(v) for v in valores
    ):
      raise ValueError(
        "Las dimensiones de la ranura deben ser finitas."
      )

  @classmethod
  def crear(
    cls,
    posicion,
    sistema,
    ancho=None,
    profundidad=None,
    radio=None
  ):
    def convertir(valor):
      if valor is None:
        return None
      return longitud_a_m(valor, sistema)

    return cls(
      posicion=longitud_a_m(posicion, sistema),
      ancho=convertir(ancho),
      profundidad=convertir(profundidad),
      radio=convertir(radio)
    )

  @property
  def con_geometria(self):
    return (
      self.ancho is not None
      and self.profundidad is not None
      and self.radio is not None
    )

  @property
  def inicio(self):
    if not self.con_geometria:
      return self.posicion
    return self.posicion - self.ancho / 2

  @property
  def fin(self):
    if not self.con_geometria:
      return self.posicion
    return self.posicion + self.ancho / 2
