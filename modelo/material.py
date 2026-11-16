from dataclasses import dataclass
from math import isfinite

from .unidades import (
  densidad_a_kg_m3,
  modulo_a_pa,
  presion_a_pa,
  temperatura_a_c
)

ACABADOS_VALIDOS = (
  "esmerilado",
  "maquinado",
  "laminado_caliente",
  "forja"
)


@dataclass
class Material:
  """
  Propiedades mecánicas de un material.

  Internamente se almacenan en SI:
  - Sut: resistencia última a la tensión, en Pa.
  - Sy: esfuerzo de fluencia, en Pa.
  - E: módulo de elasticidad, en Pa (opcional, no se usa).
  - G: módulo de rigidez, en Pa (opcional, no se usa).
  - densidad: densidad másica, en kg/m³ (opcional, no se usa).
  - temperatura: temperatura de funcionamiento, en °C.
  """

  nombre: str
  Sut: float
  Sy: float
  E: float | None = None
  G: float | None = None
  densidad: float | None = None

  acabado: str = "maquinado"
  temperatura: float = 20.0
  confiabilidad: float = 0.5
  k_f_marin: float = 1.0

  def __post_init__(self):
    if not self.nombre:
      raise ValueError(
        "El material debe tener un nombre."
      )

    if not all(isfinite(v) for v in (
      self.Sut,
      self.Sy,
      self.temperatura,
      self.confiabilidad,
      self.k_f_marin
    )):
      raise ValueError(
        "Las propiedades del material deben ser finitas."
      )

    if self.Sut <= 0 or self.Sy <= 0:
      raise ValueError(
        "Sut y Sy deben ser positivos."
      )

    if self.Sut <= self.Sy:
      raise ValueError(
        "Sut debe ser mayor que Sy."
      )

    for nombre, valor in (
      ("E", self.E),
      ("G", self.G),
      ("densidad", self.densidad)
    ):
      if valor is not None:
        if not isfinite(valor) or valor <= 0:
          raise ValueError(
            f"La propiedad {nombre} debe ser positiva y finita."
          )

    if self.acabado not in ACABADOS_VALIDOS:
      raise ValueError(
        "El acabado superficial debe ser uno de: "
        + ", ".join(ACABADOS_VALIDOS) + "."
      )

    if not 20.0 <= self.temperatura <= 600.0:
      raise ValueError(
        "La temperatura debe estar entre 20 y 600 °C."
      )

    if not 0.5 <= self.confiabilidad <= 0.999999:
      raise ValueError(
        "La confiabilidad debe estar entre 0.50 y 0.999999."
      )

    if self.k_f_marin <= 0:
      raise ValueError(
        "El factor de efectos diversos k_f_marin debe ser "
        "positivo."
      )

  @classmethod
  def crear(
    cls,
    nombre,
    sistema,
    Sut,
    Sy,
    E=None,
    G=None,
    densidad=None,
    acabado="maquinado",
    temperatura=None,
    confiabilidad=0.5,
    k_f_marin=1.0
  ):
    """Crea un material con las unidades del sistema elegido.

    En SI: Sut y Sy en MPa, E y G en GPa, densidad en kg/m³,
    temperatura en °C.
    En inglés: Sut y Sy en ksi, E y G en Mpsi, densidad en lb/in³,
    temperatura en °F.
    """
    temperatura_c = (
      20.0 if temperatura is None
      else temperatura_a_c(temperatura, sistema)
    )

    return cls(
      nombre=nombre,
      Sut=presion_a_pa(Sut, sistema),
      Sy=presion_a_pa(Sy, sistema),
      E=None if E is None else modulo_a_pa(E, sistema),
      G=None if G is None else modulo_a_pa(G, sistema),
      densidad=(
        None if densidad is None
        else densidad_a_kg_m3(densidad, sistema)
      ),
      acabado=acabado,
      temperatura=temperatura_c,
      confiabilidad=confiabilidad,
      k_f_marin=k_f_marin
    )
