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


def test_eje_rechaza_longitud_no_finita():
  with pytest.raises(ValueError, match="finit"):
    Eje.crear(float("nan"), SistemaUnidades.SI)


def test_apoyo_rechaza_medidas_no_finitas():
  with pytest.raises(ValueError, match="finit"):
    Apoyo.crear(
      "A", float("inf"), 50, True, SistemaUnidades.SI
    )


def test_elemento_rechaza_medidas_no_finitas():
  with pytest.raises(ValueError, match="finit"):
    Elemento.crear(
      "E", 500, float("nan"), SistemaUnidades.SI
    )


def test_validar_rechaza_longitud_no_finita(eje_si):
  eje_si.longitud = float("nan")

  with pytest.raises(ValueError, match="finit"):
    eje_si.validar()


def test_validar_rechaza_apoyo_no_finito(eje_si):
  eje_si.apoyos[0].ancho = float("nan")

  with pytest.raises(ValueError, match="finit"):
    eje_si.validar()


def test_validar_rechaza_elemento_no_finito(eje_si):
  eje_si.agregar_elemento(
    Elemento.crear("E", 500, 100, SistemaUnidades.SI)
  )
  eje_si.elementos[0].ancho = float("nan")

  with pytest.raises(ValueError, match="finit"):
    eje_si.validar()


def test_apoyos_con_nombres_duplicados_no_son_validos():
  eje = Eje.crear(1000, SistemaUnidades.SI)
  eje.agregar_apoyo(
    Apoyo.crear("A", 200, 50, True, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("A", 800, 50, False, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="nombres de los apoyos"):
    eje.validar()


def test_elemento_sobre_apoyo_no_es_valido(eje_si):
  eje_si.agregar_elemento(
    Elemento.crear("E", 200, 100, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="superponerse con el apoyo"):
    eje_si.validar()


def test_elementos_superpuestos_no_son_validos(eje_si):
  eje_si.agregar_elemento(
    Elemento.crear("E1", 400, 200, SistemaUnidades.SI)
  )
  eje_si.agregar_elemento(
    Elemento.crear("E2", 500, 200, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="no pueden superponerse"):
    eje_si.validar()


@pytest.mark.parametrize(
  "posicion, ancho",
  [
    (50, 100),
    (950, 100),
  ]
)
def test_elemento_al_ras_de_un_extremo_no_es_valido(
  eje_si, posicion, ancho
):
  eje_si.agregar_elemento(
    Elemento.crear("E", posicion, ancho, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="al ras"):
    eje_si.validar()


def test_centros_de_apoyos_coincidentes_no_son_validos():
  eje = Eje.crear(1000, SistemaUnidades.SI)
  eje.agregar_apoyo(
    Apoyo.crear("A", 500, 50, True, SistemaUnidades.SI)
  )
  eje.agregar_apoyo(
    Apoyo.crear("B", 500, 50, False, SistemaUnidades.SI)
  )

  with pytest.raises(ValueError, match="centros de los apoyos"):
    eje.validar()


@pytest.mark.parametrize(
  "metodo, valor, mensaje",
  [
    ("agregar_apoyo", "A", "Apoyo"),
    ("agregar_elemento", "E", "Elemento"),
    ("agregar_carga", "P", "Carga"),
    ("agregar_momento", "M", "Momento"),
  ]
)
def test_eje_rechaza_objetos_del_tipo_equivocado(
  eje_si, metodo, valor, mensaje
):
  with pytest.raises(TypeError, match=mensaje):
    getattr(eje_si, metodo)(valor)


def test_eje_rechaza_carga_normal_como_distribuida(eje_si):
  carga = CargaCartesiana.crear(
    "P", 500, SistemaUnidades.SI, Fy=-1000
  )

  with pytest.raises(TypeError, match="CargaDistribuida"):
    eje_si.agregar_carga_distribuida(carga)


def test_eje_no_acepta_carga_distribuida_en_agregar_carga(eje_si):
  carga = CargaDistribuida.crear(
    "q", 400, 600, SistemaUnidades.SI, qy=-10
  )

  with pytest.raises(TypeError, match="agregar_carga_distribuida"):
    eje_si.agregar_carga(carga)


def test_elemento_rechaza_objetos_del_tipo_equivocado():
  elemento = Elemento.crear(
    "E", 500, 100, SistemaUnidades.SI
  )

  with pytest.raises(TypeError, match="Carga"):
    elemento.agregar_carga("P")

  with pytest.raises(TypeError, match="Momento"):
    elemento.agregar_momento("M")
