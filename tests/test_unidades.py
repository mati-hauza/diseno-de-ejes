import pytest

from modelo.apoyo import Apoyo
from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)
from modelo.momento import Momento
from modelo.unidades import (
  SistemaUnidades,
  fuerza_a_n,
  fuerza_desde_n,
  longitud_a_m,
  longitud_desde_m,
  momento_a_nm,
  momento_desde_nm,
  obtener_unidades
)


@pytest.mark.parametrize(
  "sistema",
  [SistemaUnidades.SI, SistemaUnidades.INGLES]
)
def test_conversiones_de_longitud_ida_y_vuelta(sistema):
  for valor in (0.0, 1.0, 25.4, 1000.0):
    convertido = longitud_a_m(valor, sistema)
    assert longitud_desde_m(convertido, sistema) == pytest.approx(
      valor
    )


@pytest.mark.parametrize(
  "sistema",
  [SistemaUnidades.SI, SistemaUnidades.INGLES]
)
def test_conversiones_de_fuerza_ida_y_vuelta(sistema):
  for valor in (0.0, 1.0, 100.0, -1000.0):
    convertido = fuerza_a_n(valor, sistema)
    assert fuerza_desde_n(convertido, sistema) == pytest.approx(
      valor
    )


@pytest.mark.parametrize(
  "sistema",
  [SistemaUnidades.SI, SistemaUnidades.INGLES]
)
def test_conversiones_de_momento_ida_y_vuelta(sistema):
  for valor in (0.0, 1.0, 100.0, -1000.0):
    convertido = momento_a_nm(valor, sistema)
    assert momento_desde_nm(convertido, sistema) == pytest.approx(
      valor
    )


def test_unidades_de_salida():
  assert obtener_unidades(SistemaUnidades.SI) == {
    "longitud": "mm",
    "fuerza": "N",
    "momento": "N·mm"
  }

  assert obtener_unidades(SistemaUnidades.INGLES) == {
    "longitud": "in",
    "fuerza": "lbf",
    "momento": "lbf·in"
  }


def test_carga_distribuida_convierte_intensidad_si():
  carga = CargaDistribuida.crear(
    "q", 0, 1000, SistemaUnidades.SI, qy=-10
  )

  assert carga.inicio == pytest.approx(0.0)
  assert carga.fin == pytest.approx(1.0)
  assert carga.qy == pytest.approx(-10000.0)
  assert carga.qx == pytest.approx(0.0)
  assert carga.qz == pytest.approx(0.0)


def test_carga_distribuida_convierte_intensidad_ingles():
  carga = CargaDistribuida.crear(
    "q", 0, 40, SistemaUnidades.INGLES, qy=-10
  )

  # -10 lbf/in = -10 * 4.448221615 / 0.0254 N/m.
  assert carga.inicio == pytest.approx(0.0)
  assert carga.fin == pytest.approx(1.016)
  assert carga.qy == pytest.approx(-10 * 4.448221615 / 0.0254)


def test_apoyo_crear_convierte_medidas():
  apoyo = Apoyo.crear(
    "A", 200, 50, True, SistemaUnidades.SI
  )

  assert apoyo.posicion == pytest.approx(0.2)
  assert apoyo.ancho == pytest.approx(0.05)
  assert apoyo.inicio == pytest.approx(0.175)
  assert apoyo.fin == pytest.approx(0.225)
  assert apoyo.fijo_axial is True


def test_carga_cartesiana_convierte_componentes():
  carga = CargaCartesiana.crear(
    "F",
    500,
    SistemaUnidades.SI,
    radio_aplicacion=100,
    angulo_aplicacion=30,
    Fx=10,
    Fy=20,
    Fz=30
  )

  assert carga.posicion == pytest.approx(0.5)
  assert carga.radio_aplicacion == pytest.approx(0.1)
  assert carga.angulo_aplicacion == pytest.approx(30)
  assert carga.Fx == pytest.approx(10)
  assert carga.Fy == pytest.approx(20)
  assert carga.Fz == pytest.approx(30)


def test_carga_cilindrica_convierte_componentes():
  carga = CargaCilindrica.crear(
    "F",
    500,
    SistemaUnidades.INGLES,
    radio_aplicacion=2,
    angulo_aplicacion=45,
    axial=10,
    radial=20,
    tangencial=30
  )

  assert carga.posicion == pytest.approx(12.7)
  assert carga.radio_aplicacion == pytest.approx(0.0508)
  assert carga.angulo_aplicacion == pytest.approx(45)
  assert carga.F_axial == pytest.approx(10 * 4.448221615)
  assert carga.F_radial == pytest.approx(20 * 4.448221615)
  assert carga.F_tangencial == pytest.approx(30 * 4.448221615)


def test_momento_crear_convierte_unidades():
  momento = Momento.crear(
    "M",
    500,
    SistemaUnidades.SI,
    Mx=1000,
    My=2000,
    Mz=-3000
  )

  assert momento.posicion == pytest.approx(0.5)
  assert momento.Mx == pytest.approx(1.0)
  assert momento.My == pytest.approx(2.0)
  assert momento.Mz == pytest.approx(-3.0)
