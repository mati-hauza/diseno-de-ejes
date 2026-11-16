import pytest

from modelo.apoyo import Apoyo
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.escalonamiento import Escalonamiento
from modelo.ranura import Ranura
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades


S = SistemaUnidades.SI


def _eje_con_tramos():
  eje = Eje.crear(1000, S)
  eje.agregar_tramo(Tramo.crear(0, 400, 40, S))
  eje.agregar_tramo(Tramo.crear(400, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))
  return eje


def test_tramo_crear_convierte_a_metros():
  tramo = Tramo.crear(100, 500, 40, S)

  assert tramo.x_inicio == pytest.approx(0.1)
  assert tramo.x_fin == pytest.approx(0.5)
  assert tramo.d == pytest.approx(0.04)
  assert tramo.longitud == pytest.approx(0.4)


def test_escalonamiento_crear_convierte_a_metros():
  escalonamiento = Escalonamiento.crear(400, 2, S)

  assert escalonamiento.x_s == pytest.approx(0.4)
  assert escalonamiento.r == pytest.approx(0.002)


def test_ranura_sin_geometria_es_puntual():
  ranura = Ranura.crear(500, S)

  assert not ranura.con_geometria
  assert ranura.inicio == pytest.approx(0.5)
  assert ranura.fin == pytest.approx(0.5)


def test_ranura_con_geometria_parcial_es_invalida():
  with pytest.raises(ValueError, match="ancho"):
    Ranura.crear(500, S, ancho=4)


def test_eje_valido_con_tramos_y_escalonamiento():
  eje = _eje_con_tramos()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 2, S)
  )

  assert eje.validar() is True


def test_tramos_con_hueco_no_son_validos():
  eje = Eje.crear(1000, S)
  eje.agregar_tramo(Tramo.crear(0, 400, 40, S))
  eje.agregar_tramo(Tramo.crear(500, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))

  with pytest.raises(ValueError, match="contiguos"):
    eje.validar()


def test_escalonamiento_que_no_coincide_con_tramos_es_invalido():
  eje = _eje_con_tramos()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(450, 2, S)
  )

  with pytest.raises(ValueError, match="límite entre dos tramos"):
    eje.validar()


def test_escalonamiento_con_radio_excesivo_es_invalido():
  eje = _eje_con_tramos()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 6, S)
  )

  with pytest.raises(ValueError, match="no puede superar"):
    eje.validar()


def test_escalonamiento_entre_tramos_iguales_es_invalido():
  eje = Eje.crear(1000, S)
  eje.agregar_tramo(Tramo.crear(0, 400, 40, S))
  eje.agregar_tramo(Tramo.crear(400, 1000, 40, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 2, S)
  )

  with pytest.raises(ValueError, match="diámetros distintos"):
    eje.validar()


def test_elemento_no_puede_cruzar_un_escalonamiento():
  eje = _eje_con_tramos()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 2, S)
  )
  eje.agregar_elemento(
    Elemento.crear("E", 450, 200, S)
  )

  with pytest.raises(ValueError, match="un solo tramo"):
    eje.validar()


def test_diametro_local_respeta_lados_del_escalonamiento():
  eje = _eje_con_tramos()
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 2, S)
  )

  assert eje.diametro_local(0.4, -1) == pytest.approx(0.04)
  assert eje.diametro_local(0.4, +1) == pytest.approx(0.05)


def test_cambio_de_diametro_sin_escalonamiento_es_invalido():
  eje = _eje_con_tramos()

  with pytest.raises(
    ValueError,
    match="definido por un escalonamiento"
  ):
    eje.validar()


def test_filetes_en_los_dos_extremos_no_superan_la_longitud():
  eje = Eje.crear(1000, S)
  eje.agregar_tramo(Tramo.crear(0, 400, 50, S))
  eje.agregar_tramo(Tramo.crear(400, 415, 30, S))
  eje.agregar_tramo(Tramo.crear(415, 1000, 50, S))
  eje.agregar_apoyo(Apoyo.crear("A", 200, 50, True, S))
  eje.agregar_apoyo(Apoyo.crear("B", 800, 50, False, S))
  eje.agregar_escalonamiento(
    Escalonamiento.crear(400, 8, S)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(415, 8, S)
  )

  with pytest.raises(ValueError, match="superan su longitud"):
    eje.validar()
