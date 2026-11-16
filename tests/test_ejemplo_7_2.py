"""Regresión del ejemplo 7-2 de Shigley contra los valores publicados."""

import pytest

from calculos.analisis import analizar_eje
from main import construir_eje_ejemplo_7_2
from modelo.unidades import (
  SistemaUnidades,
  fuerza_desde_n,
  momento_desde_nm
)


SISTEMA = SistemaUnidades.INGLES

MOMENTOS_SHIGLEY = {
  2.75: 749.0,
  7.50: 3651.0,
  8.50: 4316.0,
  9.50: 2398.0,
  10.25: 959.0
}


@pytest.fixture(scope="module")
def resultado():
  return analizar_eje(construir_eje_ejemplo_7_2())


def test_reacciones_del_ejemplo_7_2(resultado):
  reacciones = {
    reaccion.nombre: reaccion
    for reaccion in resultado.reacciones
  }

  a = reacciones["Reacción A"]
  b = reacciones["Reacción B"]

  assert fuerza_desde_n(a.Fz, SISTEMA) == pytest.approx(115.0, rel=1e-3)
  assert fuerza_desde_n(a.Fy, SISTEMA) == pytest.approx(356.7, rel=1e-3)
  assert fuerza_desde_n(b.Fz, SISTEMA) == pytest.approx(1776.0, rel=1e-3)
  assert fuerza_desde_n(b.Fy, SISTEMA) == pytest.approx(725.3, rel=1e-3)


def test_par_de_torsion_del_ejemplo_7_2(resultado):
  par = resultado.solicitaciones.evaluar("T", 5.0 * 0.0254)

  assert abs(momento_desde_nm(par, SISTEMA)) == pytest.approx(
    3240.0, rel=1e-3
  )


@pytest.mark.parametrize("x_in, esperado", sorted(MOMENTOS_SHIGLEY.items()))
def test_momentos_flectores_del_ejemplo_7_2(resultado, x_in, esperado):
  momento = resultado.solicitaciones.evaluar("MR", x_in * 0.0254)

  assert momento_desde_nm(momento, SISTEMA) == pytest.approx(
    esperado, rel=2e-3
  )


def test_factor_de_seguridad_en_el_hombro_m(resultado):
  punto = next(
    p for p in resultado.puntos
    if (
      abs(p.punto.x - 10.25 * 0.0254) < 1e-6
      and p.punto.lado > 0
    )
  )

  # Shigley obtiene nf = 1.56 con Se = 33.3 kpsi.
  assert punto.n_local == pytest.approx(1.56, rel=0.03)


def test_el_minimo_global_esta_en_el_extremo_derecho_del_chavetero(
  resultado
):
  chaveta = next(
    c for c in resultado.chavetas
    if c.elemento.nombre == "Engrane 4"
  )

  # El ejemplo solo verifica el extremo izquierdo del chavetero
  # (M = 3750 lbf·in). El programa también evalúa el extremo
  # derecho, donde el momento es mayor (M ≈ 4143 lbf·in).
  assert resultado.punto_critico.punto.x == pytest.approx(
    chaveta.fin, abs=1e-6
  )
  assert resultado.criterio_gobernante == "goodman"
  assert resultado.n_eje == pytest.approx(1.405, rel=0.01)
  assert not resultado.cumple

