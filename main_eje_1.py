"""
Eje 1: tornillo sin fin.

Geometría ajustada a tres tramos 5-7-5 mm, con filetes de radio
0.5 mm en los dos escalonamientos. El momento motor se aplica en
el extremo de acoplamiento (x = 0) con sentido contrario al par
generado por la fuerza tangencial del engranamiento.

Para ejecutarlo sin entorno gráfico:

  MPLBACKEND=Agg .venv/bin/python main_eje_1.py
"""

from modelo.apoyo import Apoyo
from modelo.carga import CargaCilindrica
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.escalonamiento import Escalonamiento
from modelo.material import Material
from modelo.momento import Momento
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades

from calculos.analisis import analizar_eje

from salidas.diagramas_seguridad import generar_diagramas_seguridad
from salidas.diagramas_solicitaciones import generar_diagramas
from salidas.informe import mostrar_informe_completo


SISTEMA = SistemaUnidades.SI


def construir_eje_1():
  """Arma el eje del tornillo sin fin con los datos del problema."""

  material_eje_1 = Material.crear(
    "AISI 1040 CD",
    SISTEMA,
    Sut=590,
    Sy=490,
    acabado="maquinado",
    confiabilidad=0.5
  )

  eje_1 = Eje.crear(
    112,
    SISTEMA,
    material=material_eje_1,
    n_min=1.5,
    n_div=800
  )

  # Tres tramos: 5 mm en los asientos de cojinete y 7 mm en el
  # tramo central, donde se monta el tornillo sin fin.
  eje_1.agregar_tramo(Tramo.crear(0, 14, 5, SISTEMA))
  eje_1.agregar_tramo(Tramo.crear(14, 98, 7, SISTEMA))
  eje_1.agregar_tramo(Tramo.crear(98, 112, 5, SISTEMA))

  # Escalonamientos con radio de redondeo r = 0.5 mm.
  eje_1.agregar_escalonamiento(
    Escalonamiento.crear(14, 0.5, SISTEMA)
  )
  eje_1.agregar_escalonamiento(
    Escalonamiento.crear(98, 0.5, SISTEMA)
  )

  # Apoyos.
  # A: fijo axialmente.
  # B: libre axialmente.
  eje_1.agregar_apoyo(
    Apoyo.crear("A", 8, 12, True, SISTEMA)
  )
  eje_1.agregar_apoyo(
    Apoyo.crear("B", 104, 12, False, SISTEMA)
  )

  # Tornillo sin fin: centro x = 56 mm, ancho 82 mm.
  # Sin chaveta: unión mediante perfil D.
  tornillo = Elemento.crear(
    "Tornillo sin fin",
    56,
    82,
    SISTEMA,
    usa_chaveta=False
  )

  tornillo.agregar_carga(
    CargaCilindrica.crear(
      "Fuerzas engranamiento",
      56,
      SISTEMA,
      radio_aplicacion=11.2,
      radial=39.91,
      tangencial=42.32,
      axial=105.28
    )
  )

  eje_1.agregar_elemento(tornillo)

  # Momento motor en el extremo de acoplamiento.
  #
  # La fuerza tangencial genera Mx = r·Ft = 11.2·42.32
  # = 473.984 N·mm. Para cerrar exactamente el equilibrio
  # torsional se usa el valor sin redondear; el momento motor
  # va en sentido contrario.
  par_motor = 11.2 * 42.32

  eje_1.agregar_momento(
    Momento.crear(
      "Momento motor",
      0,
      SISTEMA,
      Mx=-par_motor
    )
  )

  return eje_1


def main():
  eje = construir_eje_1()
  resultado = analizar_eje(eje)

  mostrar_informe_completo(resultado)

  generar_diagramas(
    eje,
    resultado.solicitaciones,
    mostrar=True,
    chavetas=resultado.chavetas
  )

  generar_diagramas_seguridad(resultado, mostrar=True)


if __name__ == "__main__":
  main()
