from dataclasses import dataclass

from .geometria import diametro_local
from .transformaciones import obtener_acciones_puntuales

NOMBRES_SOLICITACIONES = (
  "N", "Vy", "Vz", "VR", "My", "Mz", "MR", "T"
)


@dataclass
class PuntoEvaluacion:
  x: float
  lado: int
  d: float
  tramo: object
  concentrador: object | None
  discontinuidad: str

  @property
  def es_critico(self):
    return self.discontinuidad != "malla"


def construir_puntos(
  eje,
  solicitaciones,
  concentradores,
  incluir_malla=True
):
  tolerancia = 1e-9 * max(eje.longitud, 1.0)

  criticos = {}

  def agregar(x, lado, discontinuidad):
    x = min(max(x, 0.0), eje.longitud)

    if abs(x) <= tolerancia:
      lado = max(lado, 0)
    if abs(x - eje.longitud) <= tolerancia:
      lado = min(lado, 0)

    clave = (round(x, 10), lado)

    if clave not in criticos:
      criticos[clave] = discontinuidad

  def agregar_lados(x, discontinuidad):
    if abs(x) <= tolerancia or abs(x - eje.longitud) <= tolerancia:
      agregar(x, 0, discontinuidad)
      return

    agregar(x, -1, discontinuidad)
    agregar(x, +1, discontinuidad)

  # Extremos de tramos.
  for tramo in eje.tramos:
    agregar_lados(tramo.x_inicio, "tramo")
    agregar_lados(tramo.x_fin, "tramo")

  # Escalonamientos.
  for escalonamiento in eje.escalonamientos:
    agregar_lados(escalonamiento.x_s, "escalonamiento")

  # Apoyos.
  for apoyo in eje.apoyos:
    agregar_lados(apoyo.posicion, "apoyo")

  # Fuerzas y momentos puntuales.
  for accion in obtener_acciones_puntuales(eje):
    agregar_lados(accion.posicion, "carga puntual")

  # Extremos de cargas distribuidas.
  for carga in eje.cargas_distribuidas:
    agregar_lados(carga.inicio, "carga distribuida")
    agregar_lados(carga.fin, "carga distribuida")

  # Chaveteros y ranuras.
  for concentrador in concentradores:
    if concentrador.tipo in ("chavetero", "ranura") and not concentrador.es_puntual:
      agregar_lados(concentrador.inicio, concentrador.tipo)
      agregar_lados(concentrador.fin, concentrador.tipo)
      agregar(concentrador.posicion, 0, concentrador.tipo)
    elif concentrador.tipo == "ranura":
      agregar_lados(concentrador.posicion, "ranura")

  # Extremos interiores de solicitaciones (aproximación numérica).
  for x in _extremos_solicitaciones(eje, solicitaciones):
    if tolerancia < x < eje.longitud - tolerancia:
      agregar(x, 0, "extremo de solicitación")

  # Malla uniforme.
  if incluir_malla:
    n = eje.n_div
    paso = eje.longitud / n

    for i in range(n + 1):
      x = i * paso

      ocupado = any(
        abs(x - posicion) <= tolerancia
        for posicion, _ in criticos
      )

      if not ocupado:
        agregar(x, 0, "malla")

  puntos = []

  for (x, lado), discontinuidad in criticos.items():
    puntos.append(
      _crear_punto(
        eje, x, lado, discontinuidad, concentradores, tolerancia
      )
    )

  puntos.sort(key=lambda p: (p.x, p.lado))

  return puntos


def concentrador_activo(eje, concentradores, x, lado=0):
  tolerancia = 1e-9 * max(eje.longitud, 1.0)
  return _concentrador_activo(
    concentradores, x, lado, tolerancia
  )


def _crear_punto(
  eje,
  x,
  lado,
  discontinuidad,
  concentradores,
  tolerancia
):
  d = diametro_local(eje, x, lado)
  tramo = eje.tramo_en(x, tolerancia)
  concentrador = _concentrador_activo(
    concentradores, x, lado, tolerancia
  )

  return PuntoEvaluacion(
    x=x,
    lado=lado,
    d=d,
    tramo=tramo,
    concentrador=concentrador,
    discontinuidad=discontinuidad
  )


def _concentrador_activo(concentradores, x, lado, tolerancia):
  activos = []

  for concentrador in concentradores:
    if concentrador.tipo == "escalonamiento":
      if (
        abs(x - concentrador.posicion) <= tolerancia
        and (lado == 0 or lado == concentrador.lado)
      ):
        activos.append(concentrador)

    elif concentrador.es_puntual:
      if abs(x - concentrador.posicion) <= tolerancia:
        activos.append(concentrador)

    else:
      if concentrador.inicio + tolerancia < x < concentrador.fin - tolerancia:
        activos.append(concentrador)
      elif abs(x - concentrador.inicio) <= tolerancia and lado > 0:
        activos.append(concentrador)
      elif abs(x - concentrador.fin) <= tolerancia and lado < 0:
        activos.append(concentrador)

  if len(activos) > 1:
    nombres = ", ".join(c.nombre for c in activos)
    raise ValueError(
      f"Hay más de un concentrador activo en x={x}: {nombres}."
    )

  return activos[0] if activos else None


def _extremos_solicitaciones(eje, solicitaciones):
  """
  Busca extremos interiores de las ocho solicitaciones mediante
  un muestreo local por intervalo continuo.
  """
  posiciones = _posiciones_de_control(eje)

  extremos = []

  for izquierda, derecha in zip(posiciones, posiciones[1:]):
    if derecha - izquierda <= 1e-12:
      continue

    muestras = 21
    xs = [
      izquierda + (derecha - izquierda) * i / (muestras - 1)
      for i in range(muestras)
    ]

    for nombre in NOMBRES_SOLICITACIONES:
      valores = [
        solicitaciones.evaluar(nombre, x)
        for x in xs
      ]

      for i in range(1, muestras - 1):
        pendiente_izq = valores[i] - valores[i - 1]
        pendiente_der = valores[i + 1] - valores[i]

        escala = max(abs(valores[i]), 1.0)

        if (
          pendiente_izq * pendiente_der < 0
          and min(abs(pendiente_izq), abs(pendiente_der)) > 1e-12 * escala
        ):
          extremos.append(xs[i])

  return extremos


def _posiciones_de_control(eje, chavetas=None):
  posiciones = {0.0, eje.longitud}

  for tramo in eje.tramos:
    posiciones.add(tramo.x_inicio)
    posiciones.add(tramo.x_fin)

  for escalonamiento in eje.escalonamientos:
    posiciones.add(escalonamiento.x_s)

  for apoyo in eje.apoyos:
    posiciones.add(apoyo.posicion)

  for accion in obtener_acciones_puntuales(eje):
    posiciones.add(accion.posicion)

  for carga in eje.cargas_distribuidas:
    posiciones.add(carga.inicio)
    posiciones.add(carga.fin)

  for ranura in eje.ranuras:
    posiciones.add(ranura.inicio)
    posiciones.add(ranura.fin)

  for chaveta in (chavetas or []):
    if chaveta.existe:
      posiciones.add(chaveta.inicio)
      posiciones.add(chaveta.fin)

  return sorted(posiciones)


def intervalos_continuos(eje, chavetas=None):
  posiciones = _posiciones_de_control(eje, chavetas)

  return [
    (a, b)
    for a, b in zip(posiciones, posiciones[1:])
    if b - a > 1e-12
  ]
