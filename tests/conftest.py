import matplotlib

matplotlib.use("Agg", force=True)

import pytest

from modelo.apoyo import Apoyo
from modelo.eje import Eje
from modelo.unidades import SistemaUnidades


@pytest.fixture
def eje_si():
  """Eje de 1000 mm con apoyos en 200 mm y 800 mm."""
  eje = Eje.crear(1000, SistemaUnidades.SI)

  eje.agregar_apoyo(
    Apoyo.crear("A", 200, 50, True, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 800, 50, False, SistemaUnidades.SI)
  )

  return eje


@pytest.fixture
def eje_ingles():
  """Equivalente al eje_si, expresado en pulgadas y libras."""
  eje = Eje.crear(40, SistemaUnidades.INGLES)

  eje.agregar_apoyo(
    Apoyo.crear("A", 8, 2, True, SistemaUnidades.INGLES)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 32, 2, False, SistemaUnidades.INGLES)
  )

  return eje
