from dataclasses import dataclass, field
from math import isfinite

from .apoyo import Apoyo
from .carga import Carga, CargaCartesiana, CargaDistribuida
from .elemento import Elemento
from .escalonamiento import Escalonamiento
from .material import Material
from .momento import Momento
from .ranura import Ranura
from .tramo import Tramo

from .unidades import (
  SistemaUnidades,
  longitud_a_m,
  validar_sistema
)

GRAVEDAD = 9.81


@dataclass
class Eje:
  longitud: float
  sistema: SistemaUnidades

  material: Material | None = None
  n_min: float | None = None
  n_div: int = 1000

  tramos: list[Tramo] = field(default_factory=list)
  escalonamientos: list[Escalonamiento] = field(default_factory=list)
  apoyos: list[Apoyo] = field(default_factory=list)
  elementos: list[Elemento] = field(default_factory=list)
  ranuras: list[Ranura] = field(default_factory=list)

  cargas: list[Carga] = field(default_factory=list)
  cargas_distribuidas: list[CargaDistribuida] = field(
    default_factory=list
  )

  momentos: list[Momento] = field(default_factory=list)

  advertencias: list[str] = field(default_factory=list)

  def __post_init__(self):
    validar_sistema(self.sistema)

    if self.material is not None and not isinstance(
      self.material, Material
    ):
      raise TypeError(
        "El material debe ser una instancia de Material."
      )

    if not isfinite(self.longitud):
      raise ValueError(
        "La longitud del eje debe ser finita."
      )

    if self.n_min is not None:
      if not isfinite(self.n_min) or self.n_min <= 0:
        raise ValueError(
          "El factor de seguridad mínimo debe ser positivo "
          "y finito."
        )

    if not isinstance(self.n_div, int) or self.n_div < 1:
      raise ValueError(
        "La cantidad de divisiones de la malla debe ser un "
        "entero mayor o igual que 1."
      )

  @classmethod
  def crear(
    cls,
    longitud,
    sistema,
    material=None,
    n_min=None,
    n_div=1000
  ):
    return cls(
      longitud=longitud_a_m(longitud, sistema),
      sistema=sistema,
      material=material,
      n_min=n_min,
      n_div=n_div
    )

  # ------------------------------------------------------------------
  # Incorporación de componentes.
  # ------------------------------------------------------------------

  def agregar_tramo(self, tramo):
    if not isinstance(tramo, Tramo):
      raise TypeError("El tramo debe ser una instancia de Tramo.")
    self.tramos.append(tramo)

  def agregar_escalonamiento(self, escalonamiento):
    if not isinstance(escalonamiento, Escalonamiento):
      raise TypeError(
        "El escalonamiento debe ser una instancia de "
        "Escalonamiento."
      )
    self.escalonamientos.append(escalonamiento)

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

  def agregar_ranura(self, ranura):
    if not isinstance(ranura, Ranura):
      raise TypeError(
        "La ranura debe ser una instancia de Ranura."
      )

    self.ranuras.append(ranura)

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

  # ------------------------------------------------------------------
  # Consultas geométricas.
  # ------------------------------------------------------------------

  def obtener_todas_las_cargas(self):
    resultado = list(self.cargas)

    for elemento in self.elementos:
      resultado.extend(elemento.cargas)

      if elemento.masa:
        resultado.append(
          CargaCartesiana(
            nombre=f"Peso de {elemento.nombre}",
            posicion=elemento.posicion,
            radio_aplicacion=0.0,
            angulo_aplicacion=0.0,
            Fy=-elemento.masa * GRAVEDAD
          )
        )

    return resultado

  def obtener_todas_las_cargas_distribuidas(self):
    return list(self.cargas_distribuidas)

  def obtener_todos_los_momentos(self):
    resultado = list(self.momentos)

    for elemento in self.elementos:
      resultado.extend(elemento.momentos)

    return resultado

  def tramo_en(self, posicion, tolerancia=1e-9):
    """Devuelve el tramo que contiene la posición."""
    for tramo in self.tramos:
      if (
        tramo.x_inicio - tolerancia
        <= posicion
        <= tramo.x_fin + tolerancia
      ):
        return tramo

    return None

  def tramo_izquierdo(self, x_s, tolerancia=1e-9):
    for tramo in self.tramos:
      if abs(tramo.x_fin - x_s) <= tolerancia:
        return tramo
    return None

  def tramo_derecho(self, x_s, tolerancia=1e-9):
    for tramo in self.tramos:
      if abs(tramo.x_inicio - x_s) <= tolerancia:
        return tramo
    return None

  def diametro_local(self, posicion, lado=0):
    """Diámetro local del eje en la posición y lado indicados."""
    tolerancia = 1e-9 * max(abs(self.longitud), 1.0)

    if lado < 0:
      for tramo in self.tramos:
        if abs(tramo.x_fin - posicion) <= tolerancia:
          return tramo.d
      for tramo in self.tramos:
        if (
          tramo.x_inicio + tolerancia
          < posicion
          <= tramo.x_fin + tolerancia
        ):
          return tramo.d
    elif lado > 0:
      for tramo in self.tramos:
        if abs(tramo.x_inicio - posicion) <= tolerancia:
          return tramo.d
      for tramo in self.tramos:
        if (
          tramo.x_inicio - tolerancia
          <= posicion
          < tramo.x_fin - tolerancia
        ):
          return tramo.d

    tramo = self.tramo_en(posicion, tolerancia)
    if tramo is not None:
      return tramo.d

    raise ValueError(
      f"No se pudo determinar el diámetro local en x={posicion} m."
    )

  # ------------------------------------------------------------------
  # Validación.
  # ------------------------------------------------------------------

  def validar(self):
    errores = []
    self.advertencias = []

    tolerancia = 1e-9 * max(abs(self.longitud), 1.0)

    if not isfinite(self.longitud):
      errores.append(
        "La longitud del eje debe ser finita."
      )
    elif self.longitud <= 0:
      errores.append(
        "La longitud del eje debe ser positiva."
      )

    self._validar_tramos(errores, tolerancia)
    self._validar_escalonamientos(errores, tolerancia)
    self._validar_apoyos(errores, tolerancia)
    self._validar_elementos(errores, tolerancia)
    self._validar_ranuras(errores, tolerancia)
    self._validar_cargas(errores)
    self._validar_material(errores)

    if errores:
      raise ValueError("\n".join(errores))

    return True

  def _validar_tramos(self, errores, tolerancia):
    if not self.tramos:
      errores.append("El eje debe tener al menos un tramo.")
      return

    ordenados = sorted(self.tramos, key=lambda t: t.x_inicio)

    for i, tramo in enumerate(ordenados):
      if not all(isfinite(v) for v in (
        tramo.x_inicio,
        tramo.x_fin,
        tramo.d
      )):
        errores.append(
          "Las dimensiones de los tramos deben ser finitas."
        )
        continue

      if tramo.longitud <= 0:
        errores.append(
          f"El tramo que comienza en x={tramo.x_inicio} debe "
          "tener longitud positiva."
        )

      if tramo.d <= 0:
        errores.append(
          f"El diámetro del tramo que comienza en "
          f"x={tramo.x_inicio} debe ser positivo."
        )

      if i == 0:
        if abs(tramo.x_inicio) > tolerancia:
          errores.append(
            "Los tramos deben comenzar en x=0."
          )
      else:
        anterior = ordenados[i - 1]
        if abs(tramo.x_inicio - anterior.x_fin) > tolerancia:
          errores.append(
            "Los tramos deben ser contiguos y sin "
            "superposiciones."
          )

      if i == len(ordenados) - 1:
        if abs(tramo.x_fin - self.longitud) > tolerancia:
          errores.append(
            "Los tramos deben cubrir exactamente [0, L]."
          )

  def _validar_escalonamientos(self, errores, tolerancia):
    ordenados = sorted(self.tramos, key=lambda t: t.x_inicio)

    for anterior, siguiente in zip(ordenados, ordenados[1:]):
      if abs(anterior.d - siguiente.d) <= tolerancia:
        continue

      definido = any(
        abs(escalonamiento.x_s - anterior.x_fin) <= tolerancia
        for escalonamiento in self.escalonamientos
      )

      if not definido:
        errores.append(
          f"El cambio de diámetro en x={anterior.x_fin} debe "
          "estar definido por un escalonamiento."
        )

    for tramo in ordenados:
      radios_invadidos = 0.0

      for escalonamiento in self.escalonamientos:
        izquierdo = self.tramo_izquierdo(
          escalonamiento.x_s, tolerancia
        )
        derecho = self.tramo_derecho(
          escalonamiento.x_s, tolerancia
        )

        if izquierdo is None or derecho is None:
          continue

        menor = (
          izquierdo if izquierdo.d < derecho.d else derecho
        )

        if menor is tramo:
          radios_invadidos += escalonamiento.r

      if radios_invadidos > tramo.longitud + tolerancia:
        errores.append(
          f"Los filetes que invaden el tramo "
          f"[{tramo.x_inicio}, {tramo.x_fin}] suman "
          f"{radios_invadidos} m y superan su longitud."
        )

    for escalonamiento in self.escalonamientos:
      if not all(isfinite(v) for v in (
        escalonamiento.x_s,
        escalonamiento.r
      )):
        errores.append(
          "La posición y el radio de los escalonamientos deben ser "
          "finitos."
        )
        continue

      if escalonamiento.r <= 0:
        errores.append(
          f"El radio del escalonamiento x={escalonamiento.x_s} "
          "debe ser positivo."
        )

      izquierdo = self.tramo_izquierdo(
        escalonamiento.x_s, tolerancia
      )
      derecho = self.tramo_derecho(
        escalonamiento.x_s, tolerancia
      )

      if izquierdo is None or derecho is None:
        errores.append(
          f"El escalonamiento x={escalonamiento.x_s} debe "
          "coincidir con el límite entre dos tramos."
        )
        continue

      if abs(izquierdo.d - derecho.d) <= tolerancia:
        errores.append(
          f"El escalonamiento x={escalonamiento.x_s} debe "
          "separar dos tramos de diámetros distintos."
        )
        continue

      # Los diámetros mayor y menor se deducen de los tramos
      # adyacentes; no se informan en el escalonamiento.
      D = max(izquierdo.d, derecho.d)
      d = min(izquierdo.d, derecho.d)

      if escalonamiento.r > (D - d) / 2 + tolerancia:
        errores.append(
          f"El radio del escalonamiento x={escalonamiento.x_s} "
          f"no puede superar (D - d)/2 = "
          f"{(D - d) / 2 * 1000:.3f} mm."
        )

      menor = (
        izquierdo if izquierdo.d < derecho.d else derecho
      )

      if escalonamiento.r > menor.longitud + tolerancia:
        errores.append(
          f"El radio del escalonamiento x={escalonamiento.x_s} "
          "no cabe en la longitud del tramo de diámetro menor."
        )

      for apoyo in self.apoyos:
        if (
          apoyo.inicio - tolerancia
          <= escalonamiento.x_s
          <= apoyo.fin + tolerancia
        ):
          if (
            abs(escalonamiento.x_s - apoyo.inicio) <= tolerancia
            or abs(escalonamiento.x_s - apoyo.fin) <= tolerancia
          ):
            self.advertencias.append(
              f"El escalonamiento x={escalonamiento.x_s} "
              f"coincide con el borde del apoyo "
              f"{apoyo.nombre}."
            )
          else:
            errores.append(
              f"El escalonamiento x={escalonamiento.x_s} está "
              f"dentro del apoyo {apoyo.nombre}."
            )

      for elemento in self.elementos:
        # Un elemento puede apoyarse contra un escalonamiento en
        # cualquiera de sus dos caras; solo se prohíbe que el
        # escalonamiento quede estrictamente dentro del elemento.
        if (
          elemento.inicio + tolerancia
          < escalonamiento.x_s
          < elemento.fin - tolerancia
        ):
          errores.append(
            f"El escalonamiento x={escalonamiento.x_s} está "
            f"dentro del elemento {elemento.nombre}."
          )

  def _validar_apoyos(self, errores, tolerancia):
    nombres_apoyos = [apoyo.nombre for apoyo in self.apoyos]

    if len(set(nombres_apoyos)) != len(nombres_apoyos):
      errores.append(
        "Los nombres de los apoyos deben ser únicos."
      )

    if len(self.apoyos) != 2:
      errores.append(
        "El eje debe tener exactamente dos apoyos."
      )

    if len(self.apoyos) == 2:
      apoyo_a, apoyo_b = self.apoyos

      if abs(apoyo_a.posicion - apoyo_b.posicion) <= tolerancia:
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

      if apoyo.inicio < -tolerancia or apoyo.fin > self.longitud + tolerancia:
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

  def _validar_elementos(self, errores, tolerancia):
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

      if elemento.inicio < -tolerancia or elemento.fin > self.longitud + tolerancia:
        errores.append(
          f"El elemento {elemento.nombre} está fuera del eje."
        )

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

      tramo = self.tramo_en(
        (elemento.inicio + elemento.fin) / 2,
        tolerancia
      )

      fronteras_interiores = [
        t.x_inicio
        for t in self.tramos
        if elemento.inicio + tolerancia
        < t.x_inicio
        < elemento.fin - tolerancia
      ]

      if tramo is None or fronteras_interiores:
        errores.append(
          f"El elemento {elemento.nombre} debe estar "
          "completamente contenido en un solo tramo."
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

      if elemento.usa_chaveta:
        if elemento.a is None or elemento.a <= 0:
          errores.append(
            f"El elemento {elemento.nombre} tiene chaveta y "
            "debe informar un lado a positivo."
          )

        if elemento.material_chaveta is None:
          errores.append(
            f"El elemento {elemento.nombre} debe informar el "
            "material de la chaveta."
          )

        if elemento.material_cubo is None:
          errores.append(
            f"El elemento {elemento.nombre} debe informar el "
            "material del cubo."
          )

        if 0 <= elemento.inicio <= tolerancia:
          errores.append(
            f"El elemento con chaveta {elemento.nombre} no "
            "puede quedar al ras del extremo izquierdo."
          )

        if (
          self.longitud - tolerancia
          <= elemento.fin
          <= self.longitud
        ):
          errores.append(
            f"El elemento con chaveta {elemento.nombre} no "
            "puede quedar al ras del extremo derecho."
          )

        if (
          tramo is not None
          and elemento.a is not None
          and elemento.a >= tramo.d
        ):
          errores.append(
            f"El lado de la chaveta de {elemento.nombre} debe "
            "ser menor que el diámetro del tramo."
          )

        if (
          tramo is not None
          and elemento.a is not None
          and tramo.d > 0
        ):
          relacion = elemento.a / tramo.d
          if relacion < 0.2 or relacion > 0.3:
            self.advertencias.append(
              f"En {elemento.nombre}, a/d={relacion:.3f}; se "
              "recomienda a ≈ d/4 (0.2 ≤ a/d ≤ 0.3)."
            )

        if (
          elemento.material_chaveta is not None
          and self.material is not None
          and elemento.material_chaveta.Sy >= self.material.Sy
        ):
          self.advertencias.append(
            f"La chaveta de {elemento.nombre} tiene "
            "Sy mayor o igual que la del eje."
          )

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

  def _validar_ranuras(self, errores, tolerancia):
    for ranura in self.ranuras:
      if not 0 <= ranura.posicion <= self.longitud:
        errores.append(
          f"La ranura x={ranura.posicion} está fuera del eje."
        )
        continue

      tramo = self.tramo_en(ranura.posicion, tolerancia)

      if tramo is None:
        errores.append(
          f"La ranura x={ranura.posicion} no pertenece a "
          "ningún tramo."
        )
        continue

      if ranura.con_geometria:
        if ranura.ancho <= 0:
          errores.append(
            f"El ancho de la ranura x={ranura.posicion} debe "
            "ser positivo."
          )

        if ranura.profundidad <= 0:
          errores.append(
            f"La profundidad de la ranura x={ranura.posicion} "
            "debe ser positiva."
          )

        if ranura.profundidad >= tramo.d / 2:
          errores.append(
            f"La profundidad de la ranura x={ranura.posicion} "
            "debe ser menor que D/2."
          )

        if ranura.radio <= 0 or ranura.radio > ranura.ancho / 2 + tolerancia:
          errores.append(
            f"El radio de la ranura x={ranura.posicion} debe "
            "cumplir 0 < r ≤ a/2."
          )

        if (
          ranura.inicio < tramo.x_inicio - tolerancia
          or ranura.fin > tramo.x_fin + tolerancia
        ):
          errores.append(
            f"La ranura x={ranura.posicion} debe estar "
            "completamente contenida en un solo tramo."
          )

      for escalonamiento in self.escalonamientos:
        if (
          ranura.inicio - tolerancia
          <= escalonamiento.x_s
          <= ranura.fin + tolerancia
        ):
          errores.append(
            f"La ranura x={ranura.posicion} no puede coincidir "
            "con un escalonamiento."
          )

      for elemento in self.elementos:
        if not (
          ranura.fin < elemento.inicio - tolerancia
          or ranura.inicio > elemento.fin + tolerancia
        ):
          errores.append(
            f"La ranura x={ranura.posicion} no puede "
            f"superponerse con el elemento {elemento.nombre}."
          )

      for apoyo in self.apoyos:
        if not (
          ranura.fin < apoyo.inicio - tolerancia
          or ranura.inicio > apoyo.fin + tolerancia
        ):
          errores.append(
            f"La ranura x={ranura.posicion} no puede "
            f"superponerse con el apoyo {apoyo.nombre}."
          )

      for otra in self.ranuras:
        if otra is ranura:
          continue
        if max(ranura.inicio, otra.inicio) <= min(
          ranura.fin, otra.fin
        ):
          errores.append(
            "Las ranuras no pueden superponerse."
          )

  def _validar_cargas(self, errores):
    for carga in self.cargas:
      if not 0 <= carga.posicion <= self.longitud:
        errores.append(
          f"La carga {carga.nombre} está fuera del eje."
        )

    for carga in self.cargas_distribuidas:
      if carga.inicio < 0 or carga.fin > self.longitud:
        errores.append(
          f"La carga distribuida {carga.nombre} está fuera del eje."
        )

    for momento in self.momentos:
      if not 0 <= momento.posicion <= self.longitud:
        errores.append(
          f"El momento {momento.nombre} está fuera del eje."
        )

  def _validar_material(self, errores):
    if self.material is not None:
      if not isinstance(self.material, Material):
        errores.append(
          "El material del eje debe ser una instancia de Material."
        )
