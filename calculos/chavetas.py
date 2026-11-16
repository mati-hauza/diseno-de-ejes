from dataclasses import dataclass, field
from math import ceil, inf

from .transformaciones import obtener_acciones_puntuales


@dataclass
class Chaveta:
  elemento: object
  Te: float
  d: float
  a: float
  b: float
  h: float

  material_chaveta: object
  material_cubo: object
  Sy_chaveta: float
  Sy_cubo: float
  Sy_eje: float
  Sy_contacto: float

  Ft: float
  Ft_i: float
  Ac: float
  tau_c: float
  Ssy: float
  n_c: float
  Ap: float
  sigma_p: float
  n_p: float

  l_req1: float
  l_max: float
  m: int
  l: float

  n_chaveta: float
  advertencias: list = field(default_factory=list)

  @property
  def posicion(self):
    return self.elemento.posicion

  @property
  def inicio(self):
    if self.l <= 0:
      return self.elemento.posicion
    return self.elemento.posicion - self.l / 2

  @property
  def fin(self):
    if self.l <= 0:
      return self.elemento.posicion
    return self.elemento.posicion + self.l / 2

  @property
  def r_e(self):
    return self.a / 2

  @property
  def existe(self):
    return self.l > 0


def _torque_del_elemento(eje, elemento):
  tolerancia = 1e-9 * max(eje.longitud, 1.0)

  acciones = obtener_acciones_puntuales(eje)

  suma = sum(
    a.Mx
    for a in acciones
    if (
      elemento.inicio - tolerancia
      <= a.posicion
      <= elemento.fin + tolerancia
    )
  )

  return abs(suma)


def dimensionar_chavetas(eje):
  """
  Dimensiona todas las chavetas del eje.

  Devuelve una lista de objetos Chaveta, uno por elemento con
  usa_chaveta=True.
  """
  if eje.material is None:
    raise ValueError(
      "Se necesita el material del eje para dimensionar las "
      "chavetas."
    )

  if eje.n_min is None:
    raise ValueError(
      "Se necesita n_min para dimensionar las chavetas."
    )

  chavetas = []

  for elemento in eje.elementos:
    if not elemento.usa_chaveta:
      continue

    chavetas.append(
      _dimensionar_chaveta(eje, elemento)
    )

  _validar_chaveteros(eje, chavetas)

  return chavetas


def _dimensionar_chaveta(eje, elemento):
  advertencias = []

  material_chaveta = elemento.material_chaveta
  material_cubo = elemento.material_cubo

  if material_chaveta is None or material_cubo is None:
    raise ValueError(
      f"El elemento {elemento.nombre} debe informar los "
      "materiales de chaveta y cubo."
    )

  d = eje.diametro_local(elemento.posicion)
  a = elemento.a
  Sy_chaveta = material_chaveta.Sy
  Sy_cubo = material_cubo.Sy
  Sy_eje = eje.material.Sy

  Sy_contacto = min(Sy_chaveta, Sy_eje, Sy_cubo)

  n_chaveta = (
    elemento.n_chaveta
    if elemento.n_chaveta is not None
    else eje.n_min
  )

  Te = _torque_del_elemento(eje, elemento)
  l_max = 0.9 * elemento.ancho

  if Te <= 1e-12:
    advertencias.append(
      f"El elemento {elemento.nombre} no transmite torque; "
      "no se dimensiona chaveta."
    )

    return Chaveta(
      elemento=elemento,
      Te=0.0,
      d=d,
      a=a,
      b=a,
      h=a,
      material_chaveta=material_chaveta,
      material_cubo=material_cubo,
      Sy_chaveta=Sy_chaveta,
      Sy_cubo=Sy_cubo,
      Sy_eje=Sy_eje,
      Sy_contacto=Sy_contacto,
      Ft=0.0,
      Ft_i=0.0,
      Ac=0.0,
      tau_c=0.0,
      Ssy=0.577 * Sy_chaveta,
      n_c=inf,
      Ap=0.0,
      sigma_p=0.0,
      n_p=inf,
      l_req1=0.0,
      l_max=l_max,
      m=1,
      l=0.0,
      n_chaveta=n_chaveta,
      advertencias=advertencias
    )

  l_c1 = (
    2 * Te * n_chaveta
    / (0.577 * d * a * Sy_chaveta)
  )

  l_p1 = (
    4 * Te * n_chaveta
    / (d * a * Sy_contacto)
  )

  l_req1 = max(l_c1, l_p1)

  m = max(1, ceil(l_req1 / l_max))

  for _ in range(100000):
    Ti = Te / m

    l_c = (
      2 * Ti * n_chaveta
      / (0.577 * d * a * Sy_chaveta)
    )

    l_p = (
      4 * Ti * n_chaveta
      / (d * a * Sy_contacto)
    )

    l = max(l_c, l_p)

    if l <= l_max + 1e-12 * max(l_max, 1.0):
      break

    m += 1
  else:
    raise ValueError(
      f"No se pudo dimensionar la chaveta de "
      f"{elemento.nombre}: se requiere una cantidad de "
      "chavetas excesiva."
    )

  if l > 1.5 * d:
    advertencias.append(
      f"La chaveta de {elemento.nombre} tiene l={l * 1000:.3f} mm "
      f"> 1.5d={1.5 * d * 1000:.3f} mm. Una chaveta muy larga "
      "tiene reparto de carga no uniforme."
    )

  relacion = a / d
  if relacion < 0.2 or relacion > 0.3:
    advertencias.append(
      f"En {elemento.nombre}, a/d={relacion:.3f}; se "
      "recomienda a ≈ d/4."
    )

  if Sy_chaveta >= Sy_eje:
    advertencias.append(
      f"La chaveta de {elemento.nombre} tiene Sy mayor o igual "
      "que la del eje."
    )

  Ft = 2 * Te / d
  Ft_i = 2 * Ti / d

  Ac = a * l
  tau_c = Ft_i / Ac
  Ssy = 0.577 * Sy_chaveta
  n_c = Ssy / tau_c if tau_c > 0 else inf

  Ap = (a / 2) * l
  sigma_p = Ft_i / Ap
  n_p = Sy_contacto / sigma_p if sigma_p > 0 else inf

  return Chaveta(
    elemento=elemento,
    Te=Te,
    d=d,
    a=a,
    b=a,
    h=a,
    material_chaveta=material_chaveta,
    material_cubo=material_cubo,
    Sy_chaveta=Sy_chaveta,
    Sy_cubo=Sy_cubo,
    Sy_eje=Sy_eje,
    Sy_contacto=Sy_contacto,
    Ft=Ft,
    Ft_i=Ft_i,
    Ac=Ac,
    tau_c=tau_c,
    Ssy=Ssy,
    n_c=n_c,
    Ap=Ap,
    sigma_p=sigma_p,
    n_p=n_p,
    l_req1=l_req1,
    l_max=l_max,
    m=m,
    l=l,
    n_chaveta=n_chaveta,
    advertencias=advertencias
  )


def _validar_chaveteros(eje, chavetas):
  """
  Comprueba que los chaveteros no se solapen con otros
  concentradores ni con apoyos, y que respeten la separación
  d/10 respecto de los filetes de escalonamiento.
  """
  errores = []
  tolerancia = 1e-9 * max(eje.longitud, 1.0)

  activas = [c for c in chavetas if c.existe]

  for chaveta in activas:
    elemento = chaveta.elemento

    if chaveta.l > 0.9 * elemento.ancho + tolerancia:
      errores.append(
        f"El chavetero de {elemento.nombre} supera 0.9·Le."
      )

    for escalonamiento in eje.escalonamientos:
      distancia = min(
        abs(chaveta.inicio - escalonamiento.x_s),
        abs(chaveta.fin - escalonamiento.x_s)
      )

      separacion = chaveta.d / 10

      if (
        chaveta.inicio - tolerancia
        <= escalonamiento.x_s
        <= chaveta.fin + tolerancia
      ):
        errores.append(
          f"El chavetero de {elemento.nombre} contiene el "
          f"escalonamiento x={escalonamiento.x_s}."
        )
      elif distancia < separacion - tolerancia:
        errores.append(
          f"El chavetero de {elemento.nombre} está a "
          f"{distancia * 1000:.3f} mm del escalonamiento "
          f"x={escalonamiento.x_s}; se exige al menos "
          f"d/10={separacion * 1000:.3f} mm."
        )

    for ranura in eje.ranuras:
      if max(chaveta.inicio, ranura.inicio) <= min(
        chaveta.fin, ranura.fin
      ):
        errores.append(
          f"El chavetero de {elemento.nombre} se superpone con "
          "una ranura."
        )

    for apoyo in eje.apoyos:
      if max(chaveta.inicio, apoyo.inicio) <= min(
        chaveta.fin, apoyo.fin
      ):
        errores.append(
          f"El chavetero de {elemento.nombre} se superpone con "
          f"el apoyo {apoyo.nombre}."
        )

    for otra in activas:
      if otra is chaveta:
        continue
      if otra.elemento is elemento:
        continue
      if max(chaveta.inicio, otra.inicio) <= min(
        chaveta.fin, otra.fin
      ):
        errores.append(
          f"El chavetero de {elemento.nombre} se superpone con "
          f"el de {otra.elemento.nombre}."
        )

  if errores:
    raise ValueError("\n".join(errores))
