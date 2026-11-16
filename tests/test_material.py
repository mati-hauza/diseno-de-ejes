import pytest

from modelo.eje import Eje
from modelo.material import Material
from modelo.unidades import (
  SistemaUnidades,
  densidad_a_kg_m3,
  densidad_desde_kg_m3,
  modulo_a_pa,
  modulo_desde_pa,
  presion_a_pa,
  presion_desde_pa
)


def test_material_crear_si_convierte_a_pa():
  material = Material.crear(
    "AISI 1045",
    SistemaUnidades.SI,
    Sut=630,
    Sy=530,
    E=205,
    G=80,
    densidad=7850
  )

  assert material.nombre == "AISI 1045"
  assert material.Sut == pytest.approx(630e6)
  assert material.Sy == pytest.approx(530e6)
  assert material.E == pytest.approx(205e9)
  assert material.G == pytest.approx(80e9)
  assert material.densidad == pytest.approx(7850)


def test_material_crear_ingles_convierte_a_si():
  material = Material.crear(
    "AISI 1045",
    SistemaUnidades.INGLES,
    Sut=91.3,
    Sy=76.9,
    E=29.7,
    G=11.6,
    densidad=0.284
  )

  assert material.Sut == pytest.approx(91.3 * 1000 * 6894.757293168361)
  assert material.Sy == pytest.approx(76.9 * 1000 * 6894.757293168361)
  assert material.E == pytest.approx(
    29.7 * 1e6 * 6894.757293168361
  )
  assert material.G == pytest.approx(
    11.6 * 1e6 * 6894.757293168361
  )
  assert material.densidad == pytest.approx(
    0.284 * 27679.904710191
  )


@pytest.mark.parametrize(
  "campo, valor",
  [
    ("Sut", 0),
    ("Sy", -100),
    ("E", 0),
    ("G", -1),
    ("densidad", 0),
    ("Sut", float("nan")),
    ("E", float("inf")),
  ]
)
def test_material_rechaza_propiedades_invalidas(campo, valor):
  datos = {
    "Sut": 630e6,
    "Sy": 530e6,
    "E": 205e9,
    "G": 80e9,
    "densidad": 7850
  }
  datos[campo] = valor

  with pytest.raises(ValueError):
    Material("AISI 1045", **datos)


def test_material_rechaza_nombre_vacio():
  with pytest.raises(ValueError, match="nombre"):
    Material.crear(
      "",
      SistemaUnidades.SI,
      Sut=630,
      Sy=530,
      E=205,
      G=80,
      densidad=7850
    )


def test_conversiones_de_presion():
  assert presion_a_pa(1, SistemaUnidades.SI) == pytest.approx(1e6)
  assert presion_a_pa(1, SistemaUnidades.INGLES) == pytest.approx(
    6894757.293168361
  )
  assert presion_desde_pa(1e6, SistemaUnidades.SI) == pytest.approx(1)
  assert presion_desde_pa(
    6894757.293168361, SistemaUnidades.INGLES
  ) == pytest.approx(1)


def test_conversiones_de_modulo():
  assert modulo_a_pa(1, SistemaUnidades.SI) == pytest.approx(1e9)
  assert modulo_a_pa(1, SistemaUnidades.INGLES) == pytest.approx(
    6894757293.168361
  )
  assert modulo_desde_pa(1e9, SistemaUnidades.SI) == pytest.approx(1)
  assert modulo_desde_pa(
    6894757293.168361, SistemaUnidades.INGLES
  ) == pytest.approx(1)


def test_conversiones_de_densidad():
  assert densidad_a_kg_m3(
    1, SistemaUnidades.INGLES
  ) == pytest.approx(27679.904710191)
  assert densidad_desde_kg_m3(
    27679.904710191, SistemaUnidades.INGLES
  ) == pytest.approx(1)
  assert densidad_a_kg_m3(7850, SistemaUnidades.SI) == pytest.approx(
    7850
  )


def test_conversiones_rechazan_sistema_invalido():
  with pytest.raises(TypeError):
    presion_a_pa(100, "SI")

  with pytest.raises(TypeError):
    modulo_desde_pa(2e11, "SI")

  with pytest.raises(TypeError):
    densidad_a_kg_m3(7850, "SI")


def test_eje_acepta_material():
  material = Material.crear(
    "AISI 1045",
    SistemaUnidades.SI,
    Sut=630,
    Sy=530,
    E=205,
    G=80,
    densidad=7850
  )

  eje = Eje.crear(
    1000, SistemaUnidades.SI, material=material
  )

  assert eje.material is material


def test_eje_rechaza_material_invalido():
  with pytest.raises(TypeError, match="Material"):
    Eje.crear(
      1000, SistemaUnidades.SI, material="AISI 1045"
    )
