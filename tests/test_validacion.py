import pytest

from modelo.apoyo import Apoyo
from modelo.carga import CargaCartesiana, CargaDistribuida
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades


def test_eje_sin_apoyos_no_es_valido():
  eje = Eje.crear(1000, SistemaUnidades.SI)

  with pytest.raises(ValueError, match="exactamente dos apoyos"):
    eje.validar()


def test_eje_con_dos_apoyos_fijos_no_es_valido():
  eje = Eje.crear(1000, SistemaUnidades.SI)
  eje.agregar_apoyo(
    Apoyo.crear("A", 200, 50, True, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 800, 50, True, SistemaUnidades.SI)
  )

  with pytest.raises(
    ValueError,
    match="exactamente un apoyo fijo axial"
  ):
    eje.validar()


def test_apoyos_superpuestos_no_son_validos():
  eje = Eje.crear(1000, SistemaUnidades.SI)
  eje.agregar_apoyo(
    Apoyo.crear("A", 200, 200, True, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 300, 200, False, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="no pueden superponerse"):
    eje.validar()


def test_carga_fuera_del_elemento_no_se_puede_agregar():
  elemento = Elemento.crear(
    "Engranaje", 500, 100, SistemaUnidades.SI
  )
  carga = CargaCartesiana.crear(
    "P", 700, SistemaUnidades.SI, Fy=-1000
  )

  with pytest.raises(ValueError, match="dentro del elemento"):
    elemento.agregar_carga(carga)


def test_momento_fuera_del_elemento_no_se_puede_agregar():
  elemento = Elemento.crear(
    "Engranaje", 500, 100, SistemaUnidades.SI
  )
  momento = Momento.crear(
    "M", 700, SistemaUnidades.SI, Mz=1000
  )

  with pytest.raises(ValueError, match="dentro del elemento"):
    elemento.agregar_momento(momento)


def test_carga_distribuida_fuera_del_eje_no_es_valida(eje_si):
  eje_si.agregar_carga_distribuida(
    CargaDistribuida.crear(
      "q", 900, 1100, SistemaUnidades.SI, qy=-10
    )
  )

  with pytest.raises(ValueError, match="fuera del eje"):
    eje_si.validar()
