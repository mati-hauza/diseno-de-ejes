from dataclasses import dataclass

from .fatiga import goodman_modificado
from .fluencia import fluencia_von_mises


@dataclass
class Criterio:
  nombre: str
  clave: str
  funcion: callable
  color: str


_REGISTRO = [
  Criterio(
    nombre="Goodman modificado",
    clave="goodman",
    funcion=goodman_modificado,
    color="#1F618D"
  ),
  Criterio(
    nombre="Fluencia Von Mises",
    clave="fluencia",
    funcion=fluencia_von_mises,
    color="#C0392B"
  )
]


def registrar_criterio(nombre, clave, funcion, color="#555555"):
  """
  Agrega un criterio de falla al registro.

  La función debe tener la firma (esfuerzos, material, Se) y
  devolver el factor de seguridad.
  """
  for criterio in _REGISTRO:
    if criterio.clave == clave:
      raise ValueError(
        f"Ya existe un criterio con la clave '{clave}'."
      )

  _REGISTRO.append(
    Criterio(nombre, clave, funcion, color)
  )


def obtener_criterios():
  return list(_REGISTRO)


def aplicar_criterios(esfuerzos, material, Se):
  resultados = {}

  for criterio in _REGISTRO:
    resultados[criterio.clave] = criterio.funcion(
      esfuerzos, material, Se
    )

  return resultados
