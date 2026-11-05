"""G3.5 H1c — published Lei HB/HT correlations vs Stuttgart CO2.

This is an out-of-original-domain **cross-fluid/geometry transfer**,
not a calibrated or validated CO2 mixed-convection law. No HM formula
is supplied by Lei; HM is excluded, never interpolated. Every source
experiment ID and original four held-out nominal families persist.

Inputs from original H1b complete pointwise evidence; each original
HB/HT station has measured heat flux, *derived* bulk CO2 state and
source-reduced local HTC. Measured wall T is diagnostic ONLY for
wall-conditioned mode; flux-driven mode solves Tw without it.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean,median
import argparse,csv,json,math,random

from sco2_braytonbench.lei_mixed_convection import (
    CorrelationDomainError,lei_wall_state,solve_lei_wall,
)

SALT="BraytonBench-STU-H1-v1-2026-11-05"
ANOMALY="4MM_HM_77.5_10_20_90_A"

def csvrows(p):
    with Path(p).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def summarize(rows):
    if not rows:
        return {"n":0,"mape_pct":None,"bias_pct":None,"family_macro_mape_pct":None}
    err=[float(x["relative_residual_pct"]) for x in rows]
    family=defaultdict(list)
    runs=defaultdict(list)
    for x in rows:
        fam=x["nominal_family"];e=abs(float(x["relative_residual_pct"]))
        family[fam].append(e);runs[x["experiment_id"]].append(e)
    return {
        "n":len(rows),"n_runs":len(runs),"n_families":len(family),
        "mape_pct":mean(map(abs,err)),
        "bias_pct":mean(err),
        "median_ape_pct":median(map(abs,err)),
        "rmspe_pct":math.sqrt(mean(e*e for e in err)),
        "family_macro_mape_pct":mean(mean(v) for v in family.values()),
        "run_macro_mape_pct":mean(mean(v) for v in runs.values()),
        "n_within_source_reported_1sigma":sum(
            abs(float(x["relative_residual_pct"]))<=float(x["reported_htc_sigma_pct"])
            for x in rows if x["reported_htc_sigma_pct"]),
    }

def paired_bootstrap(rows,other_key="original_jackson_relative_error_pct"):
    """Cluster resample original nominal families, preserving axial correlation."""
    family=defaultdict(list)
    for x in rows:
        if x[other_key]=="":
            continue
        family[x["nominal_family"]].append(
            abs(float(x[other_key]))-abs(float(x["relative_residual_pct"])))
    if not family:return {"n_families":0}
    fam_means={k:mean(v) for k,v in family.items()}
    names=sorted(fam_means)
    rng=random.Random(20261105)
    samples=sorted(
        mean(fam_means[names[rng.randrange(len(names))]] for _ in names)
        for j in range(4000))
    return {
        "mean_family_equal_weight_advantage_pp":mean(fam_means.values()),
        "positive_means_Lei_lower_error":True,
        "family_bootstrap_2p5_to_97p5_pp":[samples[99],samples[3899]],
        "bootstrap_interpretation":"between-nominal-family sampling variation, not measurement uncertainty or validated generalization",
        "n_families":len(names),
        "n_Lei_lower_family_mape":sum(v>0 for v in fam_means.values()),
        "n_comparator_lower_family_mape":sum(v<0 for v in fam_means.values()),
        "held_out_paired_advantage_pp":{
            k:mean(v) for k,v in sorted(family.items()) if
            k in HELD_OUT
        },
    }

HELD_OUT=set()

def evaluate(index_path:Path,h1b_pointwise:Path,h1b_report:Path,out_dir:Path,props):
    global HELD_OUT
    report=json.loads(Path(h1b_report).read_text(encoding="utf-8"))
    if report["original_split"]["salt"]!=SALT or not report["original_split"]["no_parameter_fitting"]:
        raise ValueError("H1c cannot change H1a/H1b split or fit model coefficients")
    HELD_OUT=set(report["original_split"]["held_out_families"])
    if len(HELD_OUT)!=4:
        raise ValueError("four original held-out families required")
    meta={r["experiment_id"]:r for r in csvrows(index_path)}
    if len(meta)!=54 or ANOMALY not in meta:
        raise ValueError("original full Stuttgart source index required")
    allrows=csvrows(h1b_pointwise)
    jackson={ (r["experiment_id"],r["axial_position_m"]):r
             for r in allrows if r["model"]=="jackson_flux_inverted"}
    bishop={ (r["experiment_id"],r["axial_position_m"]):r
             for r in allrows if r["model"]=="bishop_flux_inverted"}
    if len(jackson)!=2318:
        raise ValueError("expected unchanged 2,318 H1b Jackson points")
    if any(r["experiment_id"]==ANOMALY for r in jackson.values()):
        raise ValueError("source anomaly STU-001 was unquarantined")
    if len({r["nominal_family"] for r in jackson.values()})!=18:
        raise ValueError("nominal families changed")

    exclusions=Counter()
    rows=[]
    counts=Counter(r["orientation"] for r in jackson.values())
    if counts != {"HB":790,"HM":738,"HT":790}:
        raise ValueError(f"orientation source inventory changed: {counts}")
    for key,source in sorted(jackson.items()):
        orient=source["orientation"]
        if orient=="HM":
            exclusions[("all","HM has no published Lei equation")]+=1
            continue
        if orient not in ("HB","HT"):
            raise ValueError("unrecognized source orientation")
        raw=meta[source["experiment_id"]]
        if source["split"] not in ("development","held_out") or (
            (source["nominal_family"] in HELD_OUT)!=(source["split"]=="held_out")
        ):
            raise ValueError("split leakage or changed split")
        p=float(raw["pressure_in_bar"])*1e5
        tb=float(source["bulk_temperature_k"])
        tw_obs=float(source["measured_wall_temperature_k_diagnostic_only"])
        diameter=float(source["diameter_mm"])*.001
        mass_flow=float(raw["mass_flow_kg_s"])
        q=float(source["input_heat_flux_w_m2"])
        h_exp=float(source["measured_derived_htc_w_m2_k"])
        G=4*mass_flow/(math.pi*diameter*diameter)
        try:
            mu=props("VISCOSITY","P",p,"T",tb,"HEOS::CO2")
            k=props("CONDUCTIVITY","P",p,"T",tb,"HEOS::CO2")
            rho=props("Dmass","P",p,"T",tb,"HEOS::CO2")
            re=G*diameter/mu
            for m in ("lei_wall_conditioned","lei_flux_inverted"):
                try:
                    if m=="lei_wall_conditioned":
                        result=lei_wall_state(
                            orient,re_bulk=re,mu_bulk_pa_s=mu,
                            k_bulk_w_m_k=k,rho_bulk_kg_m3=rho,
                            heat_flux_w_m2=q,diameter_m=diameter,
                            bulk_temperature_k=tb,wall_temperature_k=tw_obs,
                            pressure_pa=p,props=props)
                        it=0;energy_rel=0.
                    else:
                        result,it,energy_rel=solve_lei_wall(
                            orient,re_bulk=re,mu_bulk_pa_s=mu,
                            k_bulk_w_m_k=k,rho_bulk_kg_m3=rho,
                            heat_flux_w_m2=q,diameter_m=diameter,
                            bulk_temperature_k=tb,pressure_pa=p,props=props)
                    error=100*(result.htc_w_m2_k/h_exp-1)
                    if not math.isfinite(error):raise CorrelationDomainError("nonfinite error")
                except (CorrelationDomainError,ValueError,OverflowError,RuntimeError) as exc:
                    exclusions[(m,type(exc).__name__+":"+str(exc)[:90])]+=1
                    continue
                refb=bishop.get(key)
                rows.append({
                    "experiment_id":source["experiment_id"],
                    "nominal_family":source["nominal_family"],
                    "split":source["split"],"orientation":orient,
                    "diameter_mm":float(source["diameter_mm"]),
                    "axial_position_m":float(source["axial_position_m"]),
                    "x_over_d":float(source["x_over_d"]),
                    "model":m,
                    "wall_mode":("measured_wall_diagnostic" if m.endswith("conditioned")
                                  else "flux_driven_no_measured_wall_input"),
                    "source_liquid_original_26_or_43_mm":True,
                    "horizontal_CO2_4_or_8mm_cross_fluid_and_geometry_extrapolation":True,
                    "input_heat_flux_w_m2":q,
                    "bulk_temperature_k":tb,
                    "measured_wall_temperature_diagnostic_k":tw_obs,
                    "predicted_or_conditioned_wall_k":result.wall_temperature_k,
                    "htc_observed_derived_w_m2_k":h_exp,
                    "htc_calculated_w_m2_k":result.htc_w_m2_k,
                    "relative_residual_pct":error,
                    "reported_htc_sigma_pct":source["reported_htc_sigma_pct"],
                    "reynolds_bulk":re,
                    "prandtl_integrated":result.integrated_cp_j_kg_k*mu/k,
                    "grashof_heat_flux":result.grashof_heat_flux or "",
                    "wall_inverse_iterations":it,
                    "wall_energy_residual_relative":energy_rel,
                    "original_jackson_relative_error_pct":source["relative_residual_pct"],
                    "original_bishop_relative_error_pct":(
                        refb["relative_residual_pct"] if refb else ""),
                    "original_gnielinski_relative_error_pct":(
                        source["original_baseline_gnielinski_relative_residual_pct"]),
                })
        except (RuntimeError,ValueError,OverflowError,CorrelationDomainError) as exc:
            exclusions[("all",type(exc).__name__+":"+str(exc)[:90])]+=2
    out_dir.mkdir(parents=True,exist_ok=True)
    if rows:
        with (out_dir/"h1c_lei_pointwise.csv").open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    summary={}
    for mode in ("lei_wall_conditioned","lei_flux_inverted"):
        rr=[r for r in rows if r["model"]==mode]
        summary[mode]={
            "overall":summarize(rr),
            "held_out":summarize([r for r in rr if r["split"]=="held_out"]),
            "development":summarize([r for r in rr if r["split"]=="development"]),
            "by_orientation":{o:summarize([r for r in rr if r["orientation"]==o])
                                for o in ("HB","HT")},
            "by_diameter":{str(d):summarize([r for r in rr if r["diameter_mm"]==d])
                                for d in (4.,8.)},
            "same_eligible_station_comparators":{
                name:summarize([dict(r,relative_residual_pct=r[col]) for r in rr
                            if r[col]!=""])
                for name,col in (
                    ("jackson_hall_flux","original_jackson_relative_error_pct"),
                    ("bishop_flux","original_bishop_relative_error_pct"),
                    ("gnielinski_bulk","original_gnielinski_relative_error_pct"))
            },
            "paired_family_comparison_to_jackson":paired_bootstrap(rr),
        }
    output={
        "scientific_stage":"G3.5 H1c published Lei HB/HT model transfer audit",
        "source_equations":"Theologou et al (2022) Eq 17 referencing Lei et al (2017) DOI 10.1016/j.ijheatmasstransfer.2017.06.052",
        "source_data":"Stuttgart Mendeley DOI 10.17632/4mvk4nxrkz.1 CC BY 4.0",
        "original_lei_fit":"supercritical WATER, horizontal tubes ID 26 and 43 mm, p about 23-25 MPa",
        "tested_domain":"supercritical CO2 at p≈7.75MPa, 4 and 8 mm tubes; all calculated points are EXTRAPOLATION outside original fitted fluid/geometry domain",
        "existing_h1b_original_split":report["original_split"],
        "STU001_entire_run_quarantined":True,
        "no_regression_tuning_or_refitting":True,
        "no_HM_model_in_published_Lei":True,
        "source_station_inventory":dict(counts),
        "models":summary,
        "exclusions":[{"mode":k[0],"reason":k[1],"n":n}
                      for k,n in sorted(exclusions.items())],
        "critical_limits":[
            "Model transfer is outside original Lei 26/43mm supercritical WATER development domain",
            "No published Lei middle orientation (HM) formula; no interpolation invented",
            "Measured wall conditioned scores leak response-associated reduced experimental temperature",
            "Flux inversion still uses experimentally reported local q and derived bulk enthalpy",
            "Limited root scanning does not mathematically guarantee global uniqueness",
            "No input covariance or independent pressure sensor profile; no statistical prediction interval",
            "No fitted correction, no PCHE geometry, no Brayton cycle/industrial rig validation",
        ],
        "gate":"numerical_benchmark_not_industrial_HTC_validation",
    }
    (out_dir/"h1c_lei_report.json").write_text(json.dumps(output,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "models":{name:{
          "overall":v["overall"],"held_out":v["held_out"],
          "HB":v["by_orientation"]["HB"],
          "HT":v["by_orientation"]["HT"],
          "matched_comparators":v["same_eligible_station_comparators"],
          "paired":v["paired_family_comparison_to_jackson"]
        } for name,v in summary.items()},
        "exclusions":output["exclusions"],"note":output["tested_domain"]
    },indent=2,allow_nan=False))
    return output

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--index",type=Path,default=Path("data/validation/stuttgart/experiment_index.csv"))
    parser.add_argument("--h1b-dir",type=Path,default=Path("evidence/generated/stuttgart_h1b"))
    parser.add_argument("--out",type=Path,default=Path("evidence/generated/stuttgart_h1c"))
    args=parser.parse_args()
    from CoolProp.CoolProp import PropsSI
    import CoolProp
    result=evaluate(args.index,args.h1b_dir/"h1b_pointwise.csv",
                    args.h1b_dir/"h1b_report.json",args.out,PropsSI)
    result["CoolProp_version"]=CoolProp.__version__
    (args.out/"h1c_lei_report.json").write_text(json.dumps(result,indent=2)+"\n")

if __name__=="__main__":
    main()
