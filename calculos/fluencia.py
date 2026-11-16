from math import inf, sqrt


def calcular_fluencia(esfuerzos, material):
  """
  Verificación de fluencia por Von Mises máximo, siguiendo el
  procedimiento de Shigley para ejes.
  """
  SB = esfuerzos.KfB * esfuerzos.sigma_Ba
  SNm = esfuerzos.KfN * esfuerzos.sigma_Nm
  SNa = esfuerzos.KfN * esfuerzos.sigma_Na

  sigma_x1 = SB + SNm + SNa
  sigma_x2 = -SB + SNm - SNa

  if abs(sigma_x1) >= abs(sigma_x2):
    sigma_x_max = sigma_x1
  else:
    sigma_x_max = sigma_x2

  tau_x_max = esfuerzos.Kfs * (
    abs(esfuerzos.tau_Tm) + esfuerzos.tau_Ta
  )

  sigma_prima_max = sqrt(
    sigma_x_max**2 + 3 * tau_x_max**2
  )

  sigma_prima_max_cons = (
    esfuerzos.sigma_prima_a + esfuerzos.sigma_prima_m
  )

  if sigma_prima_max <= 0:
    ny = inf
  else:
    ny = material.Sy / sigma_prima_max

  return {
    "SB": SB,
    "SNm": SNm,
    "SNa": SNa,
    "sigma_x1": sigma_x1,
    "sigma_x2": sigma_x2,
    "sigma_x_max": sigma_x_max,
    "tau_x_max": tau_x_max,
    "sigma_prima_max": sigma_prima_max,
    "sigma_prima_max_cons": sigma_prima_max_cons,
    "ny": ny
  }


def fluencia_von_mises(esfuerzos, material, Se=None):
  """
  Interfaz del registro de criterios para la fluencia.
  """
  return calcular_fluencia(esfuerzos, material)["ny"]
