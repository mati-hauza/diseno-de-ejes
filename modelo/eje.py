from dataclasses import dataclass, field
from math import isfinite

from .apoyo import Apoyo
from .elemento import Elemento
from .carga import Carga, CargaDistribuida
from .momento import Momento

from .unidades import (
  SistemaUnidades,
  longitud_a_m,
  validar_sistema
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

  def __post_init__(self):
    validar_sistema(self.sistema)

    if not isfinite(self.longitud):
      raise ValueError(
        "La longitud del eje debe ser finita."
      )

  @classmethod
  def crear(cls, longitud, sistema):
    return cls(
      longitud=longitud_a_m(longitud, sistema),
      sistema=sistema
    )

  def agregar_apoyo(self, apoyo):
    if not isinstance(apoyo, Apoyo):
      raise TypeError(
        "El apoyo debe ser una instancia de Apoyo."
      )

    self.apoyos.append(apoyo)

  def agregar_elemento(self, elemento):
    if not isinstance(elemento, Elemento):
      raise TypeError(
        "El elemento debe ser una instancia de Elemento."
      )

    self.elementos.append(elemento)

  def agregar_carga(self, carga):
    if not isinstance(carga, Carga):
      raise TypeError(
        "La carga debe ser una instancia de Carga. "
        "Para cargas distribuidas usá "
        "agregar_carga_distribuida()."
      )

    self.cargas.append(carga)

  def agregar_carga_distribuida(self, carga):
    if not isinstance(carga, CargaDistribuida):
      raise TypeError(
        "La carga distribuida debe ser una instancia de "
        "CargaDistribuida."
      )

    self.cargas_distribuidas.append(carga)

  def agregar_momento(self, momento):
    if not isinstance(momento, Momento):
      raise TypeError(
        "El momento debe ser una instancia de Momento."
      )

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

    if not isfinite(self.longitud):
      errores.append(
        "La longitud del eje debe ser finita."
      )
    elif self.longitud <= 0:
      errores.append(
        "La longitud del eje debe ser positiva."
      )

    nombres_apoyos = [apoyo.nombre for apoyo in self.apoyos]

    if len(set(nombres_apoyos)) != len(nombres_apoyos):
      errores.append(
        "Los nombres de los apoyos deben ser únicos."
      )

    # Comprobar apoyos.
    if len(self.apoyos) != 2:
      errores.append(
        "El eje debe tener exactamente dos apoyos."
      )

    if len(self.apoyos) == 2:
      apoyo_a, apoyo_b = self.apoyos

      tolerancia_apoyos = 1e-9 * max(
        abs(self.longitud), 1.0
      )

      if abs(apoyo_a.posicion - apoyo_b.posicion) <= tolerancia_apoyos:
        errores.append(
          "Los centros de los apoyos no pueden coincidir."
        )

      fijos = sum(a.fijo_axial for a in self.apoyos)

      if fijos != 1:
        errores.append(
          "Debe existir exactamente un apoyo fijo axial."
        )

      for i, apoyo in enumerate(self.apoyos):
        if not isfinite(apoyo.posicion) or not isfinite(apoyo.ancho):
          errores.append(
            f"La posición y el ancho del apoyo {apoyo.nombre} "
            "deben ser finitos."
          )
          continue

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
      if not isfinite(elemento.posicion) or not isfinite(elemento.ancho):
        errores.append(
          f"La posición y el ancho del elemento {elemento.nombre} "
          "deben ser finitos."
        )
        continue

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

    # Comprobar superposiciones y extremos de los elementos.
    for i, elemento in enumerate(self.elementos):
      for otro in self.elementos[i + 1:]:
        if max(elemento.inicio, otro.inicio) < min(
          elemento.fin, otro.fin
        ):
          errores.append(
            f"Los elementos {elemento.nombre} y {otro.nombre} "
            "no pueden superponerse."
          )

      for apoyo in self.apoyos:
        if max(elemento.inicio, apoyo.inicio) < min(
          elemento.fin, apoyo.fin
        ):
          errores.append(
            f"El elemento {elemento.nombre} no puede superponerse "
            f"con el apoyo {apoyo.nombre}."
          )

      tolerancia = 1e-9 * max(abs(self.longitud), 1.0)

      if 0 <= elemento.inicio <= tolerancia:
        errores.append(
          f"El elemento {elemento.nombre} no puede quedar al ras "
          "del extremo izquierdo."
        )

      if (
        self.longitud - tolerancia
        <= elemento.fin
        <= self.longitud
      ):
        errores.append(
          f"El elemento {elemento.nombre} no puede quedar al ras "
          "del extremo derecho."
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