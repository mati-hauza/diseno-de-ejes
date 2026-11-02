import numpy as np
import pytest

from calculos.transformaciones import (
  obtener_acciones_externas,
  obtener_acciones_puntuales,
  transformar_carga,
  transformar_carga_distribuida,
  transformar_momento
)
from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)
from modelo.elemento import Elemento
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades


def test_carga_cartesiana_genera_momentos_por_excentricidad():
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

  accion = transformar_carga(carga)

  ry = 0.1 * np.cos(np.radians(30))
  rz = 0.1 * np.sin(np.radians(30))

  assert accion.Fx == pytest.approx(10)
  assert accion.Fy == pytest.approx(20)
  assert accion.Fz == pytest.approx(30)
  assert accion.Mx == pytest.approx(ry * 30 - rz * 20)
  assert accion.My == pytest.approx(rz * 10)
  assert accion.Mz == pytest.approx(-ry * 10)


def test_carga_cilindrica_en_angulo_cero():
  carga = CargaCilindrica.crear(
    "F",
    500,
    SistemaUnidades.SI,
    radio_aplicacion=50,
    angulo_aplicacion=0,
    axial=100,
    radial=200,
    tangencial=300
  )

  accion = transformar_carga(carga)

  assert accion.Fx == pytest.approx(100)
  assert accion.Fy == pytest.approx(200)
  assert accion.Fz == pytest.approx(300)
  assert accion.Mx == pytest.approx(15)
  assert accion.My == pytest.approx(0)
  # La fuerza axial está aplicada en y = r y genera un momento Mz = -r*Fx.
  assert accion.Mz == pytest.approx(-5)


def test_carga_cilindrica_en_angulo_noventa_grados():
  carga = CargaCilindrica.crear(
    "F",
    500,
    SistemaUnidades.SI,
    radio_aplicacion=50,
    angulo_aplicacion=90,
    axial=100,
    radial=200,
    tangencial=300
  )

  accion = transformar_carga(carga)

  assert accion.Fx == pytest.approx(100)
  assert accion.Fy == pytest.approx(-300)
  assert accion.Fz == pytest.approx(200)
  assert accion.Mx == pytest.approx(15)
  assert accion.My == pytest.approx(5)
  assert accion.Mz == pytest.approx(0)


def test_carga_distribuida_se_reemplaza_por_su_resultante():
  carga = CargaDistribuida.crear(
    "q", 100, 700, SistemaUnidades.SI, qy=-10
  )

  accion = transformar_carga_distribuida(carga)

  assert accion.posicion == pytest.approx(0.4)
  assert accion.Fx == pytest.approx(0)
  assert accion.Fy == pytest.approx(-6000)
  assert accion.Fz == pytest.approx(0)


def test_momento_se_convierte_en_accion_sin_fuerzas():
  momento = Momento.crear(
    "M",
    500,
    SistemaUnidades.SI,
    Mx=1000,
    My=2000,
    Mz=-3000
  )

  accion = transformar_momento(momento)

  assert accion.posicion == pytest.approx(0.5)
  assert accion.Fx == accion.Fy == accion.Fz == 0
  assert accion.Mx == pytest.approx(1)
  assert accion.My == pytest.approx(2)
  assert accion.Mz == pytest.approx(-3)


def test_acciones_puntuales_incluyen_cargas_y_momentos_de_elementos():
  elemento = Elemento.crear(
    "Engranaje", 500, 200, SistemaUnidades.SI
  )
  carga = CargaCilindrica.crear(
    "F",
    500,
    SistemaUnidades.SI,
    radio_aplicacion=50,
    radial=100
  )
  momento = Momento.crear(
    "M", 500, SistemaUnidades.SI, Mz=1000
  )

  elemento.agregar_carga(carga)
  elemento.agregar_momento(momento)

  class EjeFalso:
    def obtener_todas_las_cargas(self):
      return [carga]

    def obtener_todos_los_momentos(self):
      return [momento]

  acciones = obtener_acciones_puntuales(EjeFalso())

  assert len(acciones) == 2
  assert acciones[0].nombre == "F"
  assert acciones[0].Fy == pytest.approx(100)
  assert acciones[1].nombre == "M"
  assert acciones[1].Mz == pytest.approx(1)


def test_acciones_externas_incluyen_distribuidas_como_resultantes():
  carga = CargaDistribuida.crear(
    "q", 100, 700, SistemaUnidades.SI, qy=-10
  )

  class EjeFalso:
    def obtener_todas_las_cargas(self):
      return []

    def obtener_todos_los_momentos(self):
      return []

    def obtener_todas_las_cargas_distribuidas(self):
      return [carga]

  acciones = obtener_acciones_externas(EjeFalso())

  assert len(acciones) == 1
  assert acciones[0].posicion == pytest.approx(0.4)
  assert acciones[0].Fy == pytest.approx(-6000)
