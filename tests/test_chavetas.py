import pytest

from calculos.chavetas import dimensionar_chavetas
from modelo.apoyo import Apoyo
from modelo.carga import CargaCilindrica
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.material import Material
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades


S = SistemaUnidades.SI


def _materiales():
  eje = Material.crear("Eje", S, Sut=630, Sy=530)
  chaveta = Material.crear("Chaveta", S, Sut=590, Sy=490)
  cubo = Material.crear("Cubo", S, Sut=630, Sy=530)
  return eje, chaveta, cubo


def _eje_con_chaveta(posicion=500, ancho=100):
  material, chaveta, cubo = _materiales()

  eje = Eje.crear(1000, S, material=material, n_min=1.5)
  eje.agregar_tramo(Tramo.crear(0, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))

  elemento = Elemento.crear(
    "Engranaje",
    posicion,
    ancho,
    S,
    usa_chaveta=True,
    a=12.5,
    material_chaveta=chaveta,
    material_cubo=cubo,
    r_f=0.5
  )

  elemento.agregar_carga(
    CargaCilindrica.crear(
      "F",
      posicion,
      S,
      radio_aplicacion=80,
      tangencial=1000
    )
  )

  eje.agregar_elemento(elemento)

  return eje


def test_chaveta_se_dimensiona_por_aplastamiento():
  eje = _eje_con_chaveta()

  chaveta, = dimensionar_chavetas(eje)

  Te = 80 * 1000 * 0.001  # r·Ft = 80 N·m
  assert chaveta.Te == pytest.approx(Te)

  l_p = 4 * Te * 1.5 / (0.05 * 0.0125 * 490e6)
  assert chaveta.l == pytest.approx(l_p)
  assert chaveta.m == 1
  assert chaveta.n_p == pytest.approx(1.5)
  assert chaveta.n_c > 1.5


def test_chaveta_sin_torque_no_genera_chavetero():
  eje = _eje_con_chaveta()
  eje.elementos[0].cargas.clear()

  chaveta, = dimensionar_chavetas(eje)

  assert chaveta.Te == 0
  assert chaveta.l == 0
  assert not chaveta.existe
  assert any("no transmite torque" in a for a in chaveta.advertencias)


def test_varias_chavetas_reducen_la_longitud():
  eje = _eje_con_chaveta()
  eje.elementos[0].cargas[0].F_tangencial *= 100

  chaveta, = dimensionar_chavetas(eje)

  assert chaveta.m > 1
  assert chaveta.l <= 0.9 * eje.elementos[0].ancho
