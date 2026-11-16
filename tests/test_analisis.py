import matplotlib
import matplotlib.pyplot as plt
import pytest

matplotlib.use("Agg", force=True)

from calculos.analisis import analizar_eje
from modelo.apoyo import Apoyo
from modelo.carga import CargaCilindrica
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.material import Material
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades
from salidas.diagramas_seguridad import generar_diagramas_seguridad


S = SistemaUnidades.SI


def _eje_balanceado(n_div=100):
  material = Material.crear(
    "AISI 1045", S, Sut=630, Sy=530,
    acabado="maquinado", confiabilidad=0.99
  )
  chaveta = Material.crear("Chaveta", S, Sut=590, Sy=490)
  cubo = Material.crear("Cubo", S, Sut=630, Sy=530)

  eje = Eje.crear(
    1000, S, material=material, n_min=1.5, n_div=n_div
  )
  eje.agregar_tramo(Tramo.crear(0, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))

  pinon = Elemento.crear(
    "Piñón", 300, 100, S,
    usa_chaveta=True, a=12.5,
    material_chaveta=chaveta,
    material_cubo=cubo,
    r_f=0.5
  )
  pinon.agregar_carga(
    CargaCilindrica.crear(
      "F1", 300, S,
      radio_aplicacion=60,
      radial=-500,
      tangencial=1000
    )
  )
  eje.agregar_elemento(pinon)

  polea = Elemento.crear(
    "Polea", 700, 100, S,
    usa_chaveta=True, a=12.5,
    material_chaveta=chaveta,
    material_cubo=cubo,
    r_f=0.5
  )
  polea.agregar_carga(
    CargaCilindrica.crear(
      "F2", 700, S,
      radio_aplicacion=60,
      tangencial=-1000
    )
  )
  eje.agregar_elemento(polea)

  return eje


def test_analisis_completo_devuelve_criterios_y_minimos():
  resultado = analizar_eje(_eje_balanceado())

  assert len(resultado.chavetas) == 2
  assert resultado.puntos
  assert resultado.n_eje > 0
  assert resultado.punto_critico is not None
  assert set(resultado.minimos) == {"goodman", "fluencia"}
  assert set(resultado.punto_critico.factores) == {
    "goodman", "fluencia"
  }
  assert resultado.cumple


def test_analisis_incluye_lados_en_discontinuidades():
  resultado = analizar_eje(_eje_balanceado())

  lados = {
    (round(rp.punto.x, 6), rp.punto.lado)
    for rp in resultado.puntos
    if abs(rp.punto.x - 0.3) < 1e-9
  }

  assert (0.3, -1) in lados
  assert (0.3, 1) in lados


def test_graficas_de_seguridad_una_por_criterio():
  resultado = analizar_eje(_eje_balanceado())

  figuras = generar_diagramas_seguridad(resultado, mostrar=False)

  assert len(figuras) == len(resultado.criterios)
  assert all(len(fig.axes) == 1 for fig in figuras)

  plt.close("all")


def test_analisis_exige_material_y_n_min():
  eje = Eje.crear(1000, S)
  eje.agregar_tramo(Tramo.crear(0, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))

  with pytest.raises(ValueError, match="material"):
    analizar_eje(eje)

  eje.material = Material.crear("M", S, Sut=630, Sy=530)
  with pytest.raises(ValueError, match="n_min"):
    analizar_eje(eje)
