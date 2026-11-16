import pytest

from calculos.concentradores import (
  _interpolar_tabla,
  calcular_concentradores,
  sensibilidad_neuber
)
from datos.concentradores import TABLA_HOMBROS, TABLA_RANURAS

from modelo.apoyo import Apoyo
from modelo.eje import Eje
from modelo.escalonamiento import Escalonamiento
from modelo.material import Material
from modelo.ranura import Ranura
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades


S = SistemaUnidades.SI


def _eje():
  material = Material.crear("Eje", S, Sut=630, Sy=530)
  eje = Eje.crear(1000, S, material=material)
  eje.agregar_tramo(Tramo.crear(0, 500, 40, S))
  eje.agregar_tramo(Tramo.crear(500, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))
  return eje


def test_interpolacion_en_punto_de_tabla():
  kt = _interpolar_tabla(
    TABLA_HOMBROS["A-15-9"], 0.10, 1.10, "A-15-9"
  )

  assert kt == pytest.approx(1.65)


def test_interpolacion_entre_curvas():
  kt = _interpolar_tabla(
    TABLA_HOMBROS["A-15-9"], 0.10, 1.30, "A-15-9"
  )

  esperado = 1.65 + (1.80 - 1.65) * (1.30 - 1.10) / (1.50 - 1.10)
  assert kt == pytest.approx(esperado)


def test_interpolacion_fuera_de_rango_es_error():
  with pytest.raises(ValueError, match="fuera del rango"):
    _interpolar_tabla(
      TABLA_HOMBROS["A-15-9"], 0.40, 1.10, "A-15-9"
    )

  with pytest.raises(ValueError, match="fuera del rango"):
    _interpolar_tabla(
      TABLA_HOMBROS["A-15-9"], 0.10, 0.90, "A-15-9"
    )


def test_interpolacion_de_ranura():
  ktn = _interpolar_tabla(
    TABLA_RANURAS["A-15-16"], 2.0, 0.10, "A-15-16"
  )
  kts = _interpolar_tabla(
    TABLA_RANURAS["A-15-17"], 2.0, 0.10, "A-15-17"
  )

  assert ktn == pytest.approx(5.00)
  assert kts == pytest.approx(3.12)


def test_sensibilidad_neuber_entre_cero_y_uno():
  q, qs = sensibilidad_neuber(0.0004, 630e6)

  assert 0 < q < 1
  assert 0 < qs < 1
  assert qs > q


def test_concentrador_de_escalonamiento():
  eje = _eje()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(500, 4, S)
  )

  concentrador, = calcular_concentradores(eje, [])

  assert concentrador.tipo == "escalonamiento"
  assert concentrador.lado == -1
  assert concentrador.KtB == pytest.approx(1.70625)
  assert concentrador.KtN > 1
  assert concentrador.Kts > 1
  assert 0 < concentrador.q < 1
  assert concentrador.KfB > concentrador.KtB - 1


def test_ranura_con_geometria_usa_figuras_de_ranura():
  eje = _eje()
  eje.agregar_ranura(
    Ranura.crear(700, S, ancho=4, profundidad=2, radio=0.4)
  )

  concentrador, = calcular_concentradores(eje, [])

  assert concentrador.tipo == "ranura"
  # a/t = 4/2 = 2 y r/t = 0.4/2 = 0.2.
  assert concentrador.KtN == pytest.approx(3.82)
  assert concentrador.KtB == concentrador.KtN
  assert concentrador.Kts == pytest.approx(2.384)
  assert concentrador.geometria["d_r"] == pytest.approx(0.046)


def test_ranura_sin_geometria_usa_tabla_7_1():
  eje = _eje()
  eje.agregar_ranura(Ranura.crear(700, S))

  concentrador, = calcular_concentradores(eje, [])

  assert concentrador.KfN == pytest.approx(5.0)
  assert concentrador.KfB == pytest.approx(5.0)
  assert concentrador.Kfs == pytest.approx(3.0)
  assert any("tabla 7-1" in a for a in concentrador.advertencias)
