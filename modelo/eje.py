from dataclasses import dataclass, field

from .apoyo import Apoyo
from .elemento import Elemento
from .carga import Carga, CargaDistribuida
from .momento import Momento

from .unidades import (
  SistemaUnidades,
  longitud_a_m
)


@dataclass
class Eje:
  longitud: float
  sistema: SistemaUnidades

  apoyos: list[Apoyo] = field(default_factory=list)
  elementos: list[Elemento] = field(default_factory=list)

  cargas: list[Carga] = field(default_factory=list)
  cargas_distribuidas: list[CargaDistribuida] = field(
    default_factory=list
  )

  momentos: list[Momento] = field(default_factory=list)

  @classmethod
  def crear(cls, longitud, sistema):
    return cls(
      longitud=longitud_a_m(longitud, sistema),
      sistema=sistema
    )

  def agregar_apoyo(self, apoyo):
    self.apoyos.append(apoyo)

  def agregar_elemento(self, elemento):
    self.elementos.append(elemento)

  def agregar_carga(self, carga):
    self.cargas.append(carga)

  def agregar_carga_distribuida(self, carga):
    self.cargas_distribuidas.append(carga)

  def agregar_momento(self, momento):
    self.momentos.append(momento)

  def obtener_todas_las_cargas(self):
    resultado = list(self.cargas)

    for elemento in self.elementos:
      resultado.extend(elemento.cargas)

    return resultado

  def obtener_todas_las_cargas_distribuidas(self):
    return list(self.cargas_distribuidas)

  def obtener_todos_los_momentos(self):
    resultado = list(self.momentos)

    for elemento in self.elementos:
      resultado.extend(elemento.momentos)

    return resultado

  def validar(self):
    errores = []

    if self.longitud <= 0:
      errores.append(
        "La longitud del eje debe ser positiva."
      )

    # Comprobar apoyos.
    if len(self.apoyos) != 2:
      errores.append(
        "El eje debe tener exactamente dos apoyos."
      )

    if len(self.apoyos) == 2:
      fijos = sum(a.fijo_axial for a in self.apoyos)

      if fijos != 1:
        errores.append(
          "Debe existir exactamente un apoyo fijo axial."
        )

      for i, apoyo in enumerate(self.apoyos):
        if apoyo.ancho <= 0:
          errores.append(
            f"El ancho del apoyo {apoyo.nombre} debe ser positivo."
          )

        if apoyo.inicio < 0 or apoyo.fin > self.longitud:
          errores.append(
            f"El apoyo {apoyo.nombre} está fuera del eje."
          )

        for otro in self.apoyos[i + 1:]:
          if max(apoyo.inicio, otro.inicio) < min(
            apoyo.fin, otro.fin
          ):
            errores.append(
              "Los apoyos no pueden superponerse."
            )

    # Comprobar elementos y sus cargas/momentos.
    for elemento in self.elementos:
      if elemento.ancho <= 0:
        errores.append(
          f"El ancho de {elemento.nombre} debe ser positivo."
        )

      if elemento.inicio < 0 or elemento.fin > self.longitud:
        errores.append(
          f"El elemento {elemento.nombre} está fuera del eje."
        )

      for carga in elemento.cargas:
        if not elemento.inicio <= carga.posicion <= elemento.fin:
          errores.append(
            f"La carga {carga.nombre} está fuera del elemento "
            f"{elemento.nombre}."
          )

      for momento in elemento.momentos:
        if not elemento.inicio <= momento.posicion <= elemento.fin:
          errores.append(
            f"El momento {momento.nombre} está fuera del elemento "
            f"{elemento.nombre}."
          )

    # Comprobar cargas independientes.
    for carga in self.cargas:
      if not 0 <= carga.posicion <= self.longitud:
        errores.append(
          f"La carga {carga.nombre} está fuera del eje."
        )

    # Comprobar cargas distribuidas.
    for carga in self.cargas_distribuidas:
      if carga.inicio < 0 or carga.fin > self.longitud:
        errores.append(
          f"La carga distribuida {carga.nombre} está fuera del eje."
        )

    # Comprobar momentos independientes.
    for momento in self.momentos:
      if not 0 <= momento.posicion <= self.longitud:
        errores.append(
          f"El momento {momento.nombre} está fuera del eje."
        )

    if errores:
      raise ValueError("\n".join(errores))

    return True