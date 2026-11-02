import numpy as np
import pytest

from calculos.reacciones import calcular_reacciones
from calculos.transformaciones import obtener_acciones_externas
from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades


def _equilibrio_global(eje, reacciones):
  """Comprueba fuerza y momento resultantes nulos."""
  acciones = obtener_acciones_externas(eje)

  fx = sum(a.Fx for a in acciones)
  fy = sum(a.Fy for a in acciones)
  fz = sum(a.Fz for a in acciones)

  mx = sum(a.Mx for a in acciones)
  my = sum(-a.posicion * a.Fz + a.My for a in acciones)
  mz = sum(a.posicion * a.Fy + a.Mz for a in acciones)

  for reaccion in reacciones:
    fx += reaccion.Fx
    fy += reaccion.Fy
    fz += reaccion.Fz
    mx += reaccion.Mx
    my += -reaccion.posicion * reaccion.Fz + reaccion.My
    mz += reaccion.posicion * reaccion.Fy + reaccion.Mz

  return np.array([fx, fy, fz, mx, my, mz])


def test_reacciones_de_carga_puntual_centrada(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fy=-1000
    )
  )

  reacciones, advertencias = calcular_reacciones(eje_si)

  assert reacciones[0].Fy == pytest.approx(500)
  assert reacciones[1].Fy == pytest.approx(500)
  assert reacciones[0].Fx == pytest.approx(0)
  assert reacciones[1].Fx == pytest.approx(0)
  assert reacciones[0].Fz == pytest.approx(0)
  assert reacciones[1].Fz == pytest.approx(0)
  assert advertencias == []
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )


def test_reacciones_de_carga_puntual_asimetrica(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 300, SistemaUnidades.SI, Fy=-1000
    )
  )

  reacciones, _ = calcular_reacciones(eje_si)

  # Ra + Rb = 1000; 0.2*Ra + 0.8*Rb = 300.
  assert reacciones[0].Fy == pytest.approx(2500 / 3)
  assert reacciones[1].Fy == pytest.approx(500 / 3)
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )


def test_reacciones_en_sistema_ingles(eje_ingles):
  eje_ingles.agregar_carga(
    CargaCartesiana.crear(
      "P", 20, SistemaUnidades.INGLES, Fy=-200
    )
  )

  reacciones, _ = calcular_reacciones(eje_ingles)

  # El resultado interno está en N, aunque la entrada esté en lbf.
  assert reacciones[0].Fy == pytest.approx(100 * 4.448221615)
  assert reacciones[1].Fy == pytest.approx(100 * 4.448221615)
  assert reacciones[0].posicion == pytest.approx(0.2032)
  assert reacciones[1].posicion == pytest.approx(0.8128)


def test_reaccion_axial_solo_en_el_apoyo_fijo(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fx=500
    )
  )

  reacciones, _ = calcular_reacciones(eje_si)

  assert reacciones[0].Fx == pytest.approx(-500)
  assert reacciones[1].Fx == pytest.approx(0)
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )


def test_reaccion_axial_en_apoyo_fijo_derecho():
  from modelo.apoyo import Apoyo
  from modelo.eje import Eje

  eje = Eje.crear(1000, SistemaUnidades.SI)
  eje.agregar_apoyo(
    Apoyo.crear("A", 200, 50, False, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 800, 50, True, SistemaUnidades.SI)
  )
  eje.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fx=500
    )
  )

  reacciones, _ = calcular_reacciones(eje)

  assert reacciones[0].Fx == pytest.approx(0)
  assert reacciones[1].Fx == pytest.approx(-500)


def test_reacciones_de_carga_distribuida(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qy=-10
    )
  )

  reacciones, _ = calcular_reacciones(eje_si)

  assert reacciones[0].Fy == pytest.approx(5000)
  assert reacciones[1].Fy == pytest.approx(5000)
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )


def test_reacciones_por_carga_axial_excentrica(eje_si):
  eje_si.agregar_carga(
    CargaCilindrica.crear(
      "F",
      500,
      SistemaUnidades.SI,
      radio_aplicacion=50,
      angulo_aplicacion=0,
      axial=500
    )
  )

  reacciones, _ = calcular_reacciones(eje_si)

  assert reacciones[0].Fy == pytest.approx(-125 / 3)
  assert reacciones[1].Fy == pytest.approx(125 / 3)
  assert reacciones[0].Fx == pytest.approx(-500)
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )


def test_aviso_de_torque_no_equilibrado(eje_si):
  eje_si.agregar_carga(
    CargaCilindrica.crear(
      "F",
      500,
      SistemaUnidades.SI,
      radio_aplicacion=50,
      tangencial=1000
    )
  )

  _, advertencias = calcular_reacciones(eje_si)

  assert len(advertencias) == 1
  assert "torsional" in advertencias[0]


def test_sin_aviso_cuando_los_torques_se_equilibran(eje_si):
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

  _, advertencias = calcular_reacciones(eje_si)

  assert advertencias == []


def test_reacciones_con_cargas_en_ambos_planos_y_momento(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P",
      300,
      SistemaUnidades.SI,
      Fx=200,
      Fy=-1000,
      Fz=500
    )
  )
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 200, 800, SistemaUnidades.SI, qz=-5
    )
  )
  eje_si.agregar_momento(
    Momento.crear(
      "M",
      600,
      SistemaUnidades.SI,
      My=2000,
      Mz=-1000
    )
  )

  reacciones, advertencias = calcular_reacciones(eje_si)

  assert advertencias == []
  assert _equilibrio_global(eje_si, reacciones) == pytest.approx(
    np.zeros(6), abs=1e-9
  )



def test_calcular_reacciones_exige_dos_apoyos():
  from modelo.eje import Eje

  eje = Eje.crear(1000, SistemaUnidades.SI)

  with pytest.raises(ValueError, match="exactamente dos apoyos"):
    calcular_reacciones(eje)
