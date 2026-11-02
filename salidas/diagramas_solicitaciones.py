import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

from modelo.unidades import (
  SistemaUnidades,
  longitud_desde_m,
  fuerza_desde_n,
  momento_desde_nm
)

CONFIGURACION_DIAGRAMAS = {
  "Vy": {
    "titulo": "Fuerza cortante en el plano XY",
    "color": "#5DADE2",
    "tipo": "fuerza"
  },
  "Vz": {
    "titulo": "Fuerza cortante en el plano XZ",
    "color": "#5DADE2",
    "tipo": "fuerza"
  },
  "VR": {
    "titulo": "Fuerza cortante resultante",
    "color": "#2874A6",
    "tipo": "fuerza"
  },
  "My": {
    "titulo": "Momento flector respecto a Y",
    "color": "#F5B041",
    "tipo": "momento"
  },
  "Mz": {
    "titulo": "Momento flector respecto a Z",
    "color": "#F5B041",
    "tipo": "momento"
  },
  "MR": {
    "titulo": "Momento flector resultante",
    "color": "#D35400",
    "tipo": "momento"
  },
  "T": {
    "titulo": "Momento torsor",
    "color": "#8E44AD",
    "tipo": "momento"
  },
  "N": {
    "titulo": "Fuerza axial",
    "color": "#E74C3C",
    "tipo": "fuerza"
  }
}


def convertir_longitud(valor, sistema):
  return longitud_desde_m(valor, sistema)


def convertir_fuerza(valor, sistema):
  return fuerza_desde_n(valor, sistema)


def convertir_momento(valor, sistema):
  return momento_desde_nm(valor, sistema)


def convertir_valores(valores, tipo, sistema):
  if tipo == "fuerza":
    return convertir_fuerza(valores, sistema)

  return convertir_momento(valores, sistema)


def obtener_unidades_grafica(tipo, sistema):
  if tipo == "fuerza":
    if sistema == SistemaUnidades.SI:
      return "N"
    return "lbf"

  if sistema == SistemaUnidades.SI:
    return "N·mm"

  return "lbf·in"


def evaluar_tramo(expresion, variable, inicio, fin, cantidad=100):
  funcion = sp.lambdify(variable, expresion, modules="numpy")

  posiciones = np.linspace(inicio, fin, cantidad)
  valores = np.asarray(funcion(posiciones), dtype=float)

  if valores.ndim == 0:
    valores = np.full(posiciones.shape, float(valores))

  return posiciones, valores


def dibujar_diagrama(
  ax,
  resultado,
  nombre,
  eje,
  estaciones
):
  configuracion = CONFIGURACION_DIAGRAMAS[nombre]

  expresion = resultado.obtener_expresion(nombre)
  variable = resultado.variable

  color = configuracion["color"]
  tipo = configuracion["tipo"]

  unidades_x = "mm" if eje.sistema == SistemaUnidades.SI else "in"
  unidades_y = obtener_unidades_grafica(tipo, eje.sistema)

  posiciones_tramos = resultado.posiciones

  # Cada expresión Piecewise conserva un caso por tramo.
  for i, (caso, inicio, fin) in enumerate(zip(
    expresion.args,
    posiciones_tramos[:-1],
    posiciones_tramos[1:]
  )):
    expresion_tramo = caso[0]

    x = np.linspace(inicio, fin, 100)

    if nombre in ("VR", "MR"):
      # No evaluar sqrt(Vy**2 + Vz**2) o sqrt(My**2 + Mz**2)
      # como polinomios expandidos. Cerca de cero, el redondeo puede
      # producir un radicando negativo diminuto. hypot es más estable.
      componentes = (
        ("Vy", "Vz") if nombre == "VR" else ("My", "Mz")
      )

      valores_componentes = []
      for componente in componentes:
        expresion_componente = resultado.obtener_expresion(
          componente
        ).args[i][0]
        funcion = sp.lambdify(
          variable,
          expresion_componente,
          modules="numpy"
        )
        valores = np.asarray(funcion(x), dtype=float)
        if valores.ndim == 0:
          valores = np.full(x.shape, float(valores))
        valores_componentes.append(valores)

      y = np.hypot(
        valores_componentes[0],
        valores_componentes[1]
      )
    else:
      x, y = evaluar_tramo(
        expresion_tramo,
        variable,
        inicio,
        fin
      )

    x = convertir_longitud(x, eje.sistema)
    y = convertir_valores(y, tipo, eje.sistema)

    # Se dibuja cada tramo por separado para evitar diagonales
    # artificiales en las discontinuidades.
    ax.plot(
      x,
      y,
      color=color,
      linewidth=2
    )

    ax.fill_between(
      x,
      y,
      0,
      color=color,
      alpha=0.15
    )

  longitud = convertir_longitud(eje.longitud, eje.sistema)

  estaciones_convertidas = [
    convertir_longitud(posicion, eje.sistema)
    for posicion in estaciones
  ]

  ax.set_xlim(0, longitud)
  ax.set_xticks(estaciones_convertidas)

  ax.set_title(
    configuracion["titulo"],
    fontsize=11,
    fontweight="bold",
    pad=9
  )

  ax.set_xlabel(f"Posición X ({unidades_x})", fontsize=9)
  ax.set_ylabel(f"{nombre} ({unidades_y})", fontsize=9)

  ax.axhline(
    y=0,
    color="black",
    linewidth=0.9
  )

  ax.grid(
    True,
    linestyle="--",
    linewidth=0.6,
    alpha=0.5
  )

  ax.tick_params(
    axis="both",
    labelsize=8
  )

  ax.tick_params(
    axis="x",
    labelrotation=0
  )

  ax.margins(y=0.15)


def generar_diagramas(eje, resultado):
  nombres = [
    "T", "Vy", "Mz", "VR",
    "N", "Vz", "My", "MR"
  ]
  
  nombres = [
    "Vy", "Mz", "N",
    "Vz", "My", "T",
    "VR", "MR"
  ]

  estaciones = resultado.posiciones

  figura, ejes = plt.subplots(
    nrows=3,
    ncols=3,
    figsize=(20, 9),
    constrained_layout=True
  )

  figura.suptitle(
    "Diagramas de fuerzas y momentos internos",
    fontsize=15,
    fontweight="bold"
  )

  for ax, nombre in zip(ejes.flat, nombres):
    dibujar_diagrama(
      ax,
      resultado,
      nombre,
      eje,
      estaciones
    )

  plt.show()