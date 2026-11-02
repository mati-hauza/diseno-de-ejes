import math

import sympy as sp

from modelo.unidades import (
  obtener_unidades, 
  longitud_a_m,
  longitud_desde_m,
  fuerza_desde_n,
  momento_desde_nm
)


def _formatear_numero(valor, decimales=3):
  """Formatea números evitando mostrar -0.000 por redondeo."""
  valor = float(valor)

  if abs(valor) < 0.5 * 10 ** (-decimales):
    valor = 0.0

  return f"{valor:.{decimales}f}"


def _formatear_lineal(expresion, variable):
  """Devuelve una expresión constante o lineal en forma legible."""
  expresion = sp.expand(expresion)

  try:
    polinomio = sp.Poly(expresion, variable)
  except sp.PolynomialError:
    return str(sp.N(expresion, 6))

  if polinomio.degree() > 1:
    return str(sp.N(expresion, 6))

  coef_x = float(polinomio.coeff_monomial(variable))
  independiente = float(polinomio.coeff_monomial(1))

  # Evitar residuos de precisión flotante en expresiones que deberían
  # ser cero, por ejemplo al llegar al segundo apoyo.
  if abs(coef_x) < 0.0005:
    coef_x = 0.0

  if abs(independiente) < 0.0005:
    independiente = 0.0

  if coef_x == 0.0:
    return _formatear_numero(independiente)

  if abs(coef_x) == 1.0:
    termino_x = "x" if coef_x > 0 else "-x"
  else:
    termino_x = f"{_formatear_numero(abs(coef_x))}·x"
    if coef_x < 0:
      termino_x = f"-{termino_x}"

  if independiente == 0.0:
    return termino_x

  signo = "+" if independiente > 0 else "-"
  termino_constante = _formatear_numero(abs(independiente))

  return f"{termino_x} {signo} {termino_constante}"


def _convertir_tramo(expresion, resultado, sistema, tipo):
  """Convierte un tramo desde unidades internas SI a unidades elegidas."""
  x = sp.Symbol("x", real=True)

  factor_x = longitud_a_m(1.0, sistema)

  if tipo == "fuerza":
    factor_y = fuerza_desde_n(1.0, sistema)
  elif tipo == "momento":
    factor_y = momento_desde_nm(1.0, sistema)
  else:
    raise ValueError(f"Tipo de resultado desconocido: {tipo}")

  expresion_convertida = expresion.subs(
    resultado.variable,
    x * factor_x
  ) * factor_y

  return sp.N(expresion_convertida, 12), x

def _formatear_expresion(expresion, variable):
  """Formatea expresiones lineales y expresiones más complejas."""
  expresion = sp.simplify(expresion)

  try:
    polinomio = sp.Poly(sp.expand(expresion), variable)

    if polinomio.degree() <= 1:
      return _formatear_lineal(expresion, variable)

  except sp.PolynomialError:
    pass

  texto = sp.sstr(sp.N(expresion, 6))

  texto = texto.replace("**", "^")
  texto = texto.replace("*", "·")
  texto = texto.replace("sqrt", "√")

  return texto

def mostrar_reacciones(reacciones, sistema, unidades):
  print("\n" + "=" * 60)
  print("REACCIONES EN LOS APOYOS")
  print("=" * 60)

  for reaccion in reacciones:
    rx = fuerza_desde_n(reaccion.Fx, sistema)
    ry = fuerza_desde_n(reaccion.Fy, sistema)
    rz = fuerza_desde_n(reaccion.Fz, sistema)

    print(f"\n{reaccion.nombre}")
    print(f"  Rx = {_formatear_numero(rx)} {unidades['fuerza']}")
    print(f"  Ry = {_formatear_numero(ry)} {unidades['fuerza']}")
    print(f"  Rz = {_formatear_numero(rz)} {unidades['fuerza']}")


def mostrar_expresiones(resultado, sistema, unidades):
  """Imprime cada función interna definida por tramos."""
  print("\n" + "=" * 60)
  print("ECUACIONES DE LAS SOLICITACIONES INTERNAS")
  print("=" * 60)
  print(
    f"Variable: x ({unidades['longitud']}) | "
    f"Fuerzas: {unidades['fuerza']} | "
    f"Momentos: {unidades['momento']}"
  )

  posiciones = resultado.posiciones
  expresiones = resultado.expresiones
  n_tramos = len(posiciones) - 1

  # Obtener las expresiones de cada tramo para las funciones originales.
  funciones_base = {
    nombre: [
      expresiones[nombre].args[i][0]
      for i in range(n_tramos)
    ]
    for nombre in ("Vy", "Vz", "My", "Mz", "T", "N")
  }

  # Calcular las resultantes como funciones por tramos.
  vr = [
    sp.sqrt(sp.expand(vy**2 + vz**2))
    for vy, vz in zip(funciones_base["Vy"], funciones_base["Vz"])
  ]

  mr = [
    sp.sqrt(sp.expand(my**2 + mz**2))
    for my, mz in zip(funciones_base["My"], funciones_base["Mz"])
  ]

  # Definir el orden y las unidades de impresión.
  funciones = {
    "Vy": ("fuerza", funciones_base["Vy"]),
    "Vz": ("fuerza", funciones_base["Vz"]),
    "VR": ("fuerza", vr),
    "N": ("fuerza", funciones_base["N"]),
    "My": ("momento", funciones_base["My"]),
    "Mz": ("momento", funciones_base["Mz"]),
    "MR": ("momento", mr),
    "T": ("momento", funciones_base["T"])
  }

  x = sp.Symbol("x", real=True)

  # Imprimir cada función con todos sus tramos.
  for nombre, (tipo, expresiones_tramo) in funciones.items():

    if tipo == "fuerza":
      unidad = unidades["fuerza"]
    else:
      unidad = unidades["momento"]

    ecuaciones = []

    for expresion in expresiones_tramo:
      expresion_usuario, variable_usuario = _convertir_tramo(
        expresion,
        resultado,
        sistema,
        tipo
      )

      ecuaciones.append(
        _formatear_expresion(
          expresion_usuario,
          variable_usuario
        )
      )

    # Alinear las expresiones antes de las condiciones.
    ancho = max(len(ecuacion) for ecuacion in ecuaciones)

    print(f"\n{nombre}(x) [{unidad}] = {{")

    for i, ecuacion in enumerate(ecuaciones):
      inicio = longitud_desde_m(posiciones[i], sistema)
      fin = longitud_desde_m(posiciones[i + 1], sistema)

      ultimo_tramo = i == n_tramos - 1
      simbolo_fin = "≤" if ultimo_tramo else "<"

      condicion = (
        f"{_formatear_numero(inicio)} ≤ x "
        f"{simbolo_fin} {_formatear_numero(fin)}"
      )

      print(f"  {ecuacion:<{ancho}}   si  {condicion}")

    print("}")

def mostrar_advertencias(advertencias):
  if not advertencias:
    return

  print("\n" + "=" * 60)
  print("ADVERTENCIAS")
  print("=" * 60)

  for advertencia in advertencias:
    print(f"\n- {advertencia}")


def mostrar_informe(eje, resultado):
  unidades = obtener_unidades(eje.sistema)

  mostrar_reacciones(
    resultado.reacciones,
    eje.sistema,
    unidades
  )

  mostrar_expresiones(
    resultado,
    eje.sistema,
    unidades
  )

  mostrar_advertencias(resultado.advertencias)
