import numpy as np
import pytest

from calculos.solicitaciones import calcular_solicitaciones
from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades


def _resultado(eje):
  return calcular_solicitaciones(eje)


def test_solicitaciones_de_carga_puntual(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fy=-1000
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.posiciones == pytest.approx(
    [0.0, 0.2, 0.5, 0.8, 1.0]
  )

  assert resultado.evaluar("Vy", 0.1) == pytest.approx(0)
  assert resultado.evaluar("Vy", 0.3) == pytest.approx(-500)
  assert resultado.evaluar("Vy", 0.5) == pytest.approx(500)
  assert resultado.evaluar("Vy", 0.9) == pytest.approx(0)

  assert resultado.evaluar("Mz", 0.2) == pytest.approx(0)
  assert resultado.evaluar("Mz", 0.3) == pytest.approx(50)
  assert resultado.evaluar("Mz", 0.5) == pytest.approx(150)
  assert resultado.evaluar("Mz", 0.6) == pytest.approx(100)
  assert resultado.evaluar("Mz", 0.8) == pytest.approx(0)

  assert resultado.evaluar("VR", 0.3) == pytest.approx(500)
  assert resultado.evaluar("MR", 0.3) == pytest.approx(50)
  assert resultado.evaluar("N", 0.3) == pytest.approx(0)
  assert resultado.evaluar("T", 0.3) == pytest.approx(0)


def test_solicitaciones_de_carga_distribuida_completa(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qy=-10
    )
  )

  resultado = _resultado(eje_si)

  # La carga total es -10000 N y su resultante está en x = 0.5 m.
  assert resultado.evaluar("Vy", 0.2) == pytest.approx(-3000)
  assert resultado.evaluar("Vy", 0.4) == pytest.approx(-1000)
  assert resultado.evaluar("Vy", 0.5) == pytest.approx(0)
  assert resultado.evaluar("Vy", 0.8) == pytest.approx(-2000)

  assert resultado.evaluar("Mz", 0.2) == pytest.approx(-200)
  assert resultado.evaluar("Mz", 0.3) == pytest.approx(50)
  assert resultado.evaluar("Mz", 0.5) == pytest.approx(250)
  assert resultado.evaluar("Mz", 0.8) == pytest.approx(-200)
  assert resultado.evaluar("Mz", 1.0) == pytest.approx(0)


def test_solicitaciones_de_carga_distribuida_parcial(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 300, 700, SistemaUnidades.SI, qy=-10
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("Vy", 0.2) == pytest.approx(-2000)
  assert resultado.evaluar("Vy", 0.4) == pytest.approx(-1000)
  assert resultado.evaluar("Vy", 0.6) == pytest.approx(1000)
  assert resultado.evaluar("Vy", 0.8) == pytest.approx(0)

  assert resultado.evaluar("Mz", 0.3) == pytest.approx(200)
  assert resultado.evaluar("Mz", 0.5) == pytest.approx(400)
  assert resultado.evaluar("Mz", 0.7) == pytest.approx(200)
  assert resultado.evaluar("Mz", 0.8) == pytest.approx(0)


def test_solicitaciones_de_carga_distribuida_en_z(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qz=-10
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("Vy", 0.4) == pytest.approx(0)
  assert resultado.evaluar("Vz", 0.2) == pytest.approx(-3000)
  assert resultado.evaluar("Vz", 0.4) == pytest.approx(-1000)
  assert resultado.evaluar("Vz", 0.5) == pytest.approx(0)
  assert resultado.evaluar("Vz", 0.8) == pytest.approx(-2000)

  assert resultado.evaluar("My", 0.2) == pytest.approx(200)
  assert resultado.evaluar("My", 0.3) == pytest.approx(-50)
  assert resultado.evaluar("My", 0.5) == pytest.approx(-250)
  assert resultado.evaluar("My", 0.8) == pytest.approx(200)
  assert resultado.evaluar("My", 1.0) == pytest.approx(0)


def test_solicitaciones_de_carga_distribuida_axial(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qx=-10
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("N", 0.2) == pytest.approx(-8000)
  assert resultado.evaluar("N", 0.3) == pytest.approx(-7000)
  assert resultado.evaluar("N", 0.5) == pytest.approx(-5000)
  assert resultado.evaluar("N", 0.8) == pytest.approx(-2000)
  assert resultado.evaluar("N", 1.0) == pytest.approx(0)


def test_resultantes_en_apoyo_no_generan_radicando_negativo(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P",
      500,
      SistemaUnidades.SI,
      Fy=-818.1811756524122,
      Fz=-905.7672491505309
    )
  )

  resultado = _resultado(eje_si)

  # En el apoyo, My y Mz deben ser nulos. Evaluar la expresión expandida
  # de MR podía devolver sqrt(negativo) por redondeo; evaluar las
  # componentes evita ese problema.
  assert resultado.evaluar("MR", 0.2) == pytest.approx(0)
  assert resultado.evaluar("MR", 0.8) == pytest.approx(0)




def test_solicitaciones_en_dos_planos(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P",
      500,
      SistemaUnidades.SI,
      Fy=-1000,
      Fz=-500
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("Vy", 0.3) == pytest.approx(-500)
  assert resultado.evaluar("Vz", 0.3) == pytest.approx(-250)
  assert resultado.evaluar("My", 0.3) == pytest.approx(-25)
  assert resultado.evaluar("Mz", 0.3) == pytest.approx(50)

  assert resultado.evaluar("Vy", 0.6) == pytest.approx(500)
  assert resultado.evaluar("Vz", 0.6) == pytest.approx(250)
  assert resultado.evaluar("My", 0.6) == pytest.approx(-50)
  assert resultado.evaluar("Mz", 0.6) == pytest.approx(100)

  assert resultado.evaluar("VR", 0.6) == pytest.approx(
    np.hypot(500, 250)
  )
  assert resultado.evaluar("MR", 0.6) == pytest.approx(
    np.hypot(50, 100)
  )


def test_solicitaciones_axiales(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fx=1000
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("N", 0.1) == pytest.approx(0)
  assert resultado.evaluar("N", 0.3) == pytest.approx(1000)
  assert resultado.evaluar("N", 0.6) == pytest.approx(0)


def test_solicitaciones_de_torsion(eje_si):
  eje_si.agregar_carga(
    CargaCilindrica.crear(
      "F1",
      500,
      SistemaUnidades.SI,
      radio_aplicacion=50,
      tangencial=1000
    )
  )
  eje_si.agregar_carga(
    CargaCilindrica.crear(
      "F2",
      800,
      SistemaUnidades.SI,
      radio_aplicacion=50,
      tangencial=-1000
    )
  )

  resultado = _resultado(eje_si)

  assert resultado.evaluar("T", 0.4) == pytest.approx(0)
  assert resultado.evaluar("T", 0.6) == pytest.approx(-50)
  assert resultado.evaluar("T", 0.9) == pytest.approx(0)


def test_solicitaciones_de_momento_aplicado(eje_si):
  eje_si.agregar_momento(
    Momento.crear(
      "M", 500, SistemaUnidades.SI, Mz=1000
    )
  )

  resultado = _resultado(eje_si)

  # 1000 N·mm = 1 N·m.  Las reacciones son 1.6667 N y -1.6667 N.
  assert resultado.evaluar("Mz", 0.4) == pytest.approx(1 / 3)
  assert resultado.evaluar("Mz", 0.6) == pytest.approx(-1 / 3)
  assert resultado.evaluar("Mz", 0.8) == pytest.approx(0)


def test_evaluar_con_nombre_inexistente(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fy=-1000
    )
  )

  resultado = _resultado(eje_si)

  with pytest.raises(KeyError, match="NoExiste"):
    resultado.evaluar("NoExiste", 0.5)
