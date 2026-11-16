from dataclasses import dataclass, field
from math import isfinite

from .carga import Carga
from .material import Material
from .momento import Momento
from .unidades import (
  longitud_a_m,
  masa_a_kg
)


@dataclass
class Elemento:
  nombre: str
  posicion: float
  ancho: float

  masa: float | None = None

  usa_chaveta: bool = False
  a: float | None = None
  material_chaveta: Material | None = None
  material_cubo: Material | None = None
  r_f: float | None = None
  n_chaveta: float | None = None

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

    if self.masa is not None:
      if not isfinite(self.masa) or self.masa < 0:
        raise ValueError(
          "La masa del elemento debe ser no negativa y finita."
        )

    if self.a is not None:
      if not isfinite(self.a) or self.a <= 0:
        raise ValueError(
          "El lado de la chaveta debe ser positivo y finito."
        )

    if self.r_f is not None:
      if not isfinite(self.r_f) or self.r_f <= 0:
        raise ValueError(
          "El radio del filo de fondo debe ser positivo y finito."
        )

    if self.n_chaveta is not None:
      if not isfinite(self.n_chaveta) or self.n_chaveta <= 0:
        raise ValueError(
          "El factor de seguridad de la chaveta debe ser "
          "positivo y finito."
        )

    if self.material_chaveta is not None and not isinstance(
      self.material_chaveta, Material
    ):
      raise TypeError(
        "El material de la chaveta debe ser un Material."
      )

    if self.material_cubo is not None and not isinstance(
      self.material_cubo, Material
    ):
      raise TypeError(
        "El material del cubo debe ser un Material."
      )

  @classmethod
  def crear(
    cls,
    nombre,
    posicion,
    ancho,
    sistema,
    masa=None,
    usa_chaveta=False,
    a=None,
    material_chaveta=None,
    material_cubo=None,
    r_f=None,
    n_chaveta=None
  ):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),
      ancho=longitud_a_m(ancho, sistema),
      masa=None if masa is None else masa_a_kg(masa, sistema),
      usa_chaveta=usa_chaveta,
      a=None if a is None else longitud_a_m(a, sistema),
      material_chaveta=material_chaveta,
      material_cubo=material_cubo,
      r_f=None if r_f is None else longitud_a_m(r_f, sistema),
      n_chaveta=n_chaveta
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
