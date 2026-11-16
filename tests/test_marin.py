import pytest

from calculos.marin import (
  factor_acabado,
  factor_confiabilidad,
  factor_tamano,
  factor_temperatura,
  factores_marin,
  limite_probeta
)
from modelo.material import Material
from modelo.unidades import SistemaUnidades


S = SistemaUnidades.SI


def _material(**cambios):
  datos = dict(
    Sut=630,
    Sy=530,
    acabado="maquinado",
    temperatura=20,
    confiabilidad=0.99
  )
  datos.update(cambios)
  return Material.crear("AISI 1045", S, **datos)


def test_factor_acabado_maquinado():
  material = _material()
  ka, a, b, Sut_mpa = factor_acabado(material)

  assert a == pytest.approx(4.51)
  assert b == pytest.approx(-0.265)
  assert Sut_mpa == pytest.approx(630)
  assert ka == pytest.approx(4.51 * 630 ** -0.265)


def test_factor_tamano_por_tramos():
  assert factor_tamano(0.040) == pytest.approx(
    1.24 * 40 ** -0.107
  )
  assert factor_tamano(0.100) == pytest.approx(
    1.51 * 100 ** -0.157
  )


def test_factor_tamano_fuera_de_rango():
  with pytest.raises(ValueError, match="fuera del rango"):
    factor_tamano(0.002)

  with pytest.raises(ValueError, match="fuera del rango"):
    factor_tamano(0.300)


def test_temperatura_y_confiabilidad():
  material = _material(temperatura=20, confiabilidad=0.99)

  assert factor_temperatura(material) == pytest.approx(1.0)
  assert factor_confiabilidad(material) == pytest.approx(0.814)


def test_temperatura_interpolada():
  material = _material(temperatura=75)

  esperado = 1.010 + (1.020 - 1.010) * (75 - 50) / (100 - 50)
  assert factor_temperatura(material) == pytest.approx(esperado)


def test_limite_probeta():
  assert limite_probeta(_material(Sut=630)) == pytest.approx(315e6)
  assert limite_probeta(_material(Sut=1600, Sy=1400)) == pytest.approx(
    700e6
  )


def test_factores_marin_completos():
  material = _material()
  datos = factores_marin(material, 0.040)

  esperado = (
    datos["ka"]
    * datos["kb"]
    * datos["kc"]
    * datos["kd"]
    * datos["ke"]
    * datos["kf_marin"]
    * datos["Se_prima"]
  )

  assert datos["Se"] == pytest.approx(esperado)
  assert datos["kc"] == 1.0
  assert datos["Se"] > 0
