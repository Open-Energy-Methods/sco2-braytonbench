"""G3.5-H1d: Kim (2019) actual CO2 mixed-convection source equations vs Stuttgart.

SOURCE: Full Kim et al. (2019) paper, DOI 10.1016/j.ijheatmasstransfer.2018.11.075,
Table 4, Eq (23),(24),(29),(30), section 3.4. Original data CC-BY
Stuttgart DOI 10.17632/4mvk4nxrkz.1. No source article PDF redistributed.

Variants:
  semi_empirical    published Eqs (23)/(29) and semi coefficients
  empirical_literal  published Eq(24)/(30) AS PRINTED with Table4 signs
  empirical_hypothesis Eq(24) SIGN placement hypothesis with Table4
                       (not certified authors' equation, NOT source-faithful)

Both diagnostic measured-wall-conditioned and prospective heat-flux-
driven wall-T inverse are computed, and distinguished in the report.

ALL original Stuttgart H1a/H1b source quarantine and 4 nominal-family
holdouts remain unchanged. None of these results is plant validation.
"""
from __future__ import annotations
import argparse,csv,json,math,random
from collections import defaultdict,Counter
from pathlib import Path
from statistics import mean,median

from sco2_braytonbench.kim2019 import (
   CoolPropCO2Transport,KimDomainError,evaluated_wall,solve_wall,
)

EXPECTED_COUNTS={"HB":790,"HT":790,"HM":738}
SALT="BraytonBench-STU-H1-v1-2026-11-05"
ANOMALY="4MM_HM_77.5_10_20_90_A"
VARIANTS={
 "semi_empirical":("semi_empirical","literal_denominator"),
 "empirical_literal":("empirical","literal_denominator"),
 "empirical_hypothesis":("empirical","signed_numerator_hypothesis")
}

def readcsv(file:Path):
    with file.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def percentile(a,q):
    if not a:return None
    a=sorted(a);v=(len(a)-1)*q;i=int(v)
    return a[i]+(a[min(len(a)-1,i+1)]-a[i])*(v-i)

def summary(rows:list[dict],error_field="relative_error_pct"):
    if not rows:
        return {"n":0,"mape_pct":None,"signed_bias_pct":None,
                "family_macro_mape_pct":None}
    errors=[float(x[error_field]) for x in rows if str(x[error_field]).strip()!=""]
    if len(errors)!=len(rows):
        raise ValueError("stationwise comparator missing")
    fam=defaultdict(list);byrun=defaultdict(list)
    for r,v in zip(rows,errors):
        fam[r["nominal_family"]].append(abs(v))
        byrun[r["experiment_id"]].append(abs(v))
    return {
        "n":len(rows),"families":len(fam),"runs":len(byrun),
        "mape_pct":mean(map(abs,errors)),
        "signed_bias_pct":mean(errors),
        "median_ape_pct":median(map(abs,errors)),
        "p90_ape_pct":percentile([abs(x) for x in errors],.90),
        "rmspe_pct":math.sqrt(mean(v*v for v in errors)),
        "family_macro_mape_pct":mean(mean(z) for z in fam.values()),
        "run_macro_mape_pct":mean(mean(z) for z in byrun.values())}

def paired_family_report(rows,baseline_field):
    matched=[r for r in rows if str(r.get(baseline_field,"")).strip()!=""]
    if not matched:return {"n":0}
    fam=defaultdict(list)
    for r in matched:
        err0=abs(float(r[baseline_field]))
        err1=abs(float(r["relative_error_pct"]))
        fam[r["nominal_family"]].append(err0-err1)
    averages={k:mean(vals) for k,vals in fam.items()}
    names=sorted(averages)
    rng=random.Random(20261105)
    samples=sorted(
       mean(averages[names[rng.randrange(len(names))]]
            for _ in names) for j in range(3000))
    return {
        "n_matched":len(matched),"families":len(names),
        "positive_advantage_pp_means_Kim_lower_error":True,
        "equal_family_mean_advantage_pp":mean(averages.values()),
        "n_families_Kim_lower_error":sum(v>0 for v in averages.values()),
        "n_families_baseline_lower_error":sum(v<0 for v in averages.values()),
        "family_bootstrap_percentile_interval_pp":[samples[74],samples[2924]],
        "bootstrap_warning":"Resampling original nominal families; not instrument covariance or external population confidence",
        "family_advantages_pp":averages}

def original_fit_envelope(p_pa,mass_flux,q,D,registry):
    src=registry["source_experimental_envelope"]
    S=src["postech"]; A=src["additional_Adebiyi_Hall"]
    # Exact original diameter available for POSTECH; Adebiyi-Hall
    # diameter not claimed from the compact registry, so this
    # calculation separately reports diameter overlap.
    return {
       "POSTECH_pressure":S["inlet_pressure_bar_min"]<=p_pa/1e5<=S["inlet_pressure_bar_max"],
       "POSTECH_mass_flux":S["mass_flux_kg_m2_s_min"]<=mass_flux<=S["mass_flux_kg_m2_s_max"],
       "POSTECH_q":S["wall_heat_flux_kw_m2_min"]<=q/1e3<=S["wall_heat_flux_kw_m2_max"],
       "POSTECH_exact_diameter":abs(D-S["tube_inner_diameter_m"])<1e-8,
       "Adebiyi_Hall_pressure":A["pressure_bar_min"]<=p_pa/1e5<=A["pressure_bar_max"],
       "Adebiyi_Hall_mass_flux":A["mass_flux_kg_m2_s_min"]<=mass_flux<=A["mass_flux_kg_m2_s_max"],
       "Adebiyi_Hall_q":A["heat_flux_kw_m2_min"]<=q/1e3<=A["heat_flux_kw_m2_max"],
       "valid_in_POSTECH_fitted_P_G_q_and_D":(
           S["inlet_pressure_bar_min"]<=p_pa/1e5<=S["inlet_pressure_bar_max"]
           and S["mass_flux_kg_m2_s_min"]<=mass_flux<=S["mass_flux_kg_m2_s_max"]
           and S["wall_heat_flux_kw_m2_min"]<=q/1e3<=S["wall_heat_flux_kw_m2_max"]
           and abs(D-S["tube_inner_diameter_m"])<1e-8),
    }

def evaluate(index_file:Path,h1b_file:Path,h1b_report_file:Path,
             destination:Path,variant:str,properties,
             source_registry=None):
    from sco2_braytonbench.kim2019 import registry as load_registry
    if variant not in VARIANTS:raise ValueError("unrecognized model variant")
    source_registry=source_registry or load_registry()
    meta={x["experiment_id"]:x for x in readcsv(index_file)}
    if len(meta)!=54 or ANOMALY not in meta:
        raise ValueError("original 54 source experiments required")
    h1b=json.loads(h1b_report_file.read_text(encoding="utf-8"))
    split=h1b["original_split"]
    if split["salt"]!=SALT or not split["no_parameter_fitting"] or len(split["held_out_families"])!=4:
        raise ValueError("original held-out nominal families changed")
    held=set(split["held_out_families"])
    rows=[r for r in readcsv(h1b_file) if r["model"]=="jackson_flux_inverted"]
    if len(rows)!=2318:
        raise ValueError(f"expected 2318 H1b eligible observations, got {len(rows)}")
    if Counter(x["orientation"] for x in rows)!=EXPECTED_COUNTS:
        raise ValueError("original top/middle/bottom station counts changed")
    if any(x["experiment_id"]==ANOMALY for x in rows):
        raise ValueError("anomalous source experiment STU-001 reintroduced")
    if len({x["nominal_family"] for x in rows})!=18:
        raise ValueError("family grouping changed")
    bishop={(r["experiment_id"],r["axial_position_m"]):r
            for r in readcsv(h1b_file) if r["model"]=="bishop_flux_inverted"}
    output=[]
    exclusions=Counter()
    q_domains=Counter()
    model,conv=VARIANTS[variant]
    for source in rows:
        orientation=source["orientation"]
        if orientation=="HM":
            exclusions[("all","no_Kim_HM_equation")]+=1
            continue
        fam=source["nominal_family"];experiment=source["experiment_id"]
        if (fam in held)!=(source["split"]=="held_out"):
            raise ValueError("unexpected heldout identifier or split leakage")
        index=meta[experiment]
        try:
            p=float(index["pressure_in_bar"])*1e5
            D=float(source["diameter_mm"])/1e3
            tb=float(source["bulk_temperature_k"])
            tw_measured=float(source["measured_wall_temperature_k_diagnostic_only"])
            mass=float(index["mass_flow_kg_s"])
            q=float(source["input_heat_flux_w_m2"])
            observed=float(source["measured_derived_htc_w_m2_k"])
            G=4*mass/(math.pi*D*D)
            domain=original_fit_envelope(p,G,q,D,source_registry)
            q_domains["source_flux_exceeds_max"]+=int(q/1e3>max(
               source_registry["source_experimental_envelope"]["postech"]["wall_heat_flux_kw_m2_max"],
               source_registry["source_experimental_envelope"]["additional_Adebiyi_Hall"]["heat_flux_kw_m2_max"]))
            q_domains["original_postech_full_P_G_q_D"]+=int(all(domain.values()))
        except (KeyError,ValueError,ZeroDivisionError,OverflowError):
            exclusions[("all","malformed_source_record")]+=2
            continue
        for mode in ("measured_wall_conditioned","flux_driven_inverse"):
            try:
                if mode=="measured_wall_conditioned":
                    result=evaluated_wall(
                        orientation,model,conv,p_pa=p,tbulk_k=tb,
                        twall_k=tw_measured,q_w_m2=q,
                        mass_flow_kg_s=mass,diameter_m=D,
                        properties=properties)
                    iterations=0
                    residual=None
                else:
                    result,iterations,residual=solve_wall(
                        orientation,model,conv,p_pa=p,tbulk_k=tb,
                        q_w_m2=q,mass_flow_kg_s=mass,diameter_m=D,
                        properties=properties)
                err=100*(result.htc_w_m2_k/observed-1)
                if not math.isfinite(err):
                    raise KimDomainError("unbounded source transfer prediction")
            except (KimDomainError,ValueError,RuntimeError,OverflowError) as exc:
                exclusions[(mode,type(exc).__name__+":"+str(exc)[:100])]+=1
                continue
            b=bishop.get((experiment,source["axial_position_m"]))
            output.append({
                "experiment_id":experiment,"nominal_family":fam,
                "split":source["split"],"orientation":orientation,
                "model":variant,"mode":mode,
                "diameter_mm":float(source["diameter_mm"]),
                "axial_position_m":float(source["axial_position_m"]),
                "bulk_temperature_k":tb,
                "measured_wall_temperature_k_diagnostic_only":tw_measured,
                "solved_or_conditioned_wall_k":result.wall_temperature_k,
                "pressure_pa":p,"mass_flux_kg_m2_s":G,
                "source_reported_heat_flux_w_m2":q,
                "experimental_reduced_htc_w_m2_k":observed,
                "model_htc_w_m2_k":result.htc_w_m2_k,
                "relative_error_pct":err,
                "source_sigma_htc_pct":source["reported_htc_sigma_pct"],
                "source_is_outside_POSTECH_fitted_domain":not all(
                    domain[k] for k in ("POSTECH_pressure",
                                       "POSTECH_mass_flux","POSTECH_q",
                                       "POSTECH_exact_diameter")),
                "original_source_flux_exceeds_both_dataset_maxima":
                    q/1e3>26.9,
                "nu_mixed":result.nu,"nu_fc":result.nu_forced,
                "nu_nc":result.nu_natural,
                "Q_bulk":result.q_b,"Gr_heat_flux":result.gr_q,
                "beta_bulk_1_k":result.beta_bulk_1_k,
                "rho_temperature_averaged":result.density_average,
                "mu_temperature_averaged":result.viscosity_average,
                "conductivity_temperature_averaged":result.conductivity_average,
                "cp_temperature_averaged":result.cp_average,
                "property_quad_segments":result.quadrature_subintervals,
                "wall_inverse_iterations":iterations,
                "wall_heat_residual_relative":residual,
                "matched_jackson_flux_error_pct":source["relative_residual_pct"],
                "matched_bishop_flux_error_pct":
                    b["relative_residual_pct"] if b else "",
                "matched_gnielinski_error_pct":
                    source["original_baseline_gnielinski_relative_residual_pct"],
            })

    destination.mkdir(parents=True,exist_ok=True)
    if output:
        with (destination/"kim_pointwise.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(output[0]))
            w.writeheader();w.writerows(output)
    metrics={}
    for mode in ("measured_wall_conditioned","flux_driven_inverse"):
        subset=[x for x in output if x["mode"]==mode]
        metrics[mode]={
            "all":summary(subset),
            "held_out":summary([x for x in subset if x["split"]=="held_out"]),
            "development":summary([x for x in subset if x["split"]=="development"]),
            "orientation":{x:summary([r for r in subset if r["orientation"]==x])
                           for x in ("HB","HT")},
            "diameter_mm":{str(x):summary([r for r in subset if r["diameter_mm"]==x])
                           for x in (4.,8.)},
            "paired_matched_jackson":paired_family_report(
                subset,"matched_jackson_flux_error_pct"),
            "paired_matched_bishop":paired_family_report(
                subset,"matched_bishop_flux_error_pct"),
            "paired_matched_gnielinski":paired_family_report(
                subset,"matched_gnielinski_error_pct"),
            "worst_heat_balance_relative":max(
                [x["wall_heat_residual_relative"] for x in subset
                 if x["wall_heat_residual_relative"] is not None],default=None),
        }
    report={
      "milestone":"G3.5 H1d Kim 2019 original-source interpretation audit",
      "variant":variant,
      "source_doi":"10.1016/j.ijheatmasstransfer.2018.11.075",
      "original_data_doi":"10.17632/4mvk4nxrkz.1",
      "source_registry_version":source_registry["schema_version"],
      "printed_eq24_or_hypothesis":conv,
      "epistemic_warning":(
        "HYPOTHESIS, not verified original author interpretation" if
        conv=="signed_numerator_hypothesis" else
        "literal printed Eq24 / Eq23 and original published signed coefficients"
      ),
      "full_original_Stuttgart_experiments":54,
      "original_eligible_source_stations":2318,
      "HB_candidate":790,"HT_candidate":790,
      "HM_excluded_by_definition":738,
      "holdouts_unchanged":sorted(held),
      "whole_anomalous_run_quarantined":True,
      "no_coefficient_fit":True,
      "source_fit_overlap":dict(q_domains),
      "model_metrics":metrics,
      "explicit_exclusions":[{"mode":k[0],"reason":k[1],"n":n}
                             for k,n in sorted(exclusions.items())],
      "interpretation_constraints":[
         "Original Kim source empirical Eq24 appears inconsistent with Table4 negative exponents: both literal and separately identified unverified sign hypotheses evaluated.",
         "Measured wall T conditioning leaks source target-related measured data and is not independent predictive validation.",
         "Flux inversion only uses reported heat flux and measured-inlet-anchored bulk enthalpy, not measured wall T.",
         "Fitted source original POSTECH q max25.9kW/m2 Adebiyi-Hall max26.9; Stuttgart source original q minimum exceeds30 kW/m2: source-domain EXTRAPOLATION for every point.",
         "No Kim middle orientation correlation, HM excluded entirely.",
         "Local experimental HTC is derived from reported heat flux and measured wall/bulk T; uncertainties are correlated.",
         "No CO2 full cycle, PCHE or industrial plant UA validation.",
      ],
      "scientific_gate":"source_equation_numerical_audit_no_industrial_or_original_error_replication",
    }
    (destination/"kim_report.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "variant":variant,
        "source_domain":report["source_fit_overlap"],
        "results":{k:{"all":v["all"],"held_out":v["held_out"],
                       "orientation":v["orientation"],
                       "matched_jackson":v["paired_matched_jackson"],
                       "worst_flux_residual":v["worst_heat_balance_relative"]}
                    for k,v in metrics.items()},
        "exclusions":report["explicit_exclusions"]
    },indent=2,allow_nan=False))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--variant",required=True,choices=list(VARIANTS))
    p.add_argument("--source",type=Path,default=Path("data/validation/stuttgart/experiment_index.csv"))
    p.add_argument("--h1b-dir",type=Path,default=Path("evidence/generated/stuttgart_h1b"))
    p.add_argument("--out-root",type=Path,default=Path("evidence/generated/stuttgart_h1d"))
    a=p.parse_args()
    import CoolProp
    r=evaluate(a.source,a.h1b_dir/"h1b_pointwise.csv",
               a.h1b_dir/"h1b_report.json",
               a.out_root/a.variant,a.variant,CoolPropCO2Transport())
    print("CoolProp version",CoolProp.__version__,"file",a.out_root/a.variant/"kim_report.json")

if __name__=="__main__":
    main()
