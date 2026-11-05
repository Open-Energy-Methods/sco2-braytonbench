"""Machine-readable measured-density validation report (not full EOS certification)."""
import csv, json, hashlib, statistics, platform
from pathlib import Path
from CoolProp.CoolProp import PropsSI
from CoolProp import __version__ as coolprop_version

path=Path("data/reference/mantilla2010_thermoml_density.csv")
rows=list(csv.DictReader(path.open(newline="")))
results=[]
for row in rows:
    T=float(row["T_K"])
    P=float(row["P_kPa"])*1000
    measured=float(row["rho_kg_m3"])
    calc=PropsSI("Dmass","T",T,"P",P,"HEOS::CO2")
    err=(calc-measured)/measured
    results.append({"T_K":T,"P_MPa":P/1e6,"rho_measured_kg_m3":measured,
        "rho_coolprop_kg_m3":calc,"relative_residual":err,
        "thermoml_combined_uncertainty_as_reported":float(row["thermoml_combined_uncertainty_as_reported"])})
err=[x["relative_residual"] for x in results]
group={}
for T in sorted(set(x["T_K"] for x in results)):
    e=[x["relative_residual"] for x in results if x["T_K"]==T]
    group[str(int(T))]={"count":len(e),"max_abs_percent":100*max(abs(i) for i in e),
        "rms_percent":100*(sum(i*i for i in e)/len(e))**.5}
result={"type":"experimental_CO2_PVT_density_comparison",
    "source":{"doi":"10.1021/je1001158",
        "thermoml_url":"https://trc.nist.gov/ThermoML/10.1021/je1001158.json",
        "measurements":len(rows),"csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest()},
    "model":{"fluid":"HEOS::CO2","CoolProp":coolprop_version,"python":platform.python_version()},
    "statistics":{"mean_bias_percent":100*statistics.mean(err),
        "max_abs_residual_percent":100*max(abs(x) for x in err),
        "rms_residual_percent":100*(sum(x*x for x in err)/len(err))**.5,
        "per_temperature":group},
    "worst_by_abs_residual":sorted(results,key=lambda x:abs(x["relative_residual"]),reverse=True)[:10],
    "all_points":results,
    "interpretation":"Independent experimental density comparison, not measured h/s/cp validation or a complete EOS certification",
    "acceptance":{"screen_max_abs_below_percent":2.0,"screen_rms_below_percent":1.0},
    "gate":"G1-E PARTIAL"}
out=Path("evidence/generated/mantilla2010_measured_density.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k not in ("all_points","worst_by_abs_residual")},indent=2))
print("TOP_WORST",json.dumps(result["worst_by_abs_residual"][:5],indent=2))
