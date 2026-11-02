from dataclasses import dataclass, field
from math import isfinite

from .carga import Carga
from .momento import Momento
from .unidades import longitud_a_m


@dataclass
class Elemento:
  nombre: str
  posicion: float
  ancho: float

  cargas: list[Carga] = field(default_factory=list)
  momentos: list[Momento] = field(default_factory=list)

  def __post_init__(self):
    if not all(isfinite(v) for v in (
      self.posicion,
      self.ancho
    )):
      raise ValueError(
        "La posición y el ancho del elemento deben ser finitos."
      )

  @classmethod
  def crear(cls, nombre, posicion, ancho, sistema):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),
      ancho=longitud_a_m(ancho, sistema)
    )

  @property
  def inicio(self):
    return self.posicion - self.ancho / 2

  @property
  def fin(self):
    return self.posicion + self.ancho / 2

  def agregar_carga(self, carga):
    if not isinstance(carga, Carga):
      raise TypeError(
        "La carga debe ser una instancia de Carga. "
        "Las cargas distribuidas se agregan al eje."
      )

    if not self.inicio <= carga.posicion <= self.fin:
      raise ValueError(
        "El punto de aplicación de la carga "
        "debe estar dentro del elemento."
      )

    self.cargas.append(carga)

  def agregar_momento(self, momento):
    if not isinstance(momento, Momento):
      raise TypeError(
        "El momento debe ser una instancia de Momento."
      )

    if not self.inicio <= momento.posicion <= self.fin:
      raise ValueError(
        "La posición del momento debe estar dentro del elemento."
      )

    self.momentos.append(momento)
