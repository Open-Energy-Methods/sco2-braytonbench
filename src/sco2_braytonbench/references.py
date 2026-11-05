"""Published Friedman & Rapp (2016) Table 2 pressure-only reconstruction.

Point numbers correspond to the PAPER Figure 2b; they must not be confused
with the internal reduced six-state numerical model.
"""
from dataclasses import dataclass
from .properties import DomainError

@dataclass(frozen=True)
class FR2016PressureMap:
    p: dict[int,float]

    def __getitem__(self,point:int)->float:
        return self.p[point]

def fr2016_pressure_map(p1_pa:float,p8_pa:float)->FR2016PressureMap:
    if p1_pa<=1e6 or p8_pa<=1e6:
        raise DomainError('reference-pressure mapping requires each boundary above 1 MPa')
    # Table 2, real recuperated column; all pressure drops in kPa.
    p={1:float(p1_pa),8:float(p8_pa)}
    p[2]=p[1]-80e3                   # section 1–2
    p[3]=p[8]+(40+100+5+50+10)*1e3   # reverse low-side closure
    p[4]=p[3]-10e3                   # section 3–4
    p[5]=p[4]-50e3                   # hot recuperator
    p[6]=p[5]-5e3                    # section 5–6
    p[7]=p[6]-100e3                  # pre-cooler
    p[9]=p[1]+(150+200+30+35)*1e3   # reverse high-side closure
    p[10]=p[9]-35e3                  # section 9–10
    p[11]=p[10]-30e3                 # cold recuperator
    p[12]=p[11]-200e3                # section 11–12
    if min(p.values())<=0 or p[2]<=p[3] or p[9]<=p[8]:
        raise DomainError('infeasible reference pressure mapping')
    if abs(p[7]-p[8]-40e3)>1e-5 or abs(p[12]-p[1]-150e3)>1e-5:
        raise DomainError('reference pressure graph did not close')
    return FR2016PressureMap(p)
