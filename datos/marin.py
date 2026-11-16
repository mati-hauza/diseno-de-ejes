"""
Tablas de los factores de Marin (Shigley, capítulo 6).

Los valores están transcriptos de la sección 15.2 de las
especificaciones. No se extrapola fuera de los rangos declarados.
"""

# Tabla 6-2: acabado superficial. a y b para Sut en MPa.
ACABADO_SUPERFICIAL = {
  "esmerilado": {"a": 1.58, "b": -0.085},
  "maquinado": {"a": 4.51, "b": -0.265},
  "laminado_caliente": {"a": 57.7, "b": -0.718},
  "forja": {"a": 272.0, "b": -0.995}
}

# Tabla 6-5: temperatura. (°C, kd)
TEMPERATURA = [
  (20.0, 1.000),
  (50.0, 1.010),
  (100.0, 1.020),
  (150.0, 1.025),
  (200.0, 1.020),
  (250.0, 1.000),
  (300.0, 0.975),
  (350.0, 0.943),
  (400.0, 0.900),
  (450.0, 0.843),
  (500.0, 0.768),
  (550.0, 0.672),
  (600.0, 0.549)
]

TEMPERATURA_MIN = 20.0
TEMPERATURA_MAX = 600.0

# Tabla 6-4: confiabilidad. (R, ke)
CONFIABILIDAD = [
  (0.50, 1.000),
  (0.90, 0.897),
  (0.95, 0.868),
  (0.99, 0.814),
  (0.999, 0.753),
  (0.9999, 0.702),
  (0.99999, 0.659),
  (0.999999, 0.620)
]

CONFIABILIDAD_MIN = 0.50
CONFIABILIDAD_MAX = 0.999999

# Límite de fatiga de la probeta.
SUT_LIMITE_PROBETA = 1400e6  # Pa
SE_PROBETA_LIMITE = 700e6    # Pa
