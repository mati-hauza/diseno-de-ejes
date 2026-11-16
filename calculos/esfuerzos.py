from dataclasses import dataclass
from math import pi, sqrt


@dataclass
class Esfuerzos:
  x: float
  lado: int
  d: float

  A: float
  I: float
  J: float
  c: float

  N: float
  Vy: float
  Vz: float
  VR: float
  My: float
  Mz: float
  MR: float
  T: float

  Na: float
  Nm: float
  Ta: float
  Tm: float
  Ma: float
  Mm: float

  sigma_Na: float
  sigma_Nm: float
  sigma_Ba: float
  sigma_Bm: float
  tau_Ta: float
  tau_Tm: float

  KfN: float
  KfB: float
  Kfs: float

  sigma_a: float
  sigma_m: float
  tau_a: float
  tau_m: float

  sigma_prima_a: float
  sigma_prima_m: float


def calcular_esfuerzos(
  solicitaciones,
  x,
  lado,
  d,
  KfN=1.0,
  KfB=1.0,
  Kfs=1.0
):
  N = solicitaciones.evaluar("N", x, lado)
  Vy = solicitaciones.evaluar("Vy", x, lado)
  Vz = solicitaciones.evaluar("Vz", x, lado)
  VR = solicitaciones.evaluar("VR", x, lado)
  My = solicitaciones.evaluar("My", x, lado)
  Mz = solicitaciones.evaluar("Mz", x, lado)
  MR = solicitaciones.evaluar("MR", x, lado)
  T = solicitaciones.evaluar("T", x, lado)

  A = pi * d**2 / 4
  I = pi * d**4 / 64
  J = pi * d**4 / 32
  c = d / 2

  Ma = MR
  Mm = 0.0
  Na = 0.0
  Nm = N
  Ta = 0.0
  Tm = T

  sigma_Na = 4 * Na / (pi * d**2)
  sigma_Nm = 4 * Nm / (pi * d**2)
  sigma_Ba = 32 * Ma / (pi * d**3)
  sigma_Bm = 0.0
  tau_Ta = 16 * Ta / (pi * d**3)
  tau_Tm = 16 * Tm / (pi * d**3)

  sigma_a = KfB * sigma_Ba + KfN * sigma_Na
  sigma_m = KfB * sigma_Bm + KfN * sigma_Nm
  tau_a = Kfs * tau_Ta
  tau_m = Kfs * tau_Tm

  sigma_prima_a = sqrt(
    (KfB * sigma_Ba + KfN * sigma_Na / 0.85) ** 2
    + 3 * (Kfs * tau_Ta) ** 2
  )

  sigma_prima_m = sqrt(
    (KfB * sigma_Bm + KfN * sigma_Nm) ** 2
    + 3 * (Kfs * tau_Tm) ** 2
  )

  return Esfuerzos(
    x=x,
    lado=lado,
    d=d,
    A=A,
    I=I,
    J=J,
    c=c,
    N=N,
    Vy=Vy,
    Vz=Vz,
    VR=VR,
    My=My,
    Mz=Mz,
    MR=MR,
    T=T,
    Na=Na,
    Nm=Nm,
    Ta=Ta,
    Tm=Tm,
    Ma=Ma,
    Mm=Mm,
    sigma_Na=sigma_Na,
    sigma_Nm=sigma_Nm,
    sigma_Ba=sigma_Ba,
    sigma_Bm=sigma_Bm,
    tau_Ta=tau_Ta,
    tau_Tm=tau_Tm,
    KfN=KfN,
    KfB=KfB,
    Kfs=Kfs,
    sigma_a=sigma_a,
    sigma_m=sigma_m,
    tau_a=tau_a,
    tau_m=tau_m,
    sigma_prima_a=sigma_prima_a,
    sigma_prima_m=sigma_prima_m
  )
