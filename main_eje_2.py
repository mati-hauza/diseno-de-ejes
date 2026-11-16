"""
Eje 2: corona PETG y tambor.

Geometría ajustada a cuatro tramos 18-20-22-20 mm. Los filetes se
adaptan a los nuevos escalones: el radio máximo admisible es
(D - d)/2 = 1.0 mm en los tres casos, por lo que se usa r = 1.0 mm.

La fuerza tangencial de la corona se ajusta al valor sin redondear
que cierra exactamente el equilibrio torsional con la tensión de la
cuerda del tambor:

  Ft,corona = 245.25 * 42.5 / 99 = 105.2840909 N

Para ejecutarlo sin entorno gráfico:

  MPLBACKEND=Agg .venv/bin/python main_eje_2.py
"""

from modelo.apoyo import Apoyo
from modelo.carga import CargaCilindrica
from modelo.eje import Eje
from modelo.elemento import Elemento
from modelo.escalonamiento import Escalonamiento
from modelo.material import Material
from modelo.tramo import Tramo
from modelo.unidades import SistemaUnidades

from calculos.analisis import analizar_eje

from salidas.diagramas_seguridad import generar_diagramas_seguridad
from salidas.diagramas_solicitaciones import generar_diagramas
from salidas.informe import mostrar_informe_completo


SISTEMA = SistemaUnidades.SI


def construir_eje_2():
  """Arma el eje de la corona y el tambor con los datos del problema."""

  material_eje_2 = Material.crear(
    "AISI 1040 CD",
    SISTEMA,
    Sut=590,
    Sy=490,
    acabado="maquinado",
    confiabilidad=0.5
  )

  eje_2 = Eje.crear(
    200,
    SISTEMA,
    material=material_eje_2,
    n_min=1.5,
    n_div=800
  )

  # Cuatro tramos: 18 mm en el extremo de la corona, 20 mm en los
  # asientos de cojinete y 22 mm en la zona del tambor.
  eje_2.agregar_tramo(Tramo.crear(0, 37.5, 18, SISTEMA))
  eje_2.agregar_tramo(Tramo.crear(37.5, 67.5, 20, SISTEMA))
  eje_2.agregar_tramo(Tramo.crear(67.5, 162.5, 22, SISTEMA))
  eje_2.agregar_tramo(Tramo.crear(162.5, 200, 20, SISTEMA))

  # Escalonamientos. Con los diámetros 18-20-22-20, el escalón es
  # de 2 mm en los tres casos y el radio máximo es 1 mm.
  eje_2.agregar_escalonamiento(
    Escalonamiento.crear(37.5, 1.0, SISTEMA)
  )
  eje_2.agregar_escalonamiento(
    Escalonamiento.crear(67.5, 1.0, SISTEMA)
  )
  eje_2.agregar_escalonamiento(
    Escalonamiento.crear(162.5, 1.0, SISTEMA)
  )

  # Apoyos.
  # B: fijo axialmente.
  # C: libre axialmente.
  eje_2.agregar_apoyo(
    Apoyo.crear("B", 55, 12, True, SISTEMA)
  )
  eje_2.agregar_apoyo(
    Apoyo.crear("C", 175, 12, False, SISTEMA)
  )

  # Corona: centro x = 25 mm, ancho 25 mm.
  # Unión mediante agujero en D, sin chaveta.
  corona = Elemento.crear(
    "Corona PETG",
    25,
    25,
    SISTEMA,
    usa_chaveta=False
  )

  # Para cerrar el par exactamente se usa la fuerza tangencial sin
  # redondear: 245.25 * 42.5 / 99 = 105.2840909 N.
  ft_corona = 245.25 * 42.5 / 99

  corona.agregar_carga(
    CargaCilindrica.crear(
      "Fuerzas engranamiento",
      25,
      SISTEMA,
      radio_aplicacion=99,
      radial=39.91,
      tangencial=ft_corona,
      axial=42.32
    )
  )

  eje_2.agregar_elemento(corona)

  # Tambor: centro x = 115 mm, ancho 95 mm.
  tambor = Elemento.crear(
    "Tambor",
    115,
    95,
    SISTEMA,
    usa_chaveta=False
  )

  # Fuerza de la cuerda: 25 kg * 9.81 m/s² = 245.25 N.
  # Radio efectivo = 42.5 mm.
  # Sentido tangencial opuesto al de la corona.
  tambor.agregar_carga(
    CargaCilindrica.crear(
      "Tension de la cuerda",
      115,
      SISTEMA,
      radio_aplicacion=42.5,
      radial=0,
      tangencial=-245.25,
      axial=0
    )
  )

  eje_2.agregar_elemento(tambor)

  return eje_2


def main():
  eje = construir_eje_2()
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
