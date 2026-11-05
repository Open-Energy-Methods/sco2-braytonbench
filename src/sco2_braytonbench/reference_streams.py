"""Literature-derived sensible-stream reference models for independent G3 studies.

* DryAirNISTShomate: fixed 79% N2/21% O2 molar mixture, NIST Chemistry
  WebBook gas-phase Shomate polynomials. Ideal-gas sensible dh/ds at
  fixed composition and pressure, 300-1000 K. It is NOT combustion
  exhaust and omits argon, water vapour and carbon dioxide.
* CoolPropLiquidWater: HEOS::Water at a specified fixed pressure,
  with strict liquid-phase and temperature-domain validation.
  It excludes evaporation, pump work and pressure loss.

Both satisfy the same small cp/delta_h/delta_s/inverse contract used by
LinearCp. No general fluid-reference-state consistency is assumed:
only within-stream enthalpy and entropy DIFFERENCES are compared.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log
from .properties import DomainError


# NIST Chemistry WebBook SRD 69, Shomate in SI:
# cp[J/mol/K] = A+B*t+C*t**2+D*t**3+E/t**2; t=T/1000.
# h[kJ/mol] = A*t+B*t²/2+C*t³/3+D*t⁴/4-E/t+F-H
# s[J/mol/K] = A ln(t)+B*t+C*t²/2+D*t³/3-E/(2*t²)+G
# https://webbook.nist.gov/cgi/cbook.cgi?ID=C7727379&Mask=1  N2
# https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447&Mask=17 O2
# Polynomial coefficients are published numeric reference data.
_N2_LOW=(28.98641,1.853978,-9.647459,16.63537,0.000117,-8.671914,226.4168)
_N2_HIGH=(19.50583,19.88705,-8.598535,1.369784,0.527601,-4.935202,212.3900)
_O2_LOW=(31.32234,-20.23531,57.86644,-36.50624,-0.007374,-8.903471,246.7945)
_O2_HIGH=(30.03235,8.772972,-3.988133,0.788313,-0.741599,-11.32468,236.1663)
_N2_MOLAR_MASS_KG_MOL=0.0280134
_O2_MOLAR_MASS_KG_MOL=0.0319988

def _shomate(t_k:float,coeff:tuple[float,...])->tuple[float,float,float]:
    a,b,c,d,e,f,g=coeff
    t=t_k/1000.
    cp=a+b*t+c*t*t+d*t**3+e/t**2
    h=(a*t+b*t*t/2+c*t**3/3+d*t**4/4-e/t+f)*1000.
    s=a*log(t)+b*t+c*t*t/2+d*t**3/3-e/(2*t*t)+g
    return cp,h,s

@dataclass(frozen=True)
class DryAirNISTShomate:
    """79% N2/21% O2 by mole, constant composition and no pressure change."""
    minimum_temperature_k:float=300.
    maximum_temperature_k:float=1000.

    def __post_init__(self)->None:
        if (not all(isfinite(v) for v in (
             self.minimum_temperature_k,self.maximum_temperature_k))
            or self.minimum_temperature_k<300. or
            self.maximum_temperature_k>1000. or
            self.minimum_temperature_k>=self.maximum_temperature_k):
            raise DomainError("NIST dry-air model supported only within 300-1000 K")

    @property
    def molar_mass_kg_mol(self)->float:
        return .79*_N2_MOLAR_MASS_KG_MOL+.21*_O2_MOLAR_MASS_KG_MOL

    def _properties(self,t_k:float)->tuple[float,float,float]:
        if not isfinite(t_k) or not self.minimum_temperature_k<=t_k<=self.maximum_temperature_k:
            raise DomainError("NIST dry-air temperature outside documented range")
        n=_shomate(t_k,_N2_LOW if t_k<=500 else _N2_HIGH)
        o=_shomate(t_k,_O2_LOW if t_k<=700 else _O2_HIGH)
        # Shomate round-off creates tiny h/s discontinuities at the
        # published polynomial switches. Apply reference offsets to
        # the upper intervals so integrated sensible h/s is continuous
        # and the h(T) inverse remains defined at every target.
        if t_k>500:
            lower=_shomate(500.,_N2_LOW)
            upper=_shomate(500.,_N2_HIGH)
            n=(n[0],n[1]+lower[1]-upper[1],n[2]+lower[2]-upper[2])
        if t_k>700:
            lower=_shomate(700.,_O2_LOW)
            upper=_shomate(700.,_O2_HIGH)
            o=(o[0],o[1]+lower[1]-upper[1],o[2]+lower[2]-upper[2])
        m=self.molar_mass_kg_mol
        return tuple((.79*n[i]+.21*o[i])/m for i in range(3))

    def cp(self,t_k:float)->float:
        v=self._properties(t_k)[0]
        if v<=0 or not isfinite(v):
            raise DomainError("NIST cp nonpositive")
        return v

    def delta_h(self,t1:float,t2:float)->float:
        return self._properties(t2)[1]-self._properties(t1)[1]

    def delta_s(self,t1:float,t2:float)->float:
        return self._properties(t2)[2]-self._properties(t1)[2]

    def temperature_for_delta_h(self,t_start_k:float,dh_j_kg:float)->float:
        if not isfinite(dh_j_kg):
            raise DomainError("nonfinite target sensible enthalpy")
        hstart=self._properties(t_start_k)[1]
        target=hstart+dh_j_kg
        lo,hi=self.minimum_temperature_k,self.maximum_temperature_k
        hlo,hhi=self._properties(lo)[1],self._properties(hi)[1]
        if target<hlo-1e-5 or target>hhi+1e-5:
            raise DomainError("NIST air enthalpy target outside 300-1000 K")
        for _ in range(48):
            mid=(lo+hi)/2.
            if self._properties(mid)[1]<target:lo=mid
            else:hi=mid
        result=(lo+hi)/2.
        if abs(self.delta_h(t_start_k,result)-dh_j_kg)>max(1e-5,1e-8*abs(dh_j_kg)):
            raise DomainError("NIST air temperature inverse did not close")
        return result


@dataclass(frozen=True)
class CoolPropLiquidWater:
    """CoolProp HEOS::Water at fixed coolant pressure, no phase change."""
    pressure_pa:float=300000.
    minimum_temperature_k:float=280.
    maximum_temperature_k:float=340.

    def __post_init__(self)->None:
        if (not all(isfinite(v) for v in (
                self.pressure_pa,self.minimum_temperature_k,
                self.maximum_temperature_k)) or
            self.pressure_pa<=0 or self.minimum_temperature_k<=273.16 or
            self.maximum_temperature_k<=self.minimum_temperature_k):
            raise DomainError("invalid liquid-water pressure or temperature range")
        self._state(self.minimum_temperature_k,"Hmass")
        self._state(self.maximum_temperature_k,"Hmass")

    @staticmethod
    def _props():
        try:
            from CoolProp.CoolProp import PropsSI
        except ImportError as e:
            raise ImportError("install sco2-braytonbench[co2] for real water") from e
        return PropsSI

    def _state(self,t:float,key:str)->float:
        if not isfinite(t) or not self.minimum_temperature_k<=t<=self.maximum_temperature_k:
            raise DomainError("water temperature outside declared range")
        p=self.pressure_pa
        props=self._props()
        try:
            psat=props("P","T",t,"Q",0,"HEOS::Water")
            if p<=psat*1.00001:
                raise DomainError("coolant leaves guaranteed single-phase liquid regime")
            v=props(key,"P",p,"T",t,"HEOS::Water")
        except (ValueError,OverflowError,RuntimeError) as e:
            raise DomainError("CoolProp water state failed") from e
        if not isfinite(v):
            raise DomainError("nonfinite CoolProp water property")
        return float(v)

    def cp(self,t:float)->float:
        v=self._state(t,"Cpmass")
        if v<=0:raise DomainError("water cp must be positive")
        return v

    def delta_h(self,t1:float,t2:float)->float:
        return self._state(t2,"Hmass")-self._state(t1,"Hmass")

    def delta_s(self,t1:float,t2:float)->float:
        return self._state(t2,"Smass")-self._state(t1,"Smass")

    def temperature_for_delta_h(self,t_start_k:float,dh_j_kg:float)->float:
        if not isfinite(dh_j_kg):
            raise DomainError("nonfinite water sensible enthalpy change")
        h_start=self._state(t_start_k,"Hmass")
        if dh_j_kg==0:
            return float(t_start_k)  # avoid unnecessary P/H flash for zero duty
        p=self._props()
        h_target=h_start+dh_j_kg
        try:
            t=p("T","P",self.pressure_pa,"Hmass",h_target,"HEOS::Water")
            # Refine the P/H flash against direct P/T enthalpy with
            # cp=(dh/dT)_P; very small segment duties can otherwise
            # magnify the P/H numerical residual.
            for _ in range(6):
                self.cp(t)  # phase and declared-domain validation
                residual=self._state(t,"Hmass")-h_target
                if abs(residual)<=max(5e-5,1e-10*abs(dh_j_kg)):
                    return float(t)
                t-=residual/self.cp(t)
        except (ValueError,RuntimeError,OverflowError) as e:
            raise DomainError("water enthalpy inversion failed") from e
        raise DomainError("water enthalpy inversion did not close")
