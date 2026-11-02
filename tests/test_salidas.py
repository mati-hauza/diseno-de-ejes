import io
from contextlib import redirect_stdout

import matplotlib.pyplot as plt
import numpy as np
import pytest

from calculos.solicitaciones import calcular_solicitaciones
from calculos.transformaciones import transformar_carga
from modelo.carga import (
  CargaCartesiana,
  CargaCilindrica,
  CargaDistribuida
)
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades
from salidas.diagramas_eje import (
  _carga_distribuida_desde_n_por_m,
  _componentes_carga,
  _obtener_datos_graficos,
  _punto_aplicacion,
  _texto_acciones,
  generar_diagramas_eje
)
from salidas.diagramas_solicitaciones import generar_diagramas
from salidas.informe_solicitaciones import mostrar_informe


def _eje_con_carga_simple(eje):
  eje.agregar_carga(
    CargaCartesiana.crear(
      "P", 500, SistemaUnidades.SI, Fy=-1000
    )
  )

  return calcular_solicitaciones(eje)


def test_informe_muestra_reacciones_y_unidades_si(eje_si):
  resultado = _eje_con_carga_simple(eje_si)

  salida = io.StringIO()

  with redirect_stdout(salida):
    mostrar_informe(eje_si, resultado)

  texto = salida.getvalue()

  assert "REACCIONES EN LOS APOYOS" in texto
  assert "Ry = 500.000 N" in texto
  assert "ECUACIONES DE LAS SOLICITACIONES INTERNAS" in texto
  assert "Variable: x (mm)" in texto
  assert "Momentos: N·mm" in texto
  assert "Mz(x) [N·mm]" in texto


def test_informe_convierte_unidades_en_sistema_ingles(eje_ingles):
  eje_ingles.agregar_carga(
    CargaCartesiana.crear(
      "P", 20, SistemaUnidades.INGLES, Fy=-200
    )
  )
  resultado = calcular_solicitaciones(eje_ingles)

  salida = io.StringIO()

  with redirect_stdout(salida):
    mostrar_informe(eje_ingles, resultado)

  texto = salida.getvalue()

  assert "Ry = 100.000 lbf" in texto
  assert "Variable: x (in)" in texto
  assert "Momentos: lbf·in" in texto


def test_datos_graficos_reflejan_el_modelo(eje_si):
  eje_si.agregar_carga(
    CargaCartesiana.crear(
      "P", 300, SistemaUnidades.SI, Fy=-1000
    )
  )
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qy=-10
    )
  )
  eje_si.agregar_momento(
    Momento.crear(
      "M", 500, SistemaUnidades.SI, Mz=1000
    )
  )

  resultado = calcular_solicitaciones(eje_si)

  datos = _obtener_datos_graficos(
    eje_si,
    resultado,
    eje_si.obtener_todas_las_cargas(),
    eje_si.obtener_todos_los_momentos()
  )

  assert len(datos["cargas"]) == 1
  assert datos["cargas"][0]["id"] == "F1"
  assert datos["cargas"][0]["origen"][0] == pytest.approx(0.3)
  assert np.allclose(
    datos["cargas"][0]["vector"], np.array([0, -1000, 0])
  )

  assert len(datos["distribuidas"]) == 1
  assert datos["distribuidas"][0]["id"] == "D1"
  assert datos["distribuidas"][0]["inicio"] == pytest.approx(0)
  assert datos["distribuidas"][0]["fin"] == pytest.approx(1)
  assert np.allclose(
    datos["distribuidas"][0]["vector"], np.array([0, -10000, 0])
  )

  assert len(datos["reacciones"]) == 2
  assert datos["reacciones"][0]["origen"][0] == pytest.approx(0.2)
  assert datos["reacciones"][1]["origen"][0] == pytest.approx(0.8)
  assert np.allclose(
    datos["reacciones"][0]["vector"],
    np.array([
      resultado.reacciones[0].Fx,
      resultado.reacciones[0].Fy,
      resultado.reacciones[0].Fz
    ])
  )

  assert len(datos["momentos"]) == 1
  assert datos["momentos"][0]["id"] == "M1"
  assert np.allclose(
    datos["momentos"][0]["vector"], np.array([0, 0, 1])
  )


def test_texto_de_acciones_muestra_intensidades_convertidas(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qy=-10
    )
  )
  resultado = calcular_solicitaciones(eje_si)

  datos = _obtener_datos_graficos(
    eje_si,
    resultado,
    eje_si.obtener_todas_las_cargas(),
    eje_si.obtener_todos_los_momentos()
  )
  texto = _texto_acciones(eje_si, datos, ("mm", "N", "N·mm"))

  assert "CARGAS DISTRIBUIDAS" in texto
  assert "qy = -10 N/mm" in texto
  assert "REACCIONES CALCULADAS" in texto


def test_texto_de_acciones_convierte_intensidad_en_ingles(eje_ingles):
  eje_ingles.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 40, SistemaUnidades.INGLES, qy=-10
    )
  )
  resultado = calcular_solicitaciones(eje_ingles)

  datos = _obtener_datos_graficos(
    eje_ingles,
    resultado,
    eje_ingles.obtener_todas_las_cargas(),
    eje_ingles.obtener_todos_los_momentos()
  )
  texto = _texto_acciones(
    eje_ingles, datos, ("in", "lbf", "lbf·in")
  )

  assert "qy = -10 lbf/in" in texto


def test_generar_diagramas_eje_con_distribuidas_y_momentos(
  eje_si,
  monkeypatch
):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 0, 1000, SistemaUnidades.SI, qy=-10
    )
  )
  eje_si.agregar_momento(
    Momento.crear(
      "M", 500, SistemaUnidades.SI, Mz=1000
    )
  )
  resultado = calcular_solicitaciones(eje_si)
  llamadas = []

  monkeypatch.setattr(
    plt, "show", lambda: llamadas.append(True)
  )

  figura_3d, figura_2d = generar_diagramas_eje(
    eje_si, resultado, mostrar=False
  )

  assert llamadas == []
  assert figura_3d.axes[0].name == "3d"
  assert len(figura_2d.axes[0].patches) > 0
  assert len(figura_2d.axes[0].texts) > 0

  plt.close("all")



def test_componentes_graficas_coinciden_con_la_carga():
  carga = CargaCilindrica.crear(
    "F",
    500,
    SistemaUnidades.SI,
    radio_aplicacion=100,
    angulo_aplicacion=37,
    axial=50,
    radial=100,
    tangencial=200
  )

  accion = transformar_carga(carga)
  componentes = _componentes_carga(carga, "F1")

  suma = sum(
    (componente["vector"] for componente in componentes),
    np.zeros(3)
  )

  assert np.allclose(
    suma,
    np.array([accion.Fx, accion.Fy, accion.Fz])
  )

  origen = _punto_aplicacion(carga)
  assert origen[0] == pytest.approx(0.5)
  assert origen[1] == pytest.approx(0.1 * np.cos(np.radians(37)))
  assert origen[2] == pytest.approx(0.1 * np.sin(np.radians(37)))


def test_conversion_de_carga_distribuida_para_graficos(eje_si):
  assert _carga_distribuida_desde_n_por_m(
    -10000, eje_si
  ) == pytest.approx(-10)


def test_generar_diagramas_eje_no_llama_a_show(eje_si, monkeypatch):
  resultado = _eje_con_carga_simple(eje_si)
  llamadas = []

  monkeypatch.setattr(
    plt, "show", lambda: llamadas.append(True)
  )

  figura_3d, figura_2d = generar_diagramas_eje(
    eje_si, resultado, mostrar=False
  )

  assert llamadas == []
  assert figura_3d is not None
  assert figura_2d is not None
  assert len(figura_3d.axes) == 2
  assert len(figura_2d.axes) == 3
  assert figura_2d.axes[0].get_title() == "Proyección XY"
  assert figura_2d.axes[1].get_title() == "Proyección XZ"

  plt.close("all")


def test_generar_diagramas_de_solicitaciones_dibuja_todos_los_tramos(
  eje_si,
  monkeypatch
):
  resultado = _eje_con_carga_simple(eje_si)
  llamadas = []

  monkeypatch.setattr(
    plt, "show", lambda: llamadas.append(True)
  )

  generar_diagramas(eje_si, resultado)

  assert llamadas == [True]

  figura = plt.gcf()

  assert len(figura.axes) == 9
  assert figura.axes[0].get_ylabel() == "Vy (N)"
  assert figura.axes[0].get_xlabel() == "Posición X (mm)"

  lineas_datos = [
    linea for linea in figura.axes[0].lines
    if len(linea.get_xdata()) > 2
  ]
  assert len(lineas_datos) == 4

  valores_vy = np.concatenate([
    linea.get_ydata() for linea in lineas_datos
  ])

  assert np.any(np.isclose(valores_vy, -500))
  assert np.any(np.isclose(valores_vy, 0))
  assert np.any(np.isclose(valores_vy, 500))

  assert figura.axes[5].get_ylabel() == "T (N·mm)"
  assert figura.axes[7].get_ylabel() == "MR (N·mm)"
  assert len(figura.axes[8].lines) == 0

  plt.close("all")
