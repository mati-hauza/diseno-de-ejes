from math import inf, isfinite

from modelo.unidades import (
  obtener_unidades,
  longitud_desde_m,
  fuerza_desde_n,
  momento_desde_nm,
  presion_desde_pa,
  temperatura_desde_c
)

from .informe_solicitaciones import (
  mostrar_expresiones,
  mostrar_reacciones
)


def _n(valor, decimales=3):
  valor = float(valor)

  if valor == inf:
    return "∞"

  if not isfinite(valor):
    return "no verificable"

  if abs(valor) < 0.5 * 10 ** (-decimales):
    valor = 0.0

  return f"{valor:.{decimales}f}"


def _unidades(eje):
  unidades = dict(obtener_unidades(eje.sistema))
  unidades["temperatura"] = (
    "°C" if eje.sistema.name == "SI" else "°F"
  )
  unidades["area"] = (
    "mm²" if eje.sistema.name == "SI" else "in²"
  )
  return unidades


def _long(eje, valor):
  return _n(longitud_desde_m(valor, eje.sistema))


def _fue(eje, valor):
  return _n(fuerza_desde_n(valor, eje.sistema))


def _mom(eje, valor):
  return _n(momento_desde_nm(valor, eje.sistema))


def _pres(eje, valor):
  return _n(presion_desde_pa(valor, eje.sistema))


def _temp(eje, valor):
  return _n(temperatura_desde_c(valor, eje.sistema))


def _area(eje, valor):
  """Convierte un área interna (m²) a la unidad del usuario."""
  factor = longitud_desde_m(1.0, eje.sistema)
  return _n(valor * factor**2)


def _titulo(texto):
  print("\n" + "=" * 72)
  print(texto)
  print("=" * 72)


def mostrar_informe_completo(resultado):
  eje = resultado.eje
  u = _unidades(eje)

  _mostrar_entradas(resultado, u)
  _mostrar_advertencias(resultado.advertencias)
  _mostrar_chavetas(resultado, u)
  _mostrar_concentradores(resultado, u)

  mostrar_reacciones(
    resultado.reacciones,
    eje.sistema,
    u
  )

  mostrar_expresiones(
    resultado.solicitaciones,
    eje.sistema,
    u
  )

  _mostrar_puntos_criticos(resultado, u)
  _mostrar_resumen(resultado, u)


def _mostrar_entradas(resultado, u):
  eje = resultado.eje
  material = eje.material

  _titulo("1. RESUMEN DE ENTRADAS")

  print(f"Longitud del eje: {_long(eje, eje.longitud)} {u['longitud']}")
  print(f"Sistema de unidades: {eje.sistema.value}")
  print(f"Factor de seguridad mínimo: {_n(eje.n_min)}")
  print(f"Divisiones de la malla: {eje.n_div}")

  print("\nTramos:")
  for i, tramo in enumerate(eje.tramos, start=1):
    print(
      f"  {i}. x ∈ [{_long(eje, tramo.x_inicio)}, "
      f"{_long(eje, tramo.x_fin)}] {u['longitud']}, "
      f"d = {_long(eje, tramo.d)} {u['longitud']}"
    )

  print("\nEscalonamientos:")
  if not eje.escalonamientos:
    print("  (ninguno)")

  tolerancia_eje = 1e-9 * max(eje.longitud, 1.0)

  for escalonamiento in eje.escalonamientos:
    izquierdo = eje.tramo_izquierdo(
      escalonamiento.x_s, tolerancia_eje
    )
    derecho = eje.tramo_derecho(
      escalonamiento.x_s, tolerancia_eje
    )

    if izquierdo is None or derecho is None:
      print(
        f"  x = {_long(eje, escalonamiento.x_s)} "
        f"{u['longitud']}, "
        f"r = {_long(eje, escalonamiento.r)} {u['longitud']}"
      )
      continue

    D = max(izquierdo.d, derecho.d)
    d = min(izquierdo.d, derecho.d)

    print(
      f"  x = {_long(eje, escalonamiento.x_s)} {u['longitud']}, "
      f"D = {_long(eje, D)} {u['longitud']}, "
      f"d = {_long(eje, d)} {u['longitud']}, "
      f"r = {_long(eje, escalonamiento.r)} {u['longitud']}"
    )

  print("\nApoyos:")
  for apoyo in eje.apoyos:
    print(
      f"  {apoyo.nombre}: centro x = {_long(eje, apoyo.posicion)} "
      f"{u['longitud']}, ancho = {_long(eje, apoyo.ancho)}, "
      f"fijo axial = {apoyo.fijo_axial}"
    )

  print("\nElementos:")
  if not eje.elementos:
    print("  (ninguno)")
  for elemento in eje.elementos:
    print(
      f"  {elemento.nombre}: centro x = "
      f"{_long(eje, elemento.posicion)} {u['longitud']}, "
      f"ancho = {_long(eje, elemento.ancho)}"
    )
    if elemento.usa_chaveta:
      print(
        f"    chaveta: a = {_long(eje, elemento.a)} {u['longitud']}, "
        f"r_f = "
        f"{_long(eje, elemento.r_f) if elemento.r_f else 'no informado'}, "
        f"n_chaveta = "
        f"{_n(elemento.n_chaveta) if elemento.n_chaveta else 'n_min'}"
      )

  print("\nRanuras:")
  if not eje.ranuras:
    print("  (ninguna)")
  for ranura in eje.ranuras:
    if ranura.con_geometria:
      print(
        f"  x = {_long(eje, ranura.posicion)} {u['longitud']}, "
        f"a = {_long(eje, ranura.ancho)}, "
        f"t = {_long(eje, ranura.profundidad)}, "
        f"r = {_long(eje, ranura.radio)}"
      )
    else:
      print(
        f"  x = {_long(eje, ranura.posicion)} {u['longitud']} "
        "(sin geometría)"
      )

  print("\nMaterial del eje:")
  print(
    f"  {material.nombre}: Sut = {_pres(eje, material.Sut)} "
    f"{u['presion']}, Sy = {_pres(eje, material.Sy)} "
    f"{u['presion']}, acabado = {material.acabado}, "
    f"T = {_temp(eje, material.temperatura)} {u['temperatura']}, "
    f"R = {_n(material.confiabilidad, 6)}, "
    f"k_f_marin = {_n(material.k_f_marin)}"
  )

  print("\nCargas puntuales y momentos:")
  todas = eje.obtener_todas_las_cargas()
  todos = eje.obtener_todos_los_momentos()
  if not todas and not todos:
    print("  (ninguna)")
  for carga in todas:
    print(
      f"  {carga.nombre}: x = {_long(eje, carga.posicion)} "
      f"{u['longitud']}"
    )
  for momento in todos:
    print(
      f"  {momento.nombre}: x = {_long(eje, momento.posicion)} "
      f"{u['longitud']}, Mx = {_mom(eje, momento.Mx)}, "
      f"My = {_mom(eje, momento.My)}, "
      f"Mz = {_mom(eje, momento.Mz)} {u['momento']}"
    )

  print("\nCargas distribuidas:")
  if not eje.cargas_distribuidas:
    print("  (ninguna)")
  for carga in eje.cargas_distribuidas:
    print(
      f"  {carga.nombre}: x ∈ [{_long(eje, carga.inicio)}, "
      f"{_long(eje, carga.fin)}] {u['longitud']}"
    )


def _mostrar_advertencias(advertencias):
  _titulo("2. VALIDACIONES Y ADVERTENCIAS")

  if not advertencias:
    print("No se registraron advertencias.")
    return

  vistas = []

  for advertencia in advertencias:
    if advertencia not in vistas:
      vistas.append(advertencia)

  for advertencia in vistas:
    print(f"- {advertencia}")


def _mostrar_chavetas(resultado, u):
  eje = resultado.eje

  _titulo("3. DIMENSIONAMIENTO DE CHAVETAS")

  if not resultado.chavetas:
    print("El eje no tiene elementos con chaveta.")
    return

  for chaveta in resultado.chavetas:
    print(f"\n{chaveta.elemento.nombre}:")
    print(
      f"  Te = |Σ Mx| = {_mom(eje, chaveta.Te)} {u['momento']}"
    )
    print(f"  d = {_long(eje, chaveta.d)} {u['longitud']}")
    print(
      f"  a = b = h = {_long(eje, chaveta.a)} {u['longitud']}"
    )
    print(
      f"  Material chaveta: {chaveta.material_chaveta.nombre} "
      f"(Sy = {_pres(eje, chaveta.Sy_chaveta)} {u['presion']})"
    )
    print(
      f"  Material cubo: {chaveta.material_cubo.nombre} "
      f"(Sy = {_pres(eje, chaveta.Sy_cubo)} {u['presion']})"
    )
    print(
      f"  Sy,contacto = min = {_pres(eje, chaveta.Sy_contacto)} "
      f"{u['presion']}"
    )
    print(
      f"  n_chaveta = {_n(chaveta.n_chaveta)}"
    )

    if not chaveta.existe:
      print(
        "  El elemento no transmite torque: no se genera "
        "chavetero (m = 1, l = 0)."
      )
      continue

    print(
      f"  Ft = 2Te/d = {_fue(eje, chaveta.Ft)} {u['fuerza']}"
    )
    print(
      f"  Fuerza por chaveta (m = {chaveta.m}): "
      f"Ft,i = {_fue(eje, chaveta.Ft_i)} {u['fuerza']}"
    )
    print(
      f"  Ac = a·l = {_area(eje, chaveta.Ac)} {u['area']}, "
      f"τc = {_pres(eje, chaveta.tau_c)} {u['presion']}"
    )
    print(
      f"  Ssy = 0.577·Sy,chaveta = "
      f"{_pres(eje, chaveta.Ssy)} {u['presion']}, "
      f"nc = {_n(chaveta.n_c)}"
    )
    print(
      f"  Ap = (a/2)·l = {_area(eje, chaveta.Ap)} {u['area']}, "
      f"σp = {_pres(eje, chaveta.sigma_p)} {u['presion']}"
    )
    print(
      f"  np = Sy,contacto/σp = {_n(chaveta.n_p)}"
    )
    print(
      f"  l_req,1 = {_long(eje, chaveta.l_req1)} "
      f"{u['longitud']}, l_max = 0.9Le = "
      f"{_long(eje, chaveta.l_max)} {u['longitud']}"
    )
    print(
      f"  m = {chaveta.m}, l = {_long(eje, chaveta.l)} "
      f"{u['longitud']}, Lk = l"
    )
    print(
      f"  Chavetero: [{_long(eje, chaveta.inicio)}, "
      f"{_long(eje, chaveta.fin)}] {u['longitud']}, "
      f"r_e = a/2 = {_long(eje, chaveta.r_e)}, "
      f"t_eje = t_cubo = a/2 = "
      f"{_long(eje, chaveta.a / 2)}"
    )
    print(
      "  Verificación: nc ≥ n_chaveta y np ≥ n_chaveta: "
      f"{'cumple' if chaveta.n_c >= chaveta.n_chaveta and chaveta.n_p >= chaveta.n_chaveta else 'no cumple'}"
    )


def _mostrar_concentradores(resultado, u):
  eje = resultado.eje

  _titulo("4. CONCENTRADORES DE ESFUERZOS")

  if not resultado.concentradores:
    print("No hay concentradores de esfuerzos.")
    return

  for c in resultado.concentradores:
    print(f"\n{c.nombre} ({c.tipo}):")

    if c.es_puntual:
      print(
        f"  Posición: x = {_long(eje, c.posicion)} "
        f"{u['longitud']}, lado = {c.lado:+d}"
      )
    else:
      print(
        f"  Intervalo: [{_long(eje, c.inicio)}, "
        f"{_long(eje, c.fin)}] {u['longitud']}"
      )

    for clave, valor in c.geometria.items():
      if clave in ("m",):
        print(f"  {clave} = {valor}")
      elif clave == "r_f" and valor is None:
        print(f"  {clave} = no informado")
      else:
        print(f"  {clave} = {_long(eje, valor)} {u['longitud']}")

    for clave, valor in c.relaciones.items():
      print(f"  {clave} = {_n(valor, 6)}")

    print(f"  Figura / fuente: {c.figura}")
    print(f"  Interpolación: {c.interpolacion}")
    print(
      f"  Kt,N = {_n(c.KtN, 4)}, Kt,B = {_n(c.KtB, 4)}, "
      f"Kts = {_n(c.Kts, 4)}"
    )
    print(
      f"  q = {_n(c.q, 4)}, qs = {_n(c.qs, 4)}"
    )
    print(
      f"  Kf,N = {_n(c.KfN, 4)}, Kf,B = {_n(c.KfB, 4)}, "
      f"Kfs = {_n(c.Kfs, 4)}"
    )

    for advertencia in c.advertencias:
      print(f"  Advertencia: {advertencia}")


def _tramo_en_punto(eje, x, lado):
  if lado < 0:
    tramo = eje.tramo_izquierdo(x)
  elif lado > 0:
    tramo = eje.tramo_derecho(x)
  else:
    tramo = eje.tramo_en(x)

  return tramo if tramo is not None else eje.tramo_en(x)


def _mostrar_puntos_criticos(resultado, u):
  eje = resultado.eje

  _titulo("5. PROCEDIMIENTO EN LOS PUNTOS CRÍTICOS")

  mostrados = 0

  for rp in resultado.puntos:
    if not rp.punto.es_critico:
      continue

    if not isfinite(rp.n_local):
      continue

    mostrados += 1
    punto = rp.punto
    esf = rp.esfuerzos
    tramo = _tramo_en_punto(eje, punto.x, punto.lado)

    radio = (
      punto.concentrador.radio
      if punto.concentrador is not None
      else None
    )

    print(
      f"\n{'-' * 72}\n"
      f"x = {_long(eje, punto.x)} {u['longitud']}, "
      f"lado = {_lado_texto(punto.lado)}, "
      f"tramo = [{_long(eje, tramo.x_inicio)}, "
      f"{_long(eje, tramo.x_fin)}] {u['longitud']}, "
      f"d = {_long(eje, punto.d)} {u['longitud']}, "
      f"discontinuidad = {punto.discontinuidad}"
    )
    print(
      "  Radio de redondeo: "
      + (
        "no aplica"
        if radio is None
        else f"{_long(eje, radio)} {u['longitud']}"
      )
    )

    if punto.concentrador is None:
      print("  Concentrador activo: ninguno (Kf,N = Kf,B = Kfs = 1)")
    else:
      print(
        f"  Concentrador activo: {punto.concentrador.nombre}"
      )
      print(
        f"  Kt,N = {_n(punto.concentrador.KtN, 4)}, "
        f"Kt,B = {_n(punto.concentrador.KtB, 4)}, "
        f"Kts = {_n(punto.concentrador.Kts, 4)}"
      )
      print(
        f"  q = {_n(punto.concentrador.q, 4)}, "
        f"qs = {_n(punto.concentrador.qs, 4)}"
      )
      print(
        f"  Kf,N = {_n(esf.KfN, 4)}, Kf,B = {_n(esf.KfB, 4)}, "
        f"Kfs = {_n(esf.Kfs, 4)}"
      )
      print(
        f"  Fuente: {punto.concentrador.fuente}"
      )
      print(
        "  Nota: Kt es un resultado intermedio; los esfuerzos "
        "corregidos usan Kf."
      )

    print("\n  A. Solicitaciones:")
    print(
      f"    N = {_fue(eje, esf.N)}, Vy = {_fue(eje, esf.Vy)}, "
      f"Vz = {_fue(eje, esf.Vz)}, VR = {_fue(eje, esf.VR)} "
      f"{u['fuerza']}"
    )
    print(
      f"    My = {_mom(eje, esf.My)}, Mz = {_mom(eje, esf.Mz)}, "
      f"MR = {_mom(eje, esf.MR)}, T = {_mom(eje, esf.T)} "
      f"{u['momento']}"
    )
    print(
      "    Ma = MR, Mm = 0, Na = 0, Nm = N, Ta = 0, Tm = T"
    )

    print("\n  B. Esfuerzos nominales:")
    print(
      f"    σN,a = {_pres(eje, esf.sigma_Na)}, "
      f"σN,m = {_pres(eje, esf.sigma_Nm)} {u['presion']}"
    )
    print(
      f"    σB,a = 32Ma/(πd³) = {_pres(eje, esf.sigma_Ba)}, "
      f"σB,m = 0 {u['presion']}"
    )
    print(
      f"    τT,a = {_pres(eje, esf.tau_Ta)}, "
      f"τT,m = 16Tm/(πd³) = {_pres(eje, esf.tau_Tm)} "
      f"{u['presion']}"
    )

    print("\n  C. Esfuerzos corregidos:")
    print(
      f"    σa = Kf,B·σB,a + Kf,N·σN,a = "
      f"{_pres(eje, esf.sigma_a)} {u['presion']}"
    )
    print(
      f"    σm = Kf,B·σB,m + Kf,N·σN,m = "
      f"{_pres(eje, esf.sigma_m)} {u['presion']}"
    )
    print(
      f"    τa = {_pres(eje, esf.tau_a)}, "
      f"τm = {_pres(eje, esf.tau_m)} {u['presion']}"
    )

    print("\n  D. Von Mises:")
    print(
      f"    σ'a = sqrt((Kf,B·σB,a + Kf,N·σN,a/0.85)² + "
      f"3(Kfs·τT,a)²)"
    )
    print(
      f"        = sqrt(({_n(esf.KfB, 4)}·{_pres(eje, esf.sigma_Ba)} + "
      f"{_n(esf.KfN, 4)}·{_pres(eje, esf.sigma_Na)}/0.85)² + "
      f"3({_n(esf.Kfs, 4)}·{_pres(eje, esf.tau_Ta)})²)"
    )
    print(
      f"        = {_pres(eje, esf.sigma_prima_a)} {u['presion']}"
    )
    print(
      f"    σ'm = sqrt((Kf,B·σB,m + Kf,N·σN,m)² + "
      f"3(Kfs·τT,m)²)"
    )
    print(
      f"        = sqrt(({_n(esf.KfB, 4)}·{_pres(eje, esf.sigma_Bm)} + "
      f"{_n(esf.KfN, 4)}·{_pres(eje, esf.sigma_Nm)})² + "
      f"3({_n(esf.Kfs, 4)}·{_pres(eje, esf.tau_Tm)})²)"
    )
    print(
      f"        = {_pres(eje, esf.sigma_prima_m)} {u['presion']}"
    )

    marin = rp.marin
    print("\n  E. Resistencia a fatiga:")
    print(
      f"    Se' = {_pres(eje, marin['Se_prima'])} "
      f"{u['presion']}"
    )
    print(
      f"    ka = {_n(marin['ka'], 4)} "
      f"(a = {_n(marin['a'], 4)}, b = {_n(marin['b'], 4)}, "
      f"Sut = {_n(marin['Sut_mpa'], 3)} MPa)"
    )
    print(
      f"    kb = {_n(marin['kb'], 4)} "
      f"(d = {_long(eje, punto.d)} {u['longitud']}), "
      f"kc = {_n(marin['kc'], 4)}, "
      f"kd = {_n(marin['kd'], 4)}, "
      f"ke = {_n(marin['ke'], 4)}, "
      f"kf,marin = {_n(marin['kf_marin'], 4)}"
    )
    print(
      f"    Se = ka·kb·kc·kd·ke·kf,marin·Se' = "
      f"{_pres(eje, marin['Se'])} {u['presion']}"
    )

    nf = rp.factores.get("goodman")
    print("\n  F. Factor de seguridad a fatiga (Goodman):")
    denominador = (
      esf.sigma_prima_a / marin["Se"]
      + esf.sigma_prima_m / eje.material.Sut
    )
    print(
      f"    1/nf = σ'a/Se + σ'm/Sut = "
      f"{_pres(eje, esf.sigma_prima_a)}/"
      f"{_pres(eje, marin['Se'])} + "
      f"{_pres(eje, esf.sigma_prima_m)}/"
      f"{_pres(eje, eje.material.Sut)} = {_n(denominador, 6)}"
    )
    print(f"    nf = {_n(nf)}")

    ny = rp.factores.get("fluencia")
    print("\n  G. Fluencia (Von Mises máximo):")
    if rp.fluencia is not None:
      detalle = rp.fluencia
      print(
        f"    σx,1 = {_pres(eje, detalle['sigma_x1'])}, "
        f"σx,2 = {_pres(eje, detalle['sigma_x2'])} "
        f"{u['presion']}"
      )
      print(
        f"    σx,max = {_pres(eje, detalle['sigma_x_max'])}, "
        f"τx,max = {_pres(eje, detalle['tau_x_max'])} "
        f"{u['presion']}"
      )
      print(
        f"    σ'max = {_pres(eje, detalle['sigma_prima_max'])} "
        f"{u['presion']}, "
        f"σ'max,cons = "
        f"{_pres(eje, detalle['sigma_prima_max_cons'])}"
      )
    print(f"    ny = Sy/σ'max = {_n(ny)}")

    print("\n  H. Resultado de la sección:")
    nombre_gobernante = next(
      (
        criterio.nombre
        for criterio in resultado.criterios
        if criterio.clave == rp.gobernante
      ),
      rp.gobernante
    )
    print(
      f"    nf = {_n(nf)}, ny = {_n(ny)}, "
      f"gobierna = {nombre_gobernante}, "
      f"n_local = {_n(rp.n_local)}"
    )
    print(
      f"    Cumple n_min = {_n(eje.n_min)}: "
      f"{'sí' if rp.n_local >= eje.n_min else 'no'}"
    )

  if mostrados == 0:
    print(
      "No hay puntos críticos con factor de seguridad finito."
    )


def _lado_texto(lado):
  if lado < 0:
    return "x⁻"
  if lado > 0:
    return "x⁺"
  return "x"


def _mostrar_resumen(resultado, u):
  eje = resultado.eje

  _titulo("6. RESUMEN FINAL")

  for criterio in resultado.criterios:
    minimo, rp = resultado.minimos[criterio.clave]

    if rp is None:
      continue

    print(
      f"Mínimo {criterio.nombre}: n = {_n(minimo)} "
      f"en x = {_long(eje, rp.punto.x)} {u['longitud']}"
    )

  print(
    f"\nFactor de seguridad del eje: n_eje = "
    f"{_n(resultado.n_eje)} en x = "
    f"{_long(eje, resultado.punto_critico.punto.x)} "
    f"{u['longitud']}"
  )
  nombre_gobernante = next(
    (
      criterio.nombre
      for criterio in resultado.criterios
      if criterio.clave == resultado.criterio_gobernante
    ),
    resultado.criterio_gobernante
  )
  print(f"Criterio que gobierna: {nombre_gobernante}")

  print(
    f"n_min = {_n(eje.n_min)}: "
    f"{'CUMPLE' if resultado.cumple_eje else 'NO CUMPLE'}"
  )

  print("\nChavetas:")
  if not resultado.chavetas:
    print("  (ninguna)")
  for chaveta in resultado.chavetas:
    if not chaveta.existe:
      print(
        f"  {chaveta.elemento.nombre}: no aplica "
        "(sin torque)."
      )
      continue
    cumple = (
      chaveta.n_c >= chaveta.n_chaveta
      and chaveta.n_p >= chaveta.n_chaveta
    )
    print(
      f"  {chaveta.elemento.nombre}: nc = {_n(chaveta.n_c)}, "
      f"np = {_n(chaveta.n_p)}, n_chaveta = "
      f"{_n(chaveta.n_chaveta)}: "
      f"{'CUMPLE' if cumple else 'NO CUMPLE'}"
    )

  print("\nAdvertencias y aproximaciones:")
  if not resultado.advertencias:
    print("  (ninguna)")
  else:
    vistas = []
    for advertencia in resultado.advertencias:
      if advertencia not in vistas:
        vistas.append(advertencia)
    for advertencia in vistas:
      print(f"  - {advertencia}")

  if resultado.no_verificable:
    resultado_general = "NO VERIFICABLE"
  elif resultado.cumple:
    resultado_general = "ACEPTADO"
  else:
    resultado_general = "NO ACEPTADO"

  print(f"\nResultado general: {resultado_general}")

  if resultado.no_verificable:
    print(
      "Atención: hay puntos no verificables. El resultado "
      "general nunca se considera aprobado."
    )
