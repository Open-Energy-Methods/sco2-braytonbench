"""Compare CO2 EOS with independent experimental *measurements*.

Mantilla et al., J. Chem. Eng. Data 55 (2010) 4611-4613.
The CSV contains the 49 actual NIST ThermoML observations, not EOS outputs.
Thresholds are initial engineering screening limits, NOT measured uncertainties.
"""
from pathlib import Path
import csv
import math
import pytest
pytest.importorskip("CoolProp", reason="requires real-fluid CI extras")
from CoolProp.CoolProp import PropsSI

CSV = Path(__file__).resolve().parents[1] / "data/reference/mantilla2010_thermoml_density.csv"

def observations():
    with CSV.open(newline="") as f:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]

def residuals():
    for point in observations():
        rho_calc = PropsSI("Dmass","T",point["T_K"],"P",point["P_kPa"]*1000,"HEOS::CO2")
        assert math.isfinite(rho_calc) and rho_calc>0
        yield ((rho_calc-point["rho_kg_m3"])/point["rho_kg_m3"],point)

def test_original_experimental_dataset_integrity():
    x = observations()
    assert len(x)==49
    assert sorted({int(p["T_K"]) for p in x})==[310,350,400,450]
    assert min(p["P_kPa"] for p in x)==999
    assert max(p["P_kPa"] for p in x)==159844
    assert all(p["rho_kg_m3"]>0 for p in x)

def test_measurement_residual_screen():
    errors=[e for e,_ in residuals()]
    max_abs=max(abs(e) for e in errors)
    rms=(sum(e*e for e in errors)/len(errors))**.5
    # Broad screen to detect unit, dataset, phase and backend regressions.
    # Not a statement that density is validated to 2% uncertainty.
    assert max_abs < .02, f"max relative measured density residual: {max_abs:.6%}"
    assert rms < .01, f"RMS relative measured density residual: {rms:.6%}"

@pytest.mark.parametrize("temperature_k",[310,350,400,450])
def test_individual_temperature_groups(temperature_k):
    err=[abs(e) for e,p in residuals() if p["T_K"]==temperature_k]
    assert len(err)>=5
    assert max(err)<.02
