from modelo.eje import Eje
from modelo.apoyo import Apoyo
from modelo.carga import CargaCartesiana, CargaCilindrica, CargaDistribuida
from modelo.elemento import Elemento
from modelo.momento import Momento
from modelo.unidades import SistemaUnidades

from calculos.solicitaciones import calcular_solicitaciones

from salidas.informe_solicitaciones import mostrar_informe
from salidas.diagramas_solicitaciones import generar_diagramas
from salidas.diagramas_eje import generar_diagramas_eje



def main():
  sistema = SistemaUnidades.INGLES

  eje = Eje.crear(11.5, sistema)

  eje.agregar_apoyo(
    Apoyo.crear("A", 0.75, 1, True, sistema)
  )

  eje.agregar_apoyo(
    Apoyo.crear("B", 10.75, 1, False, sistema)
  )
  
  engranaje3 = Elemento.crear(
                nombre="Engranaje 3",
                posicion=2.75,
                ancho=1.5,
                sistema=sistema
              )

  engranaje3.agregar_carga(
    CargaCilindrica.crear(
      nombre = "W3",
      posicion = 2.75,
      sistema = sistema,
      radio_aplicacion = 12/2,
      angulo_aplicacion = 0,
      axial=0,
      radial=-197,
      tangencial=540
    )
  )
  
  eje.agregar_elemento(engranaje3)
  
  engranaje4 = Elemento.crear(
                nombre="Engranaje 4",
                posicion=8.5,
                ancho=2,
                sistema=sistema
              )

  engranaje4.agregar_carga(
    CargaCilindrica.crear(
      nombre = "W4",
      posicion = 8.5,
      sistema = sistema,
      radio_aplicacion = 540*(12/2)/2430,
      angulo_aplicacion = 0,
      axial=0,
      radial=-885,
      tangencial=-2430
    )
  )

  eje.agregar_elemento(engranaje4)
  
  # OTRO EJEMPLO
  # sistema = SistemaUnidades.SI

  # eje = Eje.crear(540, sistema)

  # eje.agregar_apoyo(
  #   Apoyo.crear(
  #     nombre="A",
  #     posicion=20,
  #     ancho=40,
  #     fijo_axial=True,
  #     sistema=sistema
  #   )
  # )

  # eje.agregar_apoyo(
  #   Apoyo.crear(
  #     nombre="B",
  #     posicion=520,
  #     ancho=40,
  #     fijo_axial=False,
  #     sistema=sistema
  #   )
  # )

  # eje.agregar_carga(
  #   CargaCartesiana.crear(
  #     nombre="Carga",
  #     posicion=540-175-20,
  #     sistema=sistema,
  #     radio_aplicacion=50,
  #     angulo_aplicacion=0,
  #     Fx=-6000      
  #   )
  # )
  
  # eje.agregar_carga_distribuida(
  #   CargaDistribuida.crear(
  #     nombre="Peso distribuido",
  #     inicio=100,
  #     fin=500,
  #     sistema=sistema,
  #     qy=-0.1
  #   )
  # )
  
  eje.validar()

  resultado = calcular_solicitaciones(eje)

  mostrar_informe(eje, resultado)

  generar_diagramas(eje, resultado)

  generar_diagramas_eje(eje, resultado)
  

if __name__ == "__main__":
  main()
