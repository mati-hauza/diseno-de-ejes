from dataclasses import dataclass

from .unidades import (
  SistemaUnidades,
  longitud_a_m
)


@dataclass
class Apoyo:
  nombre: str
  posicion: float
  ancho: float
  fijo_axial: bool

  @classmethod
  def crear(cls, nombre, posicion, ancho, fijo_axial, sistema):
    return cls(
      nombre=nombre,
      posicion=longitud_a_m(posicion, sistema),
      ancho=longitud_a_m(ancho, sistema),
      fijo_axial=fijo_axial
    )

  @property
  def inicio(self):
    return self.posicion - self.ancho / 2

  @property
  def fin(self):
    return self.posicion + self.ancho / 2
