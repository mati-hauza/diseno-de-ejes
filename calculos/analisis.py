from dataclasses import dataclass, field
from math import inf, isfinite, sqrt

from .chavetas import dimensionar_chavetas
from .concentradores import calcular_concentradores
from .criterios import aplicar_criterios, obtener_criterios
from .discretizacion import (
  concentrador_activo,
  construir_puntos,
  intervalos_continuos
)
from .esfuerzos import calcular_esfuerzos
from .fluencia import calcular_fluencia
from .geometria import diametro_local
from .marin import factores_marin
from .reacciones import calcular_reacciones
from .solicitaciones import calcular_solicitaciones
from .validacion import validar_entradas


@dataclass
class ResultadoPunto:
  punto: object
  esfuerzos: object
  marin: dict
  factores: dict
  n_local: float
  gobernante: str
  fluencia: dict | None = None


@dataclass
class ResultadoAnalisis:
  eje: object
  chavetas: list
  concentradores: list
  reacciones: list
  solicitaciones: object
  puntos: list
  criterios: list

  minimos: dict
  n_eje: float
  punto_critico: ResultadoPunto | None
  criterio_gobernante: str | None

  cumple_eje: bool
  cumple_chavetas: bool
  cumple: bool
  no_verificable: bool

  advertencias: list = field(default_factory=list)


def analizar_eje(eje):
  if eje.material is None:
    raise ValueError(
      "Se necesita el material del eje para el análisis."
    )

  if eje.n_min is None:
    raise ValueError(
      "Se necesita el factor de seguridad mínimo n_min."
    )

  if not eje.tramos:
    raise ValueError(
      "Se necesita al menos un tramo para el análisis."
    )

  acciones = validar_entradas(eje)

  chavetas = dimensionar_chavetas(eje)
  concentradores = calcular_concentradores(eje, chavetas)

  reacciones, _ = calcular_reacciones(eje, acciones)

  solicitaciones = calcular_solicitaciones(
    eje, acciones=acciones, reacciones=reacciones
  )

  puntos = construir_puntos(
    eje, solicitaciones, concentradores
  )

  resultados = [
    _evaluar_punto(
      eje, solicitaciones, concentradores, eje.material, punto
    )
    for punto in puntos
  ]

  # Mínimos locales dentro de cada intervalo continuo.
  extra = []

  for izquierda, derecha in intervalos_continuos(eje, chavetas):
    if derecha - izquierda <= 1e-12:
      continue

    def funcion(x):
      return _factor_local(
        eje, solicitaciones, concentradores, eje.material,
        x, 0
      )

    x_min, valor_min = _minimo_dorado(
      funcion,
      izquierda,
      derecha,
      1e-6 * eje.longitud
    )

    valor_izq = funcion(izquierda)
    valor_der = funcion(derecha)

    referencia = min(valor_izq, valor_der)

    if (
      izquierda + 1e-9 < x_min < derecha - 1e-9
      and valor_min < referencia - 1e-9 * max(abs(referencia), 1.0)
      and isfinite(valor_min)
    ):
      extra.append(x_min)

  if extra:
    posiciones_existentes = [rp.punto.x for rp in resultados]
    tolerancia_extra = 2e-6 * max(eje.longitud, 1.0)

    for x in extra:
      if any(
        abs(x - existente) <= tolerancia_extra
        for existente in posiciones_existentes
      ):
        continue

      punto = _punto_interior(
        eje, x, concentradores, "mínimo de seguridad"
      )
      resultados.append(
        _evaluar_punto(
          eje, solicitaciones, concentradores, eje.material, punto
        )
      )
      posiciones_existentes.append(x)

  resultados.sort(key=lambda rp: (rp.punto.x, rp.punto.lado))

  criterios = obtener_criterios()

  minimos = _calcular_minimos(resultados, criterios)

  punto_critico = min(
    resultados,
    key=lambda rp: rp.n_local
  )

  n_eje = punto_critico.n_local

  cumple_eje = n_eje >= eje.n_min

  cumple_chavetas = all(
    _chaveta_cumple(chaveta)
    for chaveta in chavetas
  )

  no_verificable = any(
    any(
      not isfinite(valor) and valor != inf
      for valor in rp.factores.values()
    )
    for rp in resultados
  )

  advertencias = list(eje.advertencias)

  for chaveta in chavetas:
    advertencias.extend(chaveta.advertencias)

  for concentrador in concentradores:
    advertencias.extend(concentrador.advertencias)

  return ResultadoAnalisis(
    eje=eje,
    chavetas=chavetas,
    concentradores=concentradores,
    reacciones=reacciones,
    solicitaciones=solicitaciones,
    puntos=resultados,
    criterios=criterios,
    minimos=minimos,
    n_eje=n_eje,
    punto_critico=punto_critico,
    criterio_gobernante=punto_critico.gobernante,
    cumple_eje=cumple_eje,
    cumple_chavetas=cumple_chavetas,
    cumple=(
      cumple_eje and cumple_chavetas and not no_verificable
    ),
    no_verificable=no_verificable,
    advertencias=advertencias
  )


def _evaluar_punto(
  eje,
  solicitaciones,
  concentradores,
  material,
  punto
):
  concentrador = punto.concentrador

  if concentrador is None:
    KfN = KfB = Kfs = 1.0
  else:
    KfN = concentrador.KfN
    KfB = concentrador.KfB
    Kfs = concentrador.Kfs

  esfuerzos = calcular_esfuerzos(
    solicitaciones,
    punto.x,
    punto.lado,
    punto.d,
    KfN=KfN,
    KfB=KfB,
    Kfs=Kfs
  )

  marin = factores_marin(material, punto.d)
  factores = aplicar_criterios(esfuerzos, material, marin["Se"])

  gobernante = min(factores, key=factores.get)
  n_local = factores[gobernante]

  return ResultadoPunto(
    punto=punto,
    esfuerzos=esfuerzos,
    marin=marin,
    factores=factores,
    n_local=n_local,
    gobernante=gobernante,
    fluencia=calcular_fluencia(esfuerzos, material)
  )


def _factor_local(
  eje,
  solicitaciones,
  concentradores,
  material,
  x,
  lado
):
  d = diametro_local(eje, x, lado)
  concentrador = concentrador_activo(
    eje, concentradores, x, lado
  )

  if concentrador is None:
    KfN = KfB = Kfs = 1.0
  else:
    KfN = concentrador.KfN
    KfB = concentrador.KfB
    Kfs = concentrador.Kfs

  esfuerzos = calcular_esfuerzos(
    solicitaciones, x, lado, d,
    KfN=KfN, KfB=KfB, Kfs=Kfs
  )

  marin = factores_marin(material, d)
  factores = aplicar_criterios(esfuerzos, material, marin["Se"])

  return min(factores.values())


def _punto_interior(eje, x, concentradores, discontinuidad):
  from .discretizacion import PuntoEvaluacion

  d = diametro_local(eje, x, 0)
  tramo = eje.tramo_en(x)
  concentrador = concentrador_activo(
    eje, concentradores, x, 0
  )

  return PuntoEvaluacion(
    x=x,
    lado=0,
    d=d,
    tramo=tramo,
    concentrador=concentrador,
    discontinuidad=discontinuidad
  )


def _minimo_dorado(funcion, a, b, tolerancia):
  razon = (sqrt(5) - 1) / 2

  c = b - razon * (b - a)
  d = a + razon * (b - a)

  fc = funcion(c)
  fd = funcion(d)

  while b - a > tolerancia:
    if fc < fd:
      b = d
      d = c
      fd = fc
      c = b - razon * (b - a)
      fc = funcion(c)
    else:
      a = c
      c = d
      fc = fd
      d = a + razon * (b - a)
      fd = funcion(d)

  x = (a + b) / 2

  return x, funcion(x)


def _calcular_minimos(resultados, criterios):
  minimos = {}

  for criterio in criterios:
    mejor = None

    for rp in resultados:
      valor = rp.factores[criterio.clave]

      if mejor is None or valor < mejor[0]:
        mejor = (valor, rp)

    minimos[criterio.clave] = mejor

  return minimos


def _chaveta_cumple(chaveta):
  if not chaveta.existe:
    return True

  return (
    chaveta.n_c >= chaveta.n_chaveta
    and chaveta.n_p >= chaveta.n_chaveta
  )
