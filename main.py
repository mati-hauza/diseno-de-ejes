"""
Verificación del programa con el ejemplo 7-2 de Shigley.

El caso reproduce el contraeje de la figura 7-10 (dos engranes y dos
cojinetes) con unidades inglesas (pulgadas, lbf, lbf·in). Los datos de
las fuerzas, reacciones y momentos provienen de:

  R. G. Budynas y J. K. Nisbett, "Diseño en ingeniería mecánica de
  Shigley", 10.ª edición, ejemplo 7-2, págs. 349-353.

El material final del ejemplo es AISI 1050 estirado en frío
(Sut = 100 kpsi, Sy = 84 kpsi). La chaveta se supone AISI 1020 CD.

Para ejecutarlo sin entorno gráfico:

  MPLBACKEND=Agg .venv/bin/python main.py
"""

from modelo.apoyo import Apoyo
from modelo.carga import CargaCilindrica
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.escalonamiento import Escalonamiento
from modelo.material import Material
from modelo.ranura import Ranura
from modelo.tramo import Tramo
from modelo.unidades import (
  SistemaUnidades,
  fuerza_desde_n,
  momento_desde_nm
)

from calculos.analisis import analizar_eje

from salidas.diagramas_seguridad import generar_diagramas_seguridad
from salidas.diagramas_solicitaciones import generar_diagramas
from salidas.informe import mostrar_informe_completo


SISTEMA = SistemaUnidades.INGLES

# Equivalencia usada solo para la tabla de comparación.
IN_A_M = 0.0254

# Valores publicados en el ejemplo 7-2 (lbf y lbf·in).
REACCIONES_SHIGLEY = {
  "RAz": 115.0,
  "RAy": 356.7,
  "RBz": 1776.0,
  "RBy": 725.3
}

MOMENTOS_SHIGLEY = {
  2.75: 749.0,    # G, total
  7.50: 3651.0,   # I, total
  8.50: 4316.0,   # J, total
  9.50: 2398.0,   # K, total
  10.25: 959.0    # M, total
}


def construir_eje_ejemplo_7_2():
  """Arma el contraeje del ejemplo 7-2 con sus dimensiones reales."""
  material_eje = Material.crear(
    "AISI 1050 CD",
    SISTEMA,
    Sut=100,
    Sy=84,
    acabado="maquinado",
    confiabilidad=0.5
  )

  material_chaveta = Material.crear(
    "AISI 1020 CD (chaveta)",
    SISTEMA,
    Sut=68,
    Sy=57,
    acabado="maquinado",
    confiabilidad=0.5
  )

  material_cubo = Material.crear(
    "AISI 1050 CD (cubo)",
    SISTEMA,
    Sut=100,
    Sy=84,
    acabado="maquinado",
    confiabilidad=0.5
  )

  eje = Eje.crear(
    11.5,
    SISTEMA,
    material=material_eje,
    n_min=1.5,
    n_div=800
  )

  # Tramos de la figura 7-10: D1=D7=1.0, D2=D6=1.4,
  # D3=D5=1.625 y D4=2.0 pulgadas.
  eje.agregar_tramo(Tramo.crear(0.00, 1.25, 1.000, SISTEMA))
  eje.agregar_tramo(Tramo.crear(1.25, 1.75, 1.400, SISTEMA))
  eje.agregar_tramo(Tramo.crear(1.75, 3.50, 1.625, SISTEMA))
  eje.agregar_tramo(Tramo.crear(3.50, 7.50, 2.000, SISTEMA))
  eje.agregar_tramo(Tramo.crear(7.50, 9.75, 1.625, SISTEMA))
  eje.agregar_tramo(Tramo.crear(9.75, 10.25, 1.400, SISTEMA))
  eje.agregar_tramo(Tramo.crear(10.25, 11.50, 1.000, SISTEMA))

  # Filetes: 0.030 in en los asientos de cojinete, 1/16 in en los
  # hombros comunes y r = d/10 en los hombros I y H del engrane.
  eje.agregar_escalonamiento(
    Escalonamiento.crear(1.25, 0.030, SISTEMA)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(1.75, 0.0625, SISTEMA)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(3.50, 0.1625, SISTEMA)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(7.50, 0.1625, SISTEMA)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(9.75, 0.030, SISTEMA)
  )
  eje.agregar_escalonamiento(
    Escalonamiento.crear(10.25, 0.020, SISTEMA)
  )

  # Cojinetes A y B, con sus centros en x = 0.75 y 10.75 in.
  eje.agregar_apoyo(Apoyo.crear("A", 0.75, 0.90, True, SISTEMA))
  eje.agregar_apoyo(Apoyo.crear("B", 10.75, 0.90, False, SISTEMA))

  # Ranura del anillo de retención en K (x = 9.50 in). El radio se
  # ajusta a 0.0096 in para no salir del rango r/t <= 0.20 de A-15-17;
  # el ejemplo usa r = 0.010 in y consulta solo A-15-16.
  eje.agregar_ranura(
    Ranura.crear(
      9.50,
      SISTEMA,
      ancho=0.068,
      profundidad=0.048,
      radio=0.0096
    )
  )

  # Engrane 3: centro en G = 2.75 in, ancho de cubo 0.75 in.
  # La chaveta es cuadrada de 7/16 in (tabla 7-6 para d = 1.625 in)
  # y el fondo tiene r_f = 0.02 d = 0.0325 in, como en el ejemplo.
  engrane_3 = Elemento.crear(
    "Engrane 3",
    2.75,
    0.75,
    SISTEMA,
    usa_chaveta=True,
    a=0.4375,
    r_f=0.0325,
    material_chaveta=material_chaveta,
    material_cubo=material_cubo
  )

  engrane_3.agregar_carga(
    CargaCilindrica.crear(
      "W23",
      2.75,
      SISTEMA,
      radio_aplicacion=6.0,
      radial=-197,
      tangencial=540
    )
  )

  eje.agregar_elemento(engrane_3)

  # Engrane 4: cubo de I a J (centro x = 8.00 in, ancho 1.00 in).
  # El ejemplo redondea d4/2 = 1.335 in; con Wt54 = 2431 lbf eso da
  # 3245.4 lbf·in y rompe el equilibrio torsional exacto que exige el
  # programa. Se usa el radio que cierra el par en 3240 lbf·in.
  engrane_4 = Elemento.crear(
    "Engrane 4",
    8.00,
    1.00,
    SISTEMA,
    usa_chaveta=True,
    a=0.4375,
    r_f=0.0325,
    material_chaveta=material_chaveta,
    material_cubo=material_cubo
  )

  engrane_4.agregar_carga(
    CargaCilindrica.crear(
      "W54",
      8.50,
      SISTEMA,
      radio_aplicacion=3240 / 2431,
      radial=-885,
      tangencial=-2431
    )
  )

  eje.agregar_elemento(engrane_4)

  return eje


def _punto(resultado, x_in, lado):
  """Busca el punto evaluado en x (pulgadas) y el lado pedido."""
  x_m = x_in * IN_A_M
  tolerancia = 1e-6 * max(resultado.eje.longitud, 1.0)

  for punto in resultado.puntos:
    if (
      abs(punto.punto.x - x_m) <= tolerancia
      and punto.punto.lado == lado
    ):
      return punto

  for punto in resultado.puntos:
    if abs(punto.punto.x - x_m) <= tolerancia:
      return punto

  return None


def mostrar_comparacion(resultado):
  """Contrasta reacciones, momentos y factores con el ejemplo 7-2."""
  print("\n" + "=" * 72)
  print("COMPARACIÓN CON SHIGLEY, EJEMPLO 7-2")
  print("=" * 72)

  reacciones = {
    reaccion.nombre: reaccion
    for reaccion in resultado.reacciones
  }

  reaccion_a = reacciones["Reacción A"]
  reaccion_b = reacciones["Reacción B"]

  print("\nReacciones en los cojinetes (lbf):")
  print("  Magnitud        Programa   Shigley")
  print(
    f"  RAz             "
    f"{fuerza_desde_n(reaccion_a.Fz, SISTEMA):8.1f}   "
    f"{REACCIONES_SHIGLEY['RAz']:7.1f}"
  )
  print(
    f"  RAy             "
    f"{fuerza_desde_n(reaccion_a.Fy, SISTEMA):8.1f}   "
    f"{REACCIONES_SHIGLEY['RAy']:7.1f}"
  )
  print(
    f"  RBz             "
    f"{fuerza_desde_n(reaccion_b.Fz, SISTEMA):8.1f}   "
    f"{REACCIONES_SHIGLEY['RBz']:7.1f}"
  )
  print(
    f"  RBy             "
    f"{fuerza_desde_n(reaccion_b.Fy, SISTEMA):8.1f}   "
    f"{REACCIONES_SHIGLEY['RBy']:7.1f}"
  )

  par = resultado.solicitaciones.evaluar("T", 5.0 * IN_A_M)
  print("\nPar de torsión entre engranes (lbf·in):")
  print(
    f"  Programa = {abs(momento_desde_nm(par, SISTEMA)):.1f}   "
    "Shigley = 3240.0"
  )

  print("\nMomento flector resultante (lbf·in):")
  print("  Estación    x (in)   Programa   Shigley")
  for estacion, x_in in (
    ("G", 2.75),
    ("I", 7.50),
    ("J", 8.50),
    ("K", 9.50),
    ("M", 10.25)
  ):
    mr = resultado.solicitaciones.evaluar("MR", x_in * IN_A_M)
    print(
      f"  {estacion:^10} {x_in:7.2f}   "
      f"{momento_desde_nm(mr, SISTEMA):8.1f}   "
      f"{MOMENTOS_SHIGLEY[x_in]:7.1f}"
    )

  chaveta = next(
    c for c in resultado.chavetas
    if c.elemento.nombre == "Engrane 4"
  )

  puntos = {
    "Hombro I": _punto(resultado, 7.50, +1),
    "Chavetero, extremo izquierdo": _punto(
      resultado, chaveta.inicio / IN_A_M, +1
    ),
    "Chavetero, extremo derecho": _punto(
      resultado, chaveta.fin / IN_A_M, -1
    ),
    "Ranura K": _punto(resultado, 9.50, 0),
    "Hombro M": _punto(resultado, 10.25, +1)
  }

  print("\nFactor de seguridad a fatiga en los puntos del ejemplo:")
  print("  Punto                          Programa   Shigley")
  print(
    f"  {'Hombro I':30} "
    f"{puntos['Hombro I'].n_local:8.3f}   "
    "(1050: no lo recalcula)"
  )
  print(
    f"  {'Chavetero, extremo izquierdo':30} "
    f"{puntos['Chavetero, extremo izquierdo'].n_local:8.3f}   "
    "1.540"
  )
  print(
    f"  {'Chavetero, extremo derecho':30} "
    f"{puntos['Chavetero, extremo derecho'].n_local:8.3f}   "
    "(no lo verifica)"
  )
  print(
    f"  {'Ranura K':30} "
    f"{puntos['Ranura K'].n_local:8.3f}   "
    "1.860"
  )
  print(
    f"  {'Hombro M':30} "
    f"{puntos['Hombro M'].n_local:8.3f}   "
    "1.560"
  )

  print(
    "\nNotas de la comparación:\n"
    "  - Las reacciones, el par y los momentos coinciden con el\n"
    "    ejemplo dentro del redondeo de las fuerzas publicadas.\n"
    "  - El nf = 1.56 que Shigley informa para el hombro I es con\n"
    "    el AISI 1020 inicial (Se = 25.1 kpsi). Con el AISI 1050\n"
    "    final el ejemplo no vuelve a verificar ese hombro.\n"
    "  - Shigley verifica el chavetero solo en su extremo izquierdo\n"
    "    (M = 3750 lbf·in). El programa revisa también el extremo\n"
    "    derecho, donde el momento es mayor; por eso el mínimo es\n"
    "    más bajo y el resultado general no alcanza n_min = 1.5.\n"
    "  - Las diferencias de Kf y Kfs provienen de las gráficas\n"
    "    digitalizadas y de la sensibilidad de Neuber: el ejemplo\n"
    "    usa Kf = 1.82 y Kfs = 2.42; el programa obtiene 1.89 y\n"
    "    2.28 para el chavetero. La ranura usa Kt = 4.10 en lugar\n"
    "    de 4.3, también por digitalización de A-15-16."
  )


def main():
  eje = construir_eje_ejemplo_7_2()
  resultado = analizar_eje(eje)

  mostrar_informe_completo(resultado)
  mostrar_comparacion(resultado)

  generar_diagramas(
    eje,
    resultado.solicitaciones,
    mostrar=True,
    chavetas=resultado.chavetas
  )

  generar_diagramas_seguridad(resultado, mostrar=True)


if __name__ == "__main__":
  main()
