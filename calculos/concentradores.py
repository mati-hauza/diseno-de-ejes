from dataclasses import dataclass, field
from math import sqrt

from modelo.unidades import longitud_desde_m

from datos.concentradores import (
  TABLA_HOMBROS,
  TABLA_RANURAS,
  VALORES_TABLA_7_1
)


def _texto_posicion(eje, x):
  """Formatea una posición interna en la unidad del usuario."""
  return f"{longitud_desde_m(x, eje.sistema):.6g}"


@dataclass
class Concentrador:
  tipo: str
  nombre: str
  posicion: float
  inicio: float
  fin: float
  lado: int

  geometria: dict
  relaciones: dict
  figura: str
  interpolacion: str

  KtN: float
  KtB: float
  Kts: float

  q: float
  qs: float

  KfN: float
  KfB: float
  Kfs: float

  radio: float | None
  fuente: str
  advertencias: list = field(default_factory=list)
  elemento: object | None = None

  @property
  def es_puntual(self):
    return abs(self.fin - self.inicio) < 1e-15


# ----------------------------------------------------------------------
# Interpolación.
# ----------------------------------------------------------------------

def _interpolar_curva(puntos, x, descripcion):
  if not puntos:
    raise ValueError(
      f"La curva {descripcion} no tiene datos."
    )

  x_min = puntos[0][0]
  x_max = puntos[-1][0]

  if not x_min <= x <= x_max:
    raise ValueError(
      f"El valor {x:.6g} está fuera del rango [{x_min:.6g}, "
      f"{x_max:.6g}] de la curva {descripcion}. No se "
      "extrapola."
    )

  for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
    if x1 <= x <= x2:
      if abs(x2 - x1) < 1e-15:
        return y1
      return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

  return puntos[-1][1]


def _interpolar_tabla(tabla, x, curva, nombre_tabla):
  x_min = tabla["x_min"]
  x_max = tabla["x_max"]

  if not x_min <= x <= x_max:
    raise ValueError(
      f"El valor {x:.6g} está fuera del rango [{x_min:.6g}, "
      f"{x_max:.6g}] de {nombre_tabla}. No se extrapola."
    )

  curvas = tabla["curvas"]
  valores = sorted(curvas)

  if curva < valores[0] or curva > valores[-1]:
    raise ValueError(
      f"La relación {tabla['variable_curva']}={curva:.6g} está "
      f"fuera del rango [{valores[0]:.6g}, {valores[-1]:.6g}] "
      f"de {nombre_tabla}. No se extrapola."
    )

  for i, valor in enumerate(valores):
    if abs(valor - curva) < 1e-12:
      return _interpolar_curva(
        curvas[valor],
        x,
        f"{nombre_tabla} ({tabla['variable_curva']}={valor:g})"
      )

    if valor > curva:
      inferior = valores[i - 1]
      superior = valor

      y_inf = _interpolar_curva(
        curvas[inferior], x,
        f"{nombre_tabla} ({tabla['variable_curva']}={inferior:g})"
      )
      y_sup = _interpolar_curva(
        curvas[superior], x,
        f"{nombre_tabla} ({tabla['variable_curva']}={superior:g})"
      )

      factor = (curva - inferior) / (superior - inferior)
      return y_inf + (y_sup - y_inf) * factor

  return _interpolar_curva(
    curvas[valores[-1]], x,
    f"{nombre_tabla} ({tabla['variable_curva']}={valores[-1]:g})"
  )


# ----------------------------------------------------------------------
# Sensibilidad a la entalla.
# ----------------------------------------------------------------------

def parametros_neuber(Sut):
  """
  Devuelve sqrt(a) y sqrt(a_s) en sqrt(in), con Sut en Pa.
  """
  Sut_kpsi = Sut / 6.894757e6

  sqrt_a = (
    0.246
    - 3.08e-3 * Sut_kpsi
    + 1.51e-5 * Sut_kpsi**2
    - 2.67e-8 * Sut_kpsi**3
  )

  sqrt_as = (
    0.190
    - 2.51e-3 * Sut_kpsi
    + 1.35e-5 * Sut_kpsi**2
    - 2.67e-8 * Sut_kpsi**3
  )

  if sqrt_a <= 0 or sqrt_as <= 0:
    raise ValueError(
      f"Sut={Sut / 1e6:.3f} MPa está fuera del rango de validez "
      "de las relaciones de Neuber."
    )

  return sqrt_a, sqrt_as


def sensibilidad_neuber(r, Sut):
  """Devuelve q y q_s para un radio r en metros."""
  sqrt_a, sqrt_as = parametros_neuber(Sut)

  r_in = r / 0.0254

  if r_in <= 0:
    raise ValueError("El radio de entalla debe ser positivo.")

  q = 1.0 / (1.0 + sqrt_a / sqrt(r_in))
  qs = 1.0 / (1.0 + sqrt_as / sqrt(r_in))

  return q, qs


def _factores_fatiga(KtN, KtB, Kts, q, qs):
  return (
    1.0 + q * (KtN - 1.0),
    1.0 + q * (KtB - 1.0),
    1.0 + qs * (Kts - 1.0)
  )


# ----------------------------------------------------------------------
# Cálculo de concentradores.
# ----------------------------------------------------------------------

def calcular_concentradores(eje, chavetas):
  if eje.material is None:
    raise ValueError(
      "Se necesita el material del eje para calcular los "
      "concentradores."
    )

  concentradores = []

  for escalonamiento in eje.escalonamientos:
    concentradores.append(
      _concentrador_escalonamiento(eje, escalonamiento)
    )

  for ranura in eje.ranuras:
    concentradores.append(
      _concentrador_ranura(eje, ranura)
    )

  for chaveta in chavetas:
    if chaveta.existe:
      concentradores.append(
        _concentrador_chaveta(eje, chaveta)
      )

  _verificar_solape(concentradores)

  return concentradores


def _concentrador_escalonamiento(eje, escalonamiento):
  izquierdo = eje.tramo_izquierdo(escalonamiento.x_s)
  derecho = eje.tramo_derecho(escalonamiento.x_s)

  if izquierdo is None or derecho is None:
    raise ValueError(
      f"No se pudieron determinar los tramos del escalonamiento "
      f"x={escalonamiento.x_s}."
    )

  if derecho.d < izquierdo.d:
    d = derecho.d
    D = izquierdo.d
    lado = +1
  else:
    d = izquierdo.d
    D = derecho.d
    lado = -1

  r = escalonamiento.r
  D_sobre_d = D / d
  r_sobre_d = r / d

  KtN = _interpolar_tabla(
    TABLA_HOMBROS["A-15-7"], r_sobre_d, D_sobre_d, "A-15-7"
  )
  Kts = _interpolar_tabla(
    TABLA_HOMBROS["A-15-8"], r_sobre_d, D_sobre_d, "A-15-8"
  )
  KtB = _interpolar_tabla(
    TABLA_HOMBROS["A-15-9"], r_sobre_d, D_sobre_d, "A-15-9"
  )

  q, qs = sensibilidad_neuber(r, eje.material.Sut)
  KfN, KfB, Kfs = _factores_fatiga(KtN, KtB, Kts, q, qs)

  return Concentrador(
    tipo="escalonamiento",
    nombre=(
      f"Escalonamiento x={_texto_posicion(eje, escalonamiento.x_s)}"
    ),
    posicion=escalonamiento.x_s,
    inicio=escalonamiento.x_s,
    fin=escalonamiento.x_s,
    lado=lado,
    geometria={"D": D, "d": d, "r": r},
    relaciones={"D/d": D_sobre_d, "r/d": r_sobre_d},
    figura="A-15-7, A-15-8, A-15-9",
    interpolacion="bilineal lineal",
    KtN=KtN,
    KtB=KtB,
    Kts=Kts,
    q=q,
    qs=qs,
    KfN=KfN,
    KfB=KfB,
    Kfs=Kfs,
    radio=r,
    fuente="Shigley, figuras A-15-7/8/9",
    advertencias=[]
  )


def _concentrador_ranura(eje, ranura):
  tramo = eje.tramo_en(ranura.posicion)

  if tramo is None:
    raise ValueError(
      f"La ranura x={ranura.posicion} no pertenece a un tramo."
    )

  if not ranura.con_geometria:
    valores = VALORES_TABLA_7_1["ranura"]

    return Concentrador(
      tipo="ranura",
      nombre=f"Ranura x={_texto_posicion(eje, ranura.posicion)}",
      posicion=ranura.posicion,
      inicio=ranura.posicion,
      fin=ranura.posicion,
      lado=0,
      geometria={},
      relaciones={},
      figura="Tabla 7-1",
      interpolacion="no aplica",
      KtN=valores["KtN"],
      KtB=valores["KtB"],
      Kts=valores["Kts"],
      q=1.0,
      qs=1.0,
      KfN=valores["KtN"],
      KfB=valores["KtB"],
      Kfs=valores["Kts"],
      radio=None,
      fuente="Shigley, tabla 7-1",
      advertencias=[
        "La ranura no tiene geometría informada; se usaron "
        "valores iniciales de la tabla 7-1."
      ]
    )

  a = ranura.ancho
  t = ranura.profundidad
  r = ranura.radio
  D_local = tramo.d
  d_r = D_local - 2 * t

  a_sobre_t = a / t
  r_sobre_t = r / t

  KtN = _interpolar_tabla(
    TABLA_RANURAS["A-15-16"], a_sobre_t, r_sobre_t, "A-15-16"
  )
  KtB = KtN
  Kts = _interpolar_tabla(
    TABLA_RANURAS["A-15-17"], a_sobre_t, r_sobre_t, "A-15-17"
  )

  q, qs = sensibilidad_neuber(r, eje.material.Sut)
  KfN, KfB, Kfs = _factores_fatiga(KtN, KtB, Kts, q, qs)

  return Concentrador(
    tipo="ranura",
    nombre=f"Ranura x={_texto_posicion(eje, ranura.posicion)}",
    posicion=ranura.posicion,
    inicio=ranura.inicio,
    fin=ranura.fin,
    lado=0,
    geometria={
      "a": a, "t": t, "r": r,
      "D": D_local, "d_r": d_r
    },
    relaciones={"a/t": a_sobre_t, "r/t": r_sobre_t},
    figura="A-15-16, A-15-17",
    interpolacion="bilineal lineal",
    KtN=KtN,
    KtB=KtB,
    Kts=Kts,
    q=q,
    qs=qs,
    KfN=KfN,
    KfB=KfB,
    Kfs=Kfs,
    radio=r,
    fuente="Shigley, figuras A-15-16/17",
    advertencias=[]
  )


def _concentrador_chaveta(eje, chaveta):
  advertencias = []
  d = chaveta.d
  r_f = chaveta.elemento.r_f

  if r_f is not None:
    r_f_sobre_d = r_f / d

    if 0.005 <= r_f_sobre_d <= 0.04:
      x = 0.1 / r_f_sobre_d

      KtB = max(
        1.6,
        1.426 + 0.1643 * x - 0.0019 * x**2
      )

      Kts = max(
        1.7,
        1.953 + 0.1434 * x - 0.0021 * x**2
      )

      KtN = KtB

      q, qs = sensibilidad_neuber(r_f, eje.material.Sut)
      fuente = "Peterson, Chart 5.1 y 5.2"

      advertencias.append(
        "Peterson no da un factor específico para carga axial; "
        "se adopta Kt,N = Kt,B como aproximación académica."
      )
    else:
      advertencias.append(
        f"r_f/d={r_f_sobre_d:.6g} está fuera del rango de "
        "Peterson [0.005, 0.04]; se usan los valores iniciales "
        "de la tabla 7-1."
      )
      KtN, KtB, Kts, q, qs, fuente = _chaveta_tabla_7_1(
        eje, d, advertencias
      )
  else:
    KtN, KtB, Kts, q, qs, fuente = _chaveta_tabla_7_1(
      eje, d, advertencias
    )

  if chaveta.m > 1:
    KtN = chaveta.m * KtN
    KtB = chaveta.m * KtB
    Kts = chaveta.m * Kts

    KfN, KfB, Kfs = _factores_fatiga(
      KtN, KtB, Kts, q, qs
    )

    advertencias.append(
      f"El elemento {chaveta.elemento.nombre} tiene "
      f"{chaveta.m} chaveteros. La multiplicación de Kt por m "
      "es una aproximación académica; no se encontró una "
      "relación publicada para varios chaveteros simultáneos."
    )
  else:
    KfN, KfB, Kfs = _factores_fatiga(KtN, KtB, Kts, q, qs)

  a = chaveta.a
  if d > 0:
    relacion = a / d
    if relacion < 0.2 or relacion > 0.3:
      advertencias.append(
        f"a/d={relacion:.3f} se aparta de 0.25; los valores de "
        "Peterson son aproximados."
      )

  advertencias.append(
    "El chavetero se modela con el diámetro bruto del tramo, "
    "sin descontar la profundidad, y con el mismo Kf en todo su "
    "intervalo. Es una aproximación conservadora."
  )

  return Concentrador(
    tipo="chavetero",
    nombre=f"Chavetero de {chaveta.elemento.nombre}",
    posicion=chaveta.posicion,
    inicio=chaveta.inicio,
    fin=chaveta.fin,
    lado=0,
    geometria={
      "m": chaveta.m,
      "a": chaveta.a,
      "l": chaveta.l,
      "r_e": chaveta.r_e,
      "r_f": r_f,
      "d": d
    },
    relaciones={
      "a/d": a / d if d > 0 else float("nan"),
      "r_f/d": (r_f / d) if r_f is not None else 0.02
    },
    figura=fuente,
    interpolacion="fórmulas de Peterson",
    KtN=KtN,
    KtB=KtB,
    Kts=Kts,
    q=q,
    qs=qs,
    KfN=KfN,
    KfB=KfB,
    Kfs=Kfs,
    radio=r_f if r_f is not None else 0.02 * d,
    fuente=fuente,
    advertencias=advertencias,
    elemento=chaveta.elemento
  )


def _chaveta_tabla_7_1(eje, d, advertencias):
  valores = VALORES_TABLA_7_1["chavetero"]
  r_f = valores["r_f_sobre_d"] * d

  q, qs = sensibilidad_neuber(r_f, eje.material.Sut)

  advertencias.extend([
    "Se usaron los valores iniciales de la tabla 7-1 de "
    "Shigley para el chavetero.",
    "No se usaron las gráficas de Peterson."
  ])

  return (
    valores["KtN"],
    valores["KtB"],
    valores["Kts"],
    q,
    qs,
    "Shigley, tabla 7-1"
  )


def _verificar_solape(concentradores):
  tolerancia = 1e-12

  for i, primero in enumerate(concentradores):
    for segundo in concentradores[i + 1:]:
      if max(primero.inicio, segundo.inicio) <= min(
        primero.fin, segundo.fin
      ) + tolerancia:
        raise ValueError(
          f"Los concentradores '{primero.nombre}' y "
          f"'{segundo.nombre}' están activos en la misma "
          "posición. No se admite su solape."
        )
