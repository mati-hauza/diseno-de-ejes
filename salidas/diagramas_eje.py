"""
Visualización geométrica de un eje y de sus acciones externas.

Las dimensiones longitudinales y los puntos de aplicación se toman del modelo.
El diámetro dibujado del eje es ilustrativo, ya que el modelo todavía no
contiene diámetros físicos.

Criterios de representación:
- Las flechas tienen longitud gráfica fija; no representan la magnitud a escala.
- La magnitud y las componentes se muestran en un panel lateral.
- Las cargas puntuales, distribuidas, reacciones y momentos tienen estilos
  diferentes.
- Los elementos montados sobre el eje conservan el mismo diámetro visual.
- Las cargas distribuidas se dibujan mediante varias flechas a lo largo del
  intervalo de aplicación.
"""

from math import cos, radians, sin
import textwrap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from calculos.transformaciones import transformar_carga
from modelo.carga import CargaCartesiana, CargaCilindrica
from modelo.unidades import (
  fuerza_desde_n,
  longitud_desde_m,
  longitud_a_m,
  momento_desde_nm,
  obtener_unidades,
)


# Paleta
COLOR_EJE = "#AEB8C4"
COLOR_APOYO = "#2E8B70"
COLOR_ELEMENTO = "#4C9AD4"
COLOR_CARGA = "#1769AA"
COLOR_DISTRIBUIDA = "#D68910"
COLOR_REACCION = "#C0392B"
COLOR_MOMENTO = "#884EA0"
COLOR_TEXTO = "#263445"
COLOR_REJILLA = "#D8DEE7"


# -----------------------------------------------------------------------------
# Conversiones y datos del modelo
# -----------------------------------------------------------------------------


def _vector_carga(carga):
  """Devuelve Fx, Fy, Fz en N, respetando el tipo de carga."""
  accion = transformar_carga(carga)
  return np.array([accion.Fx, accion.Fy, accion.Fz], dtype=float)


def _componentes_carga(carga, identificador):
  """Descompone una carga conservando el sistema en que fue definida.

  Los vectores se expresan en coordenadas globales X, Y, Z, pero las
  etiquetas conservan el significado de cada componente local.
  """
  if isinstance(carga, CargaCartesiana):
    definicion = [
      ("x", carga.Fx, np.array([1.0, 0.0, 0.0])),
      ("y", carga.Fy, np.array([0.0, 1.0, 0.0])),
      ("z", carga.Fz, np.array([0.0, 0.0, 1.0])),
    ]
  elif isinstance(carga, CargaCilindrica):
    theta = radians(carga.angulo_aplicacion)
    definicion = [
      ("axial", carga.F_axial, np.array([1.0, 0.0, 0.0]), "ax"),
      (
        "radial",
        carga.F_radial,
        np.array([0.0, cos(theta), sin(theta)]),
        "rad",
      ),
      (
        "tangencial",
        carga.F_tangencial,
        np.array([0.0, -sin(theta), cos(theta)]),
        "tan",
      ),
    ]
  else:
    vector = _vector_carga(carga)
    definicion = [
      ("x", vector[0], np.array([1.0, 0.0, 0.0])),
      ("y", vector[1], np.array([0.0, 1.0, 0.0])),
      ("z", vector[2], np.array([0.0, 0.0, 1.0])),
    ]

  componentes = []
  for item in definicion:
    nombre, magnitud, direccion = item[:3]
    abreviatura = item[3] if len(item) == 4 else nombre
    if abs(magnitud) <= 1e-12:
      continue
    componentes.append({
      "nombre": nombre,
      "id": f"{identificador}-{abreviatura}",
      "magnitud": float(magnitud),
      "vector": np.asarray(direccion, dtype=float) * float(magnitud),
    })
  return componentes


def _componentes_cartesianas(vector, identificador):
  """Descompone un vector global en componentes cartesianas no nulas."""
  componentes = []
  for indice, nombre in enumerate(("x", "y", "z")):
    magnitud = float(vector[indice])
    if abs(magnitud) <= 1e-12:
      continue
    componente = np.zeros(3, dtype=float)
    componente[indice] = magnitud
    componentes.append({
      "nombre": nombre,
      "id": f"{identificador}-{nombre}",
      "magnitud": magnitud,
      "vector": componente,
    })
  return componentes


def _punto_aplicacion(carga):
  """Coordenadas (x, y, z) del punto real de aplicación, en metros."""
  theta = radians(carga.angulo_aplicacion)
  radio = carga.radio_aplicacion

  return np.array([
    carga.posicion,
    radio * cos(theta),
    radio * sin(theta),
  ], dtype=float)


def _norma(vector):
  return float(np.linalg.norm(vector))


def _direccion(vector):
  """Devuelve el vector unitario o None si el vector es prácticamente cero."""
  vector = np.asarray(vector, dtype=float)
  magnitud = _norma(vector)
  if magnitud <= 1e-12:
    return None
  return vector / magnitud


def _unidades(eje):
  unidades = obtener_unidades(eje.sistema)
  return unidades["longitud"], unidades["fuerza"], unidades["momento"]


def _factor_longitud(eje):
  return longitud_desde_m(1.0, eje.sistema)


def _unidad_carga_distribuida(eje):
  if eje.sistema.name == "SI":
    return "N/mm"
  return "lbf/in"


def _carga_distribuida_desde_n_por_m(valor, eje):
  """Convierte N/m a N/mm o lbf/in, según el sistema elegido."""
  longitud_en_m = longitud_a_m(1.0, eje.sistema)
  return fuerza_desde_n(valor * longitud_en_m, eje.sistema)


def _obtener_radio_visual(eje, cargas=None):
  """Radio puramente gráfico; no depende del radio de aplicación de cargas."""
  return max(0.012 * eje.longitud, 1e-4)


def _obtener_datos_graficos(eje, resultado, cargas, momentos):
  """Prepara acciones para las vistas sin modificar el modelo."""
  datos = {
    "cargas": [],
    "distribuidas": [],
    "reacciones": [],
    "momentos": [],
  }

  for indice, carga in enumerate(cargas, start=1):
    datos["cargas"].append({
      "id": f"F{indice}",
      "nombre": carga.nombre,
      "origen": _punto_aplicacion(carga),
      "vector": _vector_carga(carga),
      "componentes": _componentes_carga(carga, f"F{indice}"),
      "modelo": carga,
    })

  distribuidas = eje.obtener_todas_las_cargas_distribuidas()
  for indice, carga in enumerate(distribuidas, start=1):
    datos["distribuidas"].append({
      "id": f"D{indice}",
      "nombre": carga.nombre,
      "inicio": carga.inicio,
      "fin": carga.fin,
      "vector": np.array([carga.qx, carga.qy, carga.qz], dtype=float),
      "componentes": _componentes_cartesianas(
        np.array([carga.qx, carga.qy, carga.qz], dtype=float), f"D{indice}"
      ),
      "modelo": carga,
    })

  for reaccion in resultado.reacciones:
    nombre_apoyo = reaccion.nombre.split()[-1]
    datos["reacciones"].append({
      "id": f"R{nombre_apoyo}",
      "nombre": reaccion.nombre,
      "origen": np.array([reaccion.posicion, 0.0, 0.0]),
      "vector": np.array(
        [reaccion.Fx, reaccion.Fy, reaccion.Fz], dtype=float
      ),
      "componentes": _componentes_cartesianas(
        np.array([reaccion.Fx, reaccion.Fy, reaccion.Fz], dtype=float),
        f"R{nombre_apoyo}",
      ),
      "modelo": reaccion,
    })

  for indice, momento in enumerate(momentos, start=1):
    datos["momentos"].append({
      "id": f"M{indice}",
      "nombre": momento.nombre,
      "posicion": momento.posicion,
      "vector": np.array([momento.Mx, momento.My, momento.Mz], dtype=float),
      "modelo": momento,
    })

  return datos


# -----------------------------------------------------------------------------
# Cilindros y geometría 3D
# -----------------------------------------------------------------------------


def _cilindro(ax, x0, x1, radio, color, alpha, resolucion=32):
  """Dibuja un cilindro cuyo eje longitudinal coincide con X."""
  if x1 <= x0:
    return

  theta = np.linspace(0, 2 * np.pi, resolucion)
  x = np.linspace(x0, x1, max(2, int(resolucion / 2)))
  X, T = np.meshgrid(x, theta)
  Y = radio * np.cos(T)
  Z = radio * np.sin(T)

  ax.plot_surface(
    X,
    Y,
    Z,
    color=color,
    alpha=alpha,
    linewidth=0,
    antialiased=True,
    shade=False,
    zorder=1,
  )


def _dibujar_geometria_3d(ax, eje, radio_visual, factor):
  """Dibuja el eje por segmentos para que los colores no se oculten.

  En lugar de superponer cilindros concéntricos (que mplot3d puede ordenar
  incorrectamente), cada intervalo del eje se dibuja una sola vez con el
  color de su ocupante: apoyo, elemento o cuerpo principal.
  """
  longitud = eje.longitud * factor
  radio = radio_visual * factor

  limites = {0.0, float(eje.longitud)}
  for elemento in eje.elementos:
    limites.add(float(elemento.inicio))
    limites.add(float(elemento.fin))
  for apoyo in eje.apoyos:
    limites.add(float(apoyo.inicio))
    limites.add(float(apoyo.fin))

  limites = sorted(
    min(max(limite, 0.0), float(eje.longitud))
    for limite in limites
  )
  limites = sorted(set(limites))

  for inicio, fin in zip(limites[:-1], limites[1:]):
    if fin - inicio <= 1e-12:
      continue

    punto_medio = 0.5 * (inicio + fin)
    hay_apoyo = any(
      apoyo.inicio - 1e-12 <= punto_medio <= apoyo.fin + 1e-12
      for apoyo in eje.apoyos
    )
    hay_elemento = any(
      elemento.inicio - 1e-12 <= punto_medio <= elemento.fin + 1e-12
      for elemento in eje.elementos
    )

    if hay_apoyo:
      color = COLOR_APOYO
    elif hay_elemento:
      color = COLOR_ELEMENTO
    else:
      color = COLOR_EJE

    _cilindro(
      ax,
      inicio * factor,
      fin * factor,
      radio,
      color,
      1.0,
      resolucion=64,
    )

  # Contorno longitudinal fino para mantener la lectura de un solo eje.
  ax.plot(
    [0, longitud], [0, 0], [0, 0],
    color="#526273", linewidth=0.55, alpha=0.7, zorder=7,
  )


def _origen_axial_separado_3d(ax, origen, vector, radio_visual,
                              factor, color, lado=1.0):
  """Aparta las flechas axiales del cilindro para que no queden ocultas."""
  origen = np.asarray(origen, dtype=float).copy()
  direccion = _direccion(vector)
  if direccion is None:
    return origen

  radial = np.hypot(origen[1], origen[2])
  if abs(direccion[0]) > 0.92 and radial < 1.7 * radio_visual:
    nuevo = origen + np.array([
      0.0,
      lado * 2.6 * radio_visual,
      1.3 * radio_visual,
    ])
    ax.plot(
      [origen[0] * factor, nuevo[0] * factor],
      [origen[1] * factor, nuevo[1] * factor],
      [origen[2] * factor, nuevo[2] * factor],
      color=color,
      linewidth=0.8,
      linestyle=(0, (2, 2)),
      alpha=0.75,
      zorder=7,
    )
    return nuevo

  return origen


def _origen_componente_3d(ax, origen, vector, radio_visual, factor,
                          color):
  """Desplaza componentes nacidas dentro del eje para que sean visibles.

  El conector punteado conserva la referencia al punto físico de aplicación.
  La desviación es solo gráfica y no cambia la posición usada en cálculos.
  """
  origen = np.asarray(origen, dtype=float)
  direccion = _direccion(vector)
  if direccion is None:
    return origen

  distancia_radial = float(np.hypot(origen[1], origen[2]))
  if distancia_radial >= 1.8 * radio_visual:
    return origen

  perpendicular = np.cross(direccion, np.array([1.0, 0.0, 0.0]))
  norma_perpendicular = _norma(perpendicular)
  if norma_perpendicular <= 1e-9:
    perpendicular = np.array([0.0, 1.0, 1.0])
    norma_perpendicular = _norma(perpendicular)
  perpendicular /= norma_perpendicular

  nuevo = origen + 2.8 * radio_visual * perpendicular
  ax.plot(
    [origen[0] * factor, nuevo[0] * factor],
    [origen[1] * factor, nuevo[1] * factor],
    [origen[2] * factor, nuevo[2] * factor],
    color=color,
    linewidth=0.75,
    linestyle=(0, (2, 2)),
    alpha=0.7,
    zorder=6,
  )
  return nuevo


def _dibujar_flecha_3d(ax, origen, vector, color, etiqueta, factor,
                       escala, grosor=1.8, offset_etiqueta=None):
  """Dibuja una flecha 3D de longitud fija y dirección dada por el vector."""
  direccion = _direccion(vector)
  if direccion is None or escala <= 0:
    return

  origen = np.asarray(origen, dtype=float) * factor
  longitud_flecha = escala * factor

  ax.quiver(
    origen[0], origen[1], origen[2],
    direccion[0], direccion[1], direccion[2],
    length=longitud_flecha,
    normalize=True,
    color=color,
    linewidth=grosor,
    arrow_length_ratio=0.22,
    pivot="tail",
    zorder=8,
  )

  if etiqueta:
    posicion = origen + direccion * longitud_flecha
    if offset_etiqueta is not None:
      posicion += np.asarray(offset_etiqueta, dtype=float) * factor
    ax.text(
      posicion[0], posicion[1], posicion[2],
      etiqueta,
      color=color,
      fontsize=7,
      fontweight="bold",
      zorder=12,
    )


def _texto_acciones(eje, datos, unidades):
  """Construye el contenido del panel lateral de las figuras."""
  longitud_unidad, unidad_fuerza, unidad_momento = unidades
  lineas = [
    "RESUMEN DEL MODELO",
    "─" * 31,
    f"Longitud del eje: {longitud_desde_m(eje.longitud, eje.sistema):.5g} {longitud_unidad}",
    "",
  ]

  if eje.apoyos or eje.elementos:
    lineas.append("GEOMETRÍA")
    for apoyo in eje.apoyos:
      estado = "fijo axial" if apoyo.fijo_axial else "libre axial"
      posicion = longitud_desde_m(apoyo.posicion, eje.sistema)
      ancho = longitud_desde_m(apoyo.ancho, eje.sistema)
      lineas.append(f"Apoyo {apoyo.nombre} ({estado})")
      lineas.append(f"  x={posicion:.4g} {longitud_unidad}; ancho={ancho:.4g} {longitud_unidad}")
    for indice, elemento in enumerate(eje.elementos, start=1):
      inicio = longitud_desde_m(elemento.inicio, eje.sistema)
      fin = longitud_desde_m(elemento.fin, eje.sistema)
      lineas.append(f"E{indice} · {elemento.nombre}")
      lineas.append(f"  x=[{inicio:.4g}, {fin:.4g}] {longitud_unidad}")
    lineas.append("")

  if datos["cargas"]:
    lineas.append("CARGAS PUNTUALES")
    for carga in datos["cargas"]:
      x = longitud_desde_m(carga["origen"][0], eje.sistema)
      radio = longitud_desde_m(
        carga["modelo"].radio_aplicacion, eje.sistema
      )
      angulo = carga["modelo"].angulo_aplicacion
      lineas.extend([
        f"{carga['id']} · {carga['nombre']}",
        f"  x={x:.4g} {longitud_unidad}; r={radio:.4g} {longitud_unidad}; θ={angulo:g}°",
      ])
      for componente in carga["componentes"]:
        valor = fuerza_desde_n(componente["magnitud"], eje.sistema)
        lineas.append(
          f"  {componente['nombre']} = {valor:.4g} {unidad_fuerza}"
        )
      magnitud = fuerza_desde_n(_norma(carga["vector"]), eje.sistema)
      lineas.append(f"  |F|={magnitud:.4g} {unidad_fuerza}")
    lineas.append("")

  if datos["distribuidas"]:
    lineas.append("CARGAS DISTRIBUIDAS")
    unidad_q = _unidad_carga_distribuida(eje)
    for carga in datos["distribuidas"]:
      inicio = longitud_desde_m(carga["inicio"], eje.sistema)
      fin = longitud_desde_m(carga["fin"], eje.sistema)
      lineas.extend([
        f"{carga['id']} · {carga['nombre']}",
        f"  x=[{inicio:.4g}, {fin:.4g}] {longitud_unidad}",
      ])
      for componente in carga["componentes"]:
        valor = _carga_distribuida_desde_n_por_m(
          componente["magnitud"], eje
        )
        lineas.append(
          f"  q{componente['nombre']} = {valor:.4g} {unidad_q}"
        )
    lineas.append("")

  if datos["reacciones"]:
    lineas.append("REACCIONES CALCULADAS")
    for reaccion in datos["reacciones"]:
      x = longitud_desde_m(reaccion["origen"][0], eje.sistema)
      lineas.extend([
        f"{reaccion['id']} · {reaccion['nombre']}",
        f"  x={x:.4g} {longitud_unidad}",
      ])
      for componente in reaccion["componentes"]:
        valor = fuerza_desde_n(componente["magnitud"], eje.sistema)
        lineas.append(
          f"  R{componente['nombre']} = {valor:.4g} {unidad_fuerza}"
        )
      magnitud = fuerza_desde_n(_norma(reaccion["vector"]), eje.sistema)
      lineas.append(f"  |R|={magnitud:.4g} {unidad_fuerza}")
    lineas.append("")

  if datos["momentos"]:
    lineas.append("MOMENTOS APLICADOS")
    for momento in datos["momentos"]:
      x = longitud_desde_m(momento["posicion"], eje.sistema)
      mx, my, mz = [
        momento_desde_nm(v, eje.sistema) for v in momento["vector"]
      ]
      magnitud = momento_desde_nm(_norma(momento["vector"]), eje.sistema)
      lineas.extend([
        f"{momento['id']} · {momento['nombre']}",
        f"  x={x:.4g} {longitud_unidad}",
        f"  Mx={mx:.4g}, My={my:.4g}, Mz={mz:.4g} {unidad_momento}",
        f"  |M|={magnitud:.4g} {unidad_momento}",
      ])

  if not any(datos.values()):
    lineas.append("No hay acciones aplicadas.")

  lineas.extend([
    "",
    "NOTA",
    "Las longitudes de las flechas son",
    "uniformes. Las magnitudes reales",
    "se indican en este panel.",
  ])
  lineas_ajustadas = []
  for linea in lineas:
    if len(linea) <= 43:
      lineas_ajustadas.append(linea)
      continue

    sangria = "  " if linea.startswith("  ") else ""
    lineas_ajustadas.extend(textwrap.wrap(
      linea,
      width=43,
      subsequent_indent=sangria + "  ",
      break_long_words=False,
      break_on_hyphens=False,
    ))

  return "\n".join(lineas_ajustadas)


def _altura_figura_info(texto, altura_minima=8.5):
  cantidad_lineas = texto.count("\n") + 1
  return max(altura_minima, 1.0 + cantidad_lineas * 0.145)


def _dibujar_panel_info(ax, texto, titulo=None):
  ax.set_axis_off()
  ax.text(
    0.0, 1.0, texto,
    transform=ax.transAxes,
    va="top",
    ha="left",
    fontsize=7.8,
    linespacing=1.32,
    family="DejaVu Sans Mono",
    color=COLOR_TEXTO,
    clip_on=True,
  )


# -----------------------------------------------------------------------------
# Vista 3D
# -----------------------------------------------------------------------------


def _dibujar_vista_3d(figura, eje, resultado, cargas, momentos,
                      radio_visual, factor, unidades, datos=None):
  if datos is None:
    datos = _obtener_datos_graficos(eje, resultado, cargas, momentos)

  grilla = figura.add_gridspec(
    1, 2,
    width_ratios=[3.25, 1.35],
    wspace=0.04,
  )
  ax = figura.add_subplot(grilla[0, 0], projection="3d")
  ax_info = figura.add_subplot(grilla[0, 1])

  _dibujar_geometria_3d(ax, eje, radio_visual, factor)

  longitud = eje.longitud * factor
  radio = radio_visual * factor
  longitud_flecha = 0.095 * longitud

  # Cargas puntuales: cada componente se representa con su propia flecha.
  # El tamaño es uniforme; la etiqueta identifica el eje o componente local.
  for carga in datos["cargas"]:
    for indice_componente, componente in enumerate(carga["componentes"]):
      origen_dibujo = _origen_componente_3d(
        ax,
        carga["origen"],
        componente["vector"],
        radio_visual,
        factor,
        COLOR_CARGA,
      )
      desplazamiento_etiqueta = np.array([
        0.0,
        ((indice_componente % 3) - 1) * 0.55 * radio_visual,
        (1 if indice_componente % 2 else -1) * 0.55 * radio_visual,
      ])
      _dibujar_flecha_3d(
        ax,
        origen_dibujo,
        componente["vector"],
        COLOR_CARGA,
        componente["id"],
        factor,
        longitud_flecha / factor,
        grosor=2.1,
        offset_etiqueta=desplazamiento_etiqueta,
      )

  # Cargas distribuidas: cada componente tiene su propia serie de flechas.
  for carga in datos["distribuidas"]:
    tramo = carga["fin"] - carga["inicio"]
    cantidad = max(2, min(7, int(30 * tramo / eje.longitud) + 2))
    posiciones = np.linspace(carga["inicio"], carga["fin"], cantidad)
    for componente in carga["componentes"]:
      for j, posicion in enumerate(posiciones):
        etiqueta = componente["id"] if j == len(posiciones) // 2 else ""
        origen = np.array([posicion, 0.0, 0.0])
        origen_dibujo = _origen_componente_3d(
          ax, origen, componente["vector"], radio_visual, factor,
          COLOR_DISTRIBUIDA,
        )
        _dibujar_flecha_3d(
          ax,
          origen_dibujo,
          componente["vector"],
          COLOR_DISTRIBUIDA,
          etiqueta,
          factor,
          longitud_flecha / factor,
          grosor=1.8,
        )

  # Cada componente de reacción se muestra por separado.
  for reaccion in datos["reacciones"]:
    for indice_componente, componente in enumerate(reaccion["componentes"]):
      # Las reacciones deben nacer en la coordenada real del apoyo, sobre
      # el eje central. No se desplazan lateralmente como recurso gráfico.
      origen_dibujo = reaccion["origen"]
      desplazamiento_etiqueta = np.array([
        0.0,
        ((indice_componente % 3) - 1) * 0.55 * radio_visual,
        (1 if indice_componente % 2 else -1) * 0.55 * radio_visual,
      ])
      _dibujar_flecha_3d(
        ax,
        origen_dibujo,
        componente["vector"],
        COLOR_REACCION,
        componente["id"],
        factor,
        longitud_flecha / factor,
        grosor=2.0,
        offset_etiqueta=desplazamiento_etiqueta,
      )

  # Momentos aplicados directamente. La longitud tampoco codifica su magnitud.
  origen_momento = 2.5 * radio_visual
  for indice, momento in enumerate(datos["momentos"]):
    origen = np.array([
      momento["posicion"],
      origen_momento,
      origen_momento * (1 + 0.18 * (indice % 2)),
    ])
    _dibujar_flecha_3d(
      ax,
      origen,
      momento["vector"],
      COLOR_MOMENTO,
      momento["id"],
      factor,
      0.075 * longitud / factor,
      grosor=2.2,
    )

  # Límites basados en las posiciones reales, no en el radio visual del eje.
  radios_aplicacion = [
    carga["modelo"].radio_aplicacion * factor
    for carga in datos["cargas"]
  ]
  extension_radial = max(radios_aplicacion, default=0.0)
  extension_radial = max(
    extension_radial + 1.25 * longitud_flecha,
    3.0 * radio,
    0.12 * longitud,
  )
  margen_x = 1.15 * longitud_flecha + 0.02 * longitud
  ax.set_xlim(-margen_x, longitud + margen_x)
  ax.set_ylim(-extension_radial, extension_radial)
  ax.set_zlim(-extension_radial, extension_radial)

  ax.set_xlabel(f"X · longitudinal ({unidades[0]})", labelpad=9)
  ax.set_ylabel(f"Y · vertical ({unidades[0]})", labelpad=8)
  ax.set_zlabel(f"Z · transversal ({unidades[0]})", labelpad=8)
  ax.set_title(
    "Vista tridimensional del eje",
    fontsize=13,
    fontweight="bold",
    pad=16,
    color=COLOR_TEXTO,
  )
  ax.view_init(elev=24, azim=-58)
  ax.set_proj_type("ortho")
  ax.set_box_aspect((1.25 * longitud, 2 * extension_radial,
                     2 * extension_radial))
  ax.grid(True, alpha=0.22)

  # Suavizar el fondo 3D.
  for eje_3d in (ax.xaxis, ax.yaxis, ax.zaxis):
    try:
      eje_3d.pane.fill = False
      eje_3d.pane.set_edgecolor("#DDE3EA")
    except AttributeError:
      pass

  _dibujar_panel_info(
    ax_info,
    _texto_acciones(eje, datos, unidades),
  )

  # Leyenda cromática compacta, fuera de la geometría.
  from matplotlib.lines import Line2D
  leyenda = [
    Line2D([0], [0], color=COLOR_CARGA, lw=2, label="Cargas puntuales"),
    Line2D([0], [0], color=COLOR_DISTRIBUIDA, lw=2, label="Distribuidas"),
    Line2D([0], [0], color=COLOR_REACCION, lw=2, label="Reacciones"),
    Line2D([0], [0], color=COLOR_MOMENTO, lw=2, label="Momentos"),
    Line2D([0], [0], color=COLOR_APOYO, lw=5, label="Apoyos"),
    Line2D([0], [0], color=COLOR_ELEMENTO, lw=5, label="Elementos"),
  ]
  figura.legend(
    handles=leyenda,
    loc="lower center",
    ncol=3,
    bbox_to_anchor=(0.48, 0.012),
    fontsize=8,
    frameon=False,
  )

  figura.subplots_adjust(left=0.02, right=0.99, top=0.91, bottom=0.11)


# -----------------------------------------------------------------------------
# Vistas 2D
# -----------------------------------------------------------------------------


def _dibujar_fuerza_2d(ax, posicion, coordenada_transversal, vector,
                       nombre, componente_normal, nombre_normal,
                       escala, factor, color, indice, unidad_fuerza, sistema,
                       mostrar_normal=True):
  """Dibuja una componente de fuerza en una proyección 2D.

  La componente dentro del plano se dibuja como flecha. La componente
  perpendicular se identifica con ⊙/⊗ exactamente sobre la coordenada X
  real de aplicación.
  """
  x0 = posicion * factor
  y0 = coordenada_transversal * factor
  vector_plano = np.asarray(vector, dtype=float)
  direccion = _direccion(vector_plano)
  tiene_flecha = direccion is not None and escala > 0
  tiene_normal = mostrar_normal and abs(componente_normal) > 1e-9

  ax.scatter(
    [x0], [y0],
    color=color,
    s=18,
    edgecolors="white",
    linewidths=0.55,
    zorder=8,
  )

  if tiene_flecha:
    dx, dy = direccion * escala * factor
    ax.annotate(
      "",
      xy=(x0 + dx, y0 + dy),
      xytext=(x0, y0),
      arrowprops={
        "arrowstyle": "-|>",
        "color": color,
        "lw": 1.8,
        "mutation_scale": 10,
        "shrinkA": 0,
        "shrinkB": 0,
      },
      annotation_clip=False,
      zorder=7,
    )

    if nombre:
      # Etiqueta junto a la punta, con un desplazamiento pequeño y en el
      # mismo sentido de la flecha. Ya no se alternan alturas grandes.
      signo_x = 1 if dx >= 0 else -1
      signo_y = 1 if dy >= 0 else -1
      ax.annotate(
        nombre,
        (x0 + dx, y0 + dy),
        xytext=(2.5 * signo_x, 2.5 * signo_y),
        textcoords="offset points",
        ha="left" if signo_x > 0 else "right",
        va="bottom" if signo_y > 0 else "top",
        fontsize=6.3,
        fontweight="bold",
        color=color,
        bbox={
          "boxstyle": "round,pad=0.10",
          "fc": "white",
          "ec": color,
          "alpha": 0.94,
          "lw": 0.4,
        },
        zorder=12,
      )

  if tiene_normal:
    simbolo = "⊙" if componente_normal > 0 else "⊗"
    etiqueta_normal = simbolo if tiene_flecha else f"{nombre} {simbolo}"
    ax.annotate(
      etiqueta_normal,
      (x0, y0),
      xytext=(0, -7),
      textcoords="offset points",
      ha="center",
      va="top",
      fontsize=7.0 if tiene_flecha else 6.3,
      fontweight="bold",
      color=color,
      bbox={
        "boxstyle": "round,pad=0.08",
        "fc": "white",
        "ec": color,
        "alpha": 0.92,
        "lw": 0.35,
      },
      zorder=11,
    )
  elif not tiene_flecha and nombre:
    ax.annotate(
      nombre,
      (x0, y0),
      xytext=(0, 3),
      textcoords="offset points",
      ha="center",
      va="bottom",
      fontsize=6.3,
      fontweight="bold",
      color=color,
      zorder=12,
    )


def _dibujar_momento_2d(ax, momento, plano, escala, factor, indice,
                        desplazamiento, unidad_momento, sistema,
                        etiqueta=None):
  """Representa la dirección del vector momento con longitud constante."""
  x0 = momento.posicion * factor
  y0 = desplazamiento * factor

  if plano == "XY":
    vector_plano = np.array([momento.Mx, momento.My], dtype=float)
    normal = momento.Mz
  else:
    # La normal positiva de la vista XZ (X hacia la derecha, Z hacia arriba)
    # apunta hacia -Y.
    vector_plano = np.array([momento.Mx, momento.Mz], dtype=float)
    normal = -momento.My

  direccion = _direccion(vector_plano)
  ax.scatter(
    [x0], [y0],
    color=COLOR_MOMENTO,
    s=25,
    marker="s",
    edgecolors="white",
    linewidths=0.5,
    zorder=9,
  )

  if direccion is not None and escala > 0:
    dx, dy = direccion * escala * factor
    ax.annotate(
      "",
      xy=(x0 + dx, y0 + dy),
      xytext=(x0, y0),
      arrowprops={
        "arrowstyle": "-|>",
        "color": COLOR_MOMENTO,
        "lw": 1.9,
        "mutation_scale": 11,
      },
      annotation_clip=False,
      zorder=8,
    )
    ax.annotate(
      etiqueta or momento.nombre,
      (x0 + dx, y0 + dy),
      xytext=(5, 5 + (indice % 3) * 9),
      textcoords="offset points",
      fontsize=6.7,
      color=COLOR_MOMENTO,
      bbox={
        "boxstyle": "round,pad=0.16",
        "fc": "white",
        "ec": COLOR_MOMENTO,
        "alpha": 0.92,
        "lw": 0.45,
      },
      zorder=12,
    )

  if abs(normal) > 1e-9:
    simbolo = "⊙" if normal > 0 else "⊗"
    ax.annotate(
      simbolo,
      (x0, y0),
      xytext=(-8, -14 - (indice % 3) * 8),
      textcoords="offset points",
      fontsize=9,
      fontweight="bold",
      color=COLOR_MOMENTO,
      zorder=12,
    )


def _dibujar_geometria_2d(ax, eje, radio_visual, factor):
  longitud = eje.longitud * factor
  altura = radio_visual * factor

  # Cuerpo principal del eje.
  ax.add_patch(Rectangle(
    (0, -altura),
    longitud,
    2 * altura,
    facecolor=COLOR_EJE,
    edgecolor="#687787",
    linewidth=0.8,
    alpha=0.95,
    zorder=2,
  ))

  # Los elementos tienen la misma altura visual que el eje.
  for indice_elemento, elemento in enumerate(eje.elementos, start=1):
    ax.add_patch(Rectangle(
      (elemento.inicio * factor, -altura),
      elemento.ancho * factor,
      2 * altura,
      facecolor=COLOR_ELEMENTO,
      edgecolor="#21618C",
      linewidth=0.75,
      alpha=0.95,
      zorder=4,
    ))
    if elemento.ancho * factor >= 0.035 * longitud:
      ax.text(
        elemento.posicion * factor, 0,
        f"E{indice_elemento}",
        ha="center", va="center",
        fontsize=6.5, fontweight="bold", color="white",
        zorder=7,
      )

  # Apoyos: bandas apenas más altas que el eje para distinguirlos.
  for apoyo in eje.apoyos:
    ax.add_patch(Rectangle(
      (apoyo.inicio * factor, -1.35 * altura),
      apoyo.ancho * factor,
      2.7 * altura,
      facecolor=COLOR_APOYO,
      edgecolor="#196F3D",
      linewidth=0.8,
      alpha=0.96,
      zorder=5,
    ))
    if apoyo.ancho * factor >= 0.025 * longitud:
      ax.text(
        apoyo.posicion * factor, 0,
        apoyo.nombre,
        ha="center", va="center",
        fontsize=6.5, fontweight="bold", color="white",
        zorder=8,
      )

  ax.plot(
    [0, longitud], [0, 0],
    color="#526273",
    linewidth=0.75,
    zorder=6,
  )


def _dibujar_proyeccion_2d(ax, eje, resultado, cargas, momentos,
                           radio_visual, factor, unidades,
                           plano, escala_fuerza, escala_momento,
                           datos=None):
  if datos is None:
    datos = _obtener_datos_graficos(eje, resultado, cargas, momentos)

  eje_vertical = "Y" if plano == "XY" else "Z"
  normal_texto = "Z" if plano == "XY" else "−Y"
  longitud = eje.longitud * factor
  altura_eje = radio_visual * factor

  _dibujar_geometria_2d(ax, eje, radio_visual, factor)

  # Acciones puntuales y reacciones: una entrada por cada componente no nula.
  acciones = []
  for carga in datos["cargas"]:
    for componente in carga["componentes"]:
      acciones.append({
        "id": componente["id"],
        "origen": carga["origen"],
        "vector": componente["vector"],
        "color": COLOR_CARGA,
      })
  for reaccion in datos["reacciones"]:
    for componente in reaccion["componentes"]:
      acciones.append({
        "id": componente["id"],
        "origen": reaccion["origen"],
        "vector": componente["vector"],
        "color": COLOR_REACCION,
      })

  for indice, accion in enumerate(acciones):
    punto = accion["origen"]
    vector = accion["vector"]

    if plano == "XY":
      coordenada_transversal = punto[1]
      vector_plano = (vector[0], vector[1])
      componente_normal = vector[2]
    else:
      coordenada_transversal = punto[2]
      vector_plano = (vector[0], vector[2])
      # En XZ, la normal positiva de la página es -Y.
      componente_normal = -vector[1]

    # Los componentes axiales cercanos al centro del eje se separan un poco
    # para que no queden tapados por la representación del eje.
    norma_plano = _norma(vector_plano)
    if (
      norma_plano > 1e-12
      and abs(vector_plano[0]) > 0.92 * norma_plano
      and abs(coordenada_transversal) < 1.7 * radio_visual
    ):
      lado = 1.0 if accion["color"] == COLOR_CARGA else -1.0
      origen_real = coordenada_transversal * factor
      coordenada_transversal += lado * 3.0 * radio_visual
      ax.plot(
        [punto[0] * factor, punto[0] * factor],
        [origen_real, coordenada_transversal * factor],
        color=accion["color"],
        linewidth=0.8,
        linestyle=(0, (2, 2)),
        alpha=0.75,
        zorder=6,
      )

    _dibujar_fuerza_2d(
      ax,
      punto[0],
      coordenada_transversal,
      vector_plano,
      accion["id"],
      componente_normal,
      normal_texto,
      escala_fuerza,
      factor,
      accion["color"],
      indice,
      unidades[1],
      eje.sistema,
    )

  # Cargas distribuidas: cada componente se dibuja por separado a lo largo
  # de su intervalo; el identificador aparece en la flecha central.
  indice_distribuida = len(acciones)
  for carga in datos["distribuidas"]:
    tramo = carga["fin"] - carga["inicio"]
    cantidad = max(2, min(7, int(30 * tramo / eje.longitud) + 2))
    posiciones = np.linspace(carga["inicio"], carga["fin"], cantidad)

    for componente in carga["componentes"]:
      vector = componente["vector"]
      if plano == "XY":
        vector_plano = (vector[0], vector[1])
        componente_normal = vector[2]
      else:
        vector_plano = (vector[0], vector[2])
        componente_normal = -vector[1]

      for j, posicion in enumerate(posiciones):
        es_central = j == len(posiciones) // 2
        coordenada_dibujo = 0.0
        norma_plano = _norma(vector_plano)
        if (
          norma_plano > 1e-12
          and abs(vector_plano[0]) > 0.92 * norma_plano
        ):
          coordenada_dibujo = 3.0 * radio_visual
          if j in (0, len(posiciones) - 1):
            ax.plot(
              [posicion * factor, posicion * factor],
              [0.0, coordenada_dibujo * factor],
              color=COLOR_DISTRIBUIDA,
              linewidth=0.75,
              linestyle=(0, (2, 2)),
              alpha=0.7,
              zorder=6,
            )

        _dibujar_fuerza_2d(
          ax,
          posicion,
          coordenada_dibujo,
          vector_plano,
          componente["id"] if es_central else "",
          componente_normal,
          normal_texto,
          escala_fuerza,
          factor,
          COLOR_DISTRIBUIDA,
          indice_distribuida + j,
          unidades[1],
          eje.sistema,
          mostrar_normal=es_central,
        )
      indice_distribuida += cantidad

  # Los momentos se dibujan en una franja propia para no mezclarlos con las
  # flechas de fuerzas que parten de los puntos de aplicación.
  desplazamiento_momento = 0.19 * eje.longitud
  if plano == "XZ":
    desplazamiento_momento *= -1

  for indice, momento in enumerate(datos["momentos"]):
    _dibujar_momento_2d(
      ax,
      momento["modelo"],
      plano,
      escala_momento,
      factor,
      indice,
      desplazamiento_momento * (1 + 0.12 * (indice % 2)),
      unidades[2],
      eje.sistema,
      etiqueta=momento["id"],
    )

  # Extensión vertical automática para incluir puntos de aplicación y flechas.
  coordenadas = [0.0]
  for carga in datos["cargas"]:
    coordenadas.append(carga["origen"][1 if plano == "XY" else 2])
  coordenadas.extend([0.0] * len(datos["reacciones"]))

  max_coordenada = max((abs(v) for v in coordenadas), default=0.0) * factor
  extension = max(
    0.14 * longitud,
    max_coordenada + escala_fuerza * factor + 0.06 * longitud,
    4.0 * altura_eje,
  )
  if datos["momentos"]:
    extension = max(
      extension,
      abs(desplazamiento_momento * factor)
      + escala_momento * factor + 0.07 * longitud,
    )

  margen_x = escala_fuerza * factor + 0.02 * longitud
  ax.set_xlim(-margen_x, longitud + margen_x)
  ax.set_ylim(-extension, extension)
  ax.set_xlabel(f"X · longitudinal ({unidades[0]})", fontsize=9)
  ax.set_ylabel(f"{eje_vertical} ({unidades[0]})", fontsize=9)
  ax.set_title(
    f"Proyección {plano}",
    fontsize=11,
    fontweight="bold",
    color=COLOR_TEXTO,
    pad=9,
  )
  ax.axhline(0, color="#526273", linewidth=0.65, alpha=0.55, zorder=1)
  ax.grid(True, linestyle="--", linewidth=0.55, color=COLOR_REJILLA, alpha=0.8)
  ax.set_axisbelow(True)
  ax.tick_params(labelsize=8)
  ax.margins(x=0.01, y=0.02)


def _dibujar_vista_2d(figura, eje, resultado, cargas, momentos,
                      radio_visual, factor, unidades, datos=None):
  if datos is None:
    datos = _obtener_datos_graficos(eje, resultado, cargas, momentos)

  grilla = figura.add_gridspec(
    2, 2,
    width_ratios=[3.3, 1.35],
    height_ratios=[1, 1],
    wspace=0.23,
    hspace=0.43,
  )
  ax_xy = figura.add_subplot(grilla[0, 0])
  ax_xz = figura.add_subplot(grilla[1, 0], sharex=ax_xy)
  ax_info = figura.add_subplot(grilla[:, 1])

  # Como las flechas no se escalan con la magnitud, todos los vectores
  # comparables tienen exactamente la misma longitud gráfica.
  escala_fuerza = 0.085 * eje.longitud
  escala_momento = 0.065 * eje.longitud

  _dibujar_proyeccion_2d(
    ax_xy, eje, resultado, cargas, momentos,
    radio_visual, factor, unidades, "XY",
    escala_fuerza, escala_momento, datos,
  )
  _dibujar_proyeccion_2d(
    ax_xz, eje, resultado, cargas, momentos,
    radio_visual, factor, unidades, "XZ",
    escala_fuerza, escala_momento, datos,
  )

  ax_xz.set_xlabel(f"X · longitudinal ({unidades[0]})", fontsize=9)
  ax_xy.set_xlabel("")
  ax_xy.tick_params(axis="x", labelbottom=False)

  _dibujar_panel_info(
    ax_info,
    _texto_acciones(eje, datos, unidades),
  )

  figura.suptitle(
    "Vistas bidimensionales del eje",
    fontsize=14,
    fontweight="bold",
    color=COLOR_TEXTO,
    y=0.975,
  )

  from matplotlib.lines import Line2D
  leyenda = [
    Line2D([0], [0], color=COLOR_CARGA, lw=2, label="Cargas puntuales"),
    Line2D([0], [0], color=COLOR_DISTRIBUIDA, lw=2, label="Distribuidas"),
    Line2D([0], [0], color=COLOR_REACCION, lw=2, label="Reacciones"),
    Line2D([0], [0], color=COLOR_MOMENTO, lw=2, label="Momentos"),
    Line2D([0], [0], color=COLOR_APOYO, lw=5, label="Apoyos"),
    Line2D([0], [0], color=COLOR_ELEMENTO, lw=5, label="Elementos"),
  ]
  figura.legend(
    handles=leyenda,
    loc="lower center",
    ncol=3,
    bbox_to_anchor=(0.42, 0.025),
    fontsize=8,
    frameon=False,
  )
  figura.subplots_adjust(left=0.065, right=0.985, top=0.91, bottom=0.13)


# -----------------------------------------------------------------------------
# API pública
# -----------------------------------------------------------------------------


def generar_diagramas_eje(eje, resultado, mostrar=True):
  """Genera una vista 3D y una figura 2D con proyecciones XY y XZ.

  Args:
    eje: instancia de modelo.eje.Eje.
    resultado: ResultadoSolicitaciones devuelto por calcular_solicitaciones.
    mostrar: si es True, llama a plt.show().

  Returns:
    Tupla (figura_3d, figura_2d), útil para guardar las imágenes.
  """
  cargas = eje.obtener_todas_las_cargas()
  momentos = eje.obtener_todos_los_momentos()
  factor = _factor_longitud(eje)
  unidades = _unidades(eje)
  radio_visual = _obtener_radio_visual(eje, cargas)
  datos = _obtener_datos_graficos(eje, resultado, cargas, momentos)

  texto_info = _texto_acciones(eje, datos, unidades)
  altura = _altura_figura_info(texto_info)

  figura_3d = plt.figure(figsize=(16, altura))
  _dibujar_vista_3d(
    figura_3d,
    eje,
    resultado,
    cargas,
    momentos,
    radio_visual,
    factor,
    unidades,
    datos,
  )

  figura_2d = plt.figure(figsize=(16, max(9.5, altura)))
  _dibujar_vista_2d(
    figura_2d,
    eje,
    resultado,
    cargas,
    momentos,
    radio_visual,
    factor,
    unidades,
    datos,
  )

  if mostrar:
    plt.show()

  return figura_3d, figura_2d
