from math import inf, isfinite

import matplotlib.pyplot as plt
import numpy as np

from modelo.unidades import longitud_desde_m


def _valor_legible(valor, limite):
  if valor == inf:
    return limite
  if not isfinite(valor):
    return np.nan
  return min(valor, limite)


def generar_diagramas_seguridad(resultado, mostrar=True):
  """
  Genera una figura independiente por cada criterio registrado.

  Devuelve la lista de figuras.
  """
  eje = resultado.eje
  sistema = eje.sistema

  xs = np.array([
    longitud_desde_m(rp.punto.x, sistema)
    for rp in resultado.puntos
  ])

  limites = [
    valor
    for valor in (
      [resultado.n_eje, eje.n_min]
      + [valor for valor, _ in resultado.minimos.values()]
    )
    if isfinite(valor)
  ]

  maximo = max(limites) if limites else 1.0
  limite_grafico = max(1.25 * maximo, 2 * eje.n_min, 1.0)

  figuras = []

  for criterio in resultado.criterios:
    fig, ax = plt.subplots(figsize=(10, 4.5))

    valores = np.array([
      _valor_legible(rp.factores[criterio.clave], limite_grafico)
      for rp in resultado.puntos
    ])

    x_graf = []
    y_graf = []

    for i, (x, y) in enumerate(zip(xs, valores)):
      if i > 0 and xs[i] - xs[i - 1] < 1e-12:
        x_graf.append(np.nan)
        y_graf.append(np.nan)

      x_graf.append(x)
      y_graf.append(y)

    ax.plot(
      x_graf,
      y_graf,
      color=criterio.color,
      linewidth=1.8,
      label=criterio.nombre
    )

    minimo, resultado_min = resultado.minimos[criterio.clave]

    x_criticos = [
      longitud_desde_m(rp.punto.x, sistema)
      for rp in resultado.puntos
      if rp.punto.es_critico
    ]
    y_criticos = [
      _valor_legible(rp.factores[criterio.clave], limite_grafico)
      for rp in resultado.puntos
      if rp.punto.es_critico
    ]

    ax.scatter(
      x_criticos,
      y_criticos,
      s=16,
      color="#2C3E50",
      zorder=3,
      label="Puntos críticos"
    )

    ax.axhline(
      eje.n_min,
      color="#E67E22",
      linestyle="--",
      linewidth=1.4,
      label=f"n_min = {eje.n_min:g}"
    )

    if resultado_min is not None and isfinite(minimo):
      x_min = longitud_desde_m(resultado_min.punto.x, sistema)
      ax.scatter(
        [x_min], [min(minimo, limite_grafico)],
        color="#C0392B", s=55, zorder=5,
        label=f"Mínimo = {minimo:.3f}"
      )
      ax.annotate(
        f"n = {minimo:.3f}\nx = {x_min:.3f}",
        xy=(x_min, min(minimo, limite_grafico)),
        xytext=(10, 15),
        textcoords="offset points",
        fontsize=8,
        color="#7B241C"
      )

    for concentrador in resultado.concentradores:
      if concentrador.es_puntual:
        ax.axvline(
          longitud_desde_m(concentrador.posicion, sistema),
          color="#7F8C8D",
          linewidth=0.7,
          alpha=0.6
        )
      else:
        ax.axvspan(
          longitud_desde_m(concentrador.inicio, sistema),
          longitud_desde_m(concentrador.fin, sistema),
          color="#BDC3C7",
          alpha=0.35
        )

    ax.set_title(
      f"Factor de seguridad — {criterio.nombre}"
    )
    ax.set_xlabel(f"Posición longitudinal x [{_unidad_longitud(sistema)}]")
    ax.set_ylabel("Factor de seguridad")
    ax.set_xlim(0, longitud_desde_m(eje.longitud, sistema))
    ax.set_ylim(0, limite_grafico)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc="best")

    if any(
      not isfinite(rp.factores[criterio.clave])
      for rp in resultado.puntos
    ):
      ax.text(
        0.99, 0.96,
        "Los valores ∞ se grafican en el límite superior",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=7.5,
        color="#555555"
      )

    fig.tight_layout()
    figuras.append(fig)

  if mostrar:
    plt.show()

  return figuras


def _unidad_longitud(sistema):
  from modelo.unidades import obtener_unidades
  return obtener_unidades(sistema)["longitud"]
