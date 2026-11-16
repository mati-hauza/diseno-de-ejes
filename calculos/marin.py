from datos.marin import (
  ACABADO_SUPERFICIAL,
  CONFIABILIDAD,
  CONFIABILIDAD_MAX,
  CONFIABILIDAD_MIN,
  SE_PROBETA_LIMITE,
  SUT_LIMITE_PROBETA,
  TEMPERATURA,
  TEMPERATURA_MAX,
  TEMPERATURA_MIN
)


def _interpolar_tabla(puntos, valor, nombre, minimo, maximo):
  if not minimo <= valor <= maximo:
    raise ValueError(
      f"El valor {valor:.6g} está fuera del rango "
      f"[{minimo:.6g}, {maximo:.6g}] de {nombre}."
    )

  for (x1, y1), (x2, y2) in zip(puntos, puntos[1:]):
    if x1 <= valor <= x2:
      if x2 == x1:
        return y1
      return y1 + (y2 - y1) * (valor - x1) / (x2 - x1)

  return puntos[-1][1]


def factor_acabado(material):
  datos = ACABADO_SUPERFICIAL[material.acabado]
  Sut_mpa = material.Sut / 1e6

  return (
    datos["a"] * Sut_mpa ** datos["b"],
    datos["a"],
    datos["b"],
    Sut_mpa
  )


def factor_tamano(d_m):
  """Factor de tamaño para un eje giratorio; d en metros."""
  d_mm = d_m * 1000.0

  if 2.79 <= d_mm <= 51.0:
    return 1.24 * d_mm ** -0.107

  if 51.0 < d_mm <= 254.0:
    return 1.51 * d_mm ** -0.157

  raise ValueError(
    f"El diámetro {d_mm:.3f} mm está fuera del rango "
    "[2.79, 254] mm del factor de tamaño k_b. No se extrapola."
  )


def factor_temperatura(material):
  return _interpolar_tabla(
    TEMPERATURA,
    material.temperatura,
    "la tabla 6-5 de temperatura",
    TEMPERATURA_MIN,
    TEMPERATURA_MAX
  )


def factor_confiabilidad(material):
  return _interpolar_tabla(
    CONFIABILIDAD,
    material.confiabilidad,
    "la tabla 6-4 de confiabilidad",
    CONFIABILIDAD_MIN,
    CONFIABILIDAD_MAX
  )


def limite_probeta(material):
  if material.Sut <= SUT_LIMITE_PROBETA:
    Se_prima = 0.5 * material.Sut
  else:
    Se_prima = SE_PROBETA_LIMITE

  if Se_prima <= 0:
    raise ValueError(
      "El límite de fatiga de la probeta resultó no positivo."
    )

  return Se_prima


def factores_marin(material, d_m):
  ka, a, b, Sut_mpa = factor_acabado(material)
  kb = factor_tamano(d_m)
  kc = 1.0
  kd = factor_temperatura(material)
  ke = factor_confiabilidad(material)
  kf = material.k_f_marin

  Se_prima = limite_probeta(material)
  Se = ka * kb * kc * kd * ke * kf * Se_prima

  if Se <= 0:
    raise ValueError(
      "El límite de fatiga corregido resultó no positivo."
    )

  return {
    "Se_prima": Se_prima,
    "ka": ka,
    "a": a,
    "b": b,
    "Sut_mpa": Sut_mpa,
    "kb": kb,
    "kc": kc,
    "kd": kd,
    "ke": ke,
    "kf_marin": kf,
    "Se": Se
  }
