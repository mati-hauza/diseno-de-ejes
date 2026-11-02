from dataclasses import dataclass

import sympy as sp

from .transformaciones import (
  obtener_acciones_externas,
  obtener_acciones_puntuales
)

from .reacciones import calcular_reacciones


@dataclass
class ResultadoSolicitaciones:
  expresiones: dict
  reacciones: list
  advertencias: list
  variable: object
  posiciones: list

  def evaluar(self, nombre, posicion):
    if nombre not in self.expresiones:
      raise KeyError(
        f"No existe la expresión '{nombre}'."
      )

    valor = self.expresiones[nombre].subs(
      self.variable, posicion
    )

    return float(valor)

  def obtener_expresion(self, nombre):
    return self.expresiones[nombre]

  def mostrar_expresiones(self):
    for nombre, expresion in self.expresiones.items():
      print(f"\n{nombre}(x) =")
      sp.pprint(expresion)


def calcular_solicitaciones(eje):
  eje.validar()

  # Obtener acciones externas equivalentes.
  acciones = obtener_acciones_externas(eje)

  # Calcular reacciones.
  reacciones, advertencias = calcular_reacciones(
    eje, acciones
  )

  # Para construir los diagramas utilizamos las cargas puntuales
  # y las reacciones.
  #
  # Las cargas distribuidas se integran por separado.
  acciones_totales = (
    obtener_acciones_puntuales(eje) + reacciones
  )

  cargas_distribuidas = (
    eje.obtener_todas_las_cargas_distribuidas()
  )

  x = sp.Symbol("x", real=True)

  # Obtener posiciones donde cambian las expresiones.
  posiciones = sorted(set(
    [0.0, eje.longitud] +

    [
      a.posicion
      for a in acciones_totales
      if 0 < a.posicion < eje.longitud
    ] +

    [
      extremo
      for carga in cargas_distribuidas
      for extremo in (carga.inicio, carga.fin)
      if 0 < extremo < eje.longitud
    ]
  ))

  nombres = [
    "Vy", "Vz", "VR",
    "My", "Mz", "MR",
    "T", "N"
  ]

  tramos = {
    nombre: [] for nombre in nombres
  }

  # Construir las expresiones de cada intervalo.
  for i in range(len(posiciones) - 1):

    izquierda = posiciones[i]
    derecha = posiciones[i + 1]

    punto_medio = (izquierda + derecha) / 2

    # Acciones puntuales que ya actúan en este intervalo.
    activas = [
      a for a in acciones_totales
      if a.posicion <= punto_medio
    ]

    Vy = 0
    Vz = 0
    N = 0

    My = 0
    Mz = 0
    T = 0

    # Contribuciones de las cargas puntuales.
    for a in activas:

      posicion = sp.Float(a.posicion)

      # Fuerzas.
      Vy -= a.Fy
      Vz -= a.Fz
      N -= a.Fx

      # Momentos.
      My += (
        -a.Fz * (x - posicion)
        - a.My
      )

      Mz += (
        a.Fy * (x - posicion)
        - a.Mz
      )

      T -= a.Mx

    # Contribuciones de las cargas distribuidas.
    for carga in cargas_distribuidas:

      # La carga todavía no ha comenzado.
      if carga.inicio >= punto_medio:
        continue

      # Comprobar si estamos dentro de la carga
      # o si ya terminó.
      if punto_medio <= carga.fin:

        # Tramo situado dentro de la zona cargada.
        longitud_x = x - carga.inicio

        fuerza_y = carga.qy * longitud_x
        fuerza_z = carga.qz * longitud_x
        fuerza_x = carga.qx * longitud_x

        momento_y = (
          carga.qz * longitud_x**2 / 2
        )

        momento_z = (
          carga.qy * longitud_x**2 / 2
        )

      else:

        # La carga terminó antes de este tramo.
        # Utilizamos su resultante equivalente.
        longitud_total = carga.fin - carga.inicio

        centro = (
          carga.inicio + carga.fin
        ) / 2

        fuerza_y = carga.qy * longitud_total
        fuerza_z = carga.qz * longitud_total
        fuerza_x = carga.qx * longitud_total

        momento_y = (
          carga.qz * longitud_total * (x - centro)
        )

        momento_z = (
          carga.qy * longitud_total * (x - centro)
        )

      # Incorporar las contribuciones.
      Vy -= fuerza_y
      Vz -= fuerza_z
      N -= fuerza_x

      My -= momento_y
      Mz += momento_z

    # Simplificar expresiones del intervalo.
    Vy = sp.simplify(Vy)
    Vz = sp.simplify(Vz)
    N = sp.simplify(N)

    My = sp.simplify(My)
    Mz = sp.simplify(Mz)
    T = sp.simplify(T)

    # Resultantes.
    VR = sp.simplify(
      sp.sqrt(Vy**2 + Vz**2)
    )

    MR = sp.simplify(
      sp.sqrt(My**2 + Mz**2)
    )

    expresiones_tramo = {
      "Vy": Vy,
      "Vz": Vz,
      "VR": VR,
      "My": My,
      "Mz": Mz,
      "MR": MR,
      "T": T,
      "N": N
    }

    # Definir el intervalo.
    if i == len(posiciones) - 2:
      condicion = sp.And(
        x >= izquierda,
        x <= derecha
      )
    else:
      condicion = sp.And(
        x >= izquierda,
        x < derecha
      )

    for nombre in nombres:
      tramos[nombre].append(
        (expresiones_tramo[nombre], condicion)
      )

  # Construir las funciones Piecewise.
  expresiones = {
    nombre: sp.Piecewise(
      *casos,
      evaluate=False
    )
    for nombre, casos in tramos.items()
  }

  return ResultadoSolicitaciones(
    expresiones=expresiones,
    reacciones=reacciones,
    advertencias=advertencias,
    variable=x,
    posiciones=posiciones
  )