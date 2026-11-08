"""Aggregate independently executed Kim variants without comparing unlike subsets.

The three variants are computed in separate CI matrix jobs, and
this script reads *published machine JSON* (no fitting or re-scoring)
to render a compact research report, summary CSV and an SVG chart.
This does NOT assert author-original parity or physical validity.
"""
from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path
from xml.sax.saxutils import escape

NAMES={
 "semi_empirical":"Semi-empirical (printed)",
 "empirical_literal":"Empirical (literal Eq24)",
 "empirical_hypothesis":"Empirical (unverified sign hypothesis)"
}

def aggregate(inputs:dict[str,Path],out:Path)->dict:
    data={}
    for name,path in inputs.items():
        d=json.loads(path.read_text(encoding="utf-8"))
        if d["variant"]!=name:
            raise ValueError(f"Kim H1d mismatched variant {name}")
        if d["original_eligible_source_stations"]!=2318 or d["HM_excluded_by_definition"]!=738:
            raise ValueError("H1a/H1b original source inventory changed")
        if d["source_fit_overlap"]["source_flux_exceeds_max"]!=1580:
            raise ValueError("unreported Kim original-fit heat-flux extrapolation")
        if not d["whole_anomalous_run_quarantined"] or not d["no_coefficient_fit"]:
            raise ValueError("source quarantine or no-fit gate changed")
        data[name]=d

    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for name,d in data.items():
        for mode in ("flux_driven_inverse","measured_wall_conditioned"):
            x=d["model_metrics"][mode]
            n=x["all"]["n"]
            rows.append({
              "variant":name,"variant_label":NAMES[name],
              "mode":mode,
              "admissible_HB_HT_candidates":1580,
              "n_success":n,"n_excluded":1580-n,
              "coverage_percent":100*n/1580,
              "mape_pct":x["all"]["mape_pct"],
              "held_out_n":x["held_out"]["n"],
              "held_out_mape_pct":x["held_out"]["mape_pct"],
              "HB_mape_pct":x["orientation"]["HB"]["mape_pct"],
              "HT_mape_pct":x["orientation"]["HT"]["mape_pct"],
              "max_q_balance_residual_relative":x["worst_heat_balance_relative"],
              "model_is_unverified_sign_hypothesis":name=="empirical_hypothesis",
              "all_inputs_outside_original_heat_flux_range":True,
              "measured_wall_target_leakage":mode=="measured_wall_conditioned",
            })
    with (out/"summary.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    def f(v,precision=2):
        return "not available" if v is None else f"{v:,.{precision}f}"
    markdown=[
      "# G3.5-H1d source-ambiguity and Stuttgart transfer benchmark",
      "",
      "Kim et al. (2019), DOI 10.1016/j.ijheatmasstransfer.2018.11.075.",
      "All Stuttgart points exceed the original source paper's maximal 26.9 kW/m² heat-flux range.",
      "Original source Eq24 and Table4 fitted negative exponent signs appear inconsistent; the sign hypothesis is NOT an authenticated correction.",
      "",
      "| Variant | Flux inverse coverage | Flux HTC MAPE | Held-out MAPE | HB | HT |",
      "|---|---:|---:|---:|---:|---:|"
    ]
    for x in rows:
        if x["mode"]!="flux_driven_inverse":continue
        markdown.append(f'| {x["variant_label"]} | {x["n_success"]}/1580 | '
            f'{f(x["mape_pct"])}% | {f(x["held_out_mape_pct"])}% | '
            f'{f(x["HB_mape_pct"])}% | {f(x["HT_mape_pct"])}% |')
    markdown += [
      "",
      "**Coverage is part of the result:** a lower MAPE on a smaller successful subset is not automatically a stronger correlation.",
      "The measured-wall-conditioned scores are diagnostics with target-related input and MUST NOT be described as independent predictions.",
      "No coefficients were adjusted, original Stuttgart four-family holdouts retained, STU-001 original anomaly quarantined.",
      "Source-original 10% errors are NOT reproduced by this analysis.",
      "",
      "## Source audit and next work",
      "",
      "Resolve the apparent printed empirical Eq24/Table4 sign inconsistency using authoritative author/source information or original 620-point data/code before any parity claim.",
      "Independent in-domain original-study reproduction and cross-domain predictive validation are both OPEN.",
      "",
    ]
    (out/"summary.md").write_text("\n".join(markdown),encoding="utf-8")

    # Two scientific panels with a logarithmic MAPE scale so
    # the literal millions-percent error cannot be hidden.
    dims=(840,360)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{dims[0]}" height="{dims[1]}" viewBox="0 0 {dims[0]} {dims[1]}">',
      '<rect width="840" height="360" fill="#ffffff"/>',
      '<text x="28" y="34" font-family="Arial" font-size="19" font-weight="bold">Kim 2019: conditional HTC prediction errors</text>',
      '<text x="28" y="56" font-family="Arial" font-size="12" fill="#555">Logarithmic y-axis · every point outside original heat-flux fit range</text>']
    top=86;bottom=290;top_log=8
    for power in (1,2,3,4,5,6,7):
        y=bottom-(power/top_log)*(bottom-top)
        svg+=[f'<line x1="72" x2="798" y1="{y:.1f}" y2="{y:.1f}" stroke="#dddddd"/>',
              f'<text x="28" y="{y+4:.1f}" font-family="Arial" font-size="12">{10**power:g}%</text>']
    colors={"semi_empirical":"#4a5d91","empirical_literal":"#9b4b4b","empirical_hypothesis":"#1e7962"}
    for i,name in enumerate(NAMES):
        x=115+i*250
        row=next(r for r in rows if r["variant"]==name and r["mode"]=="flux_driven_inverse")
        mape=row["mape_pct"] or 1
        h=min(bottom-top,max(0,math.log10(max(mape,1))/top_log*(bottom-top)))
        svg += [f'<rect x="{x}" y="{bottom-h:.2f}" width="110" height="{h:.2f}" fill="{colors[name]}"/>',
                f'<text x="{x+55}" y="{bottom-h-8:.2f}" font-family="Arial" font-size="12" text-anchor="middle">{escape(f(mape,1))}%</text>',
                f'<text x="{x+55}" y="310" font-family="Arial" font-size="12" text-anchor="middle">{escape(name.replace("_"," "))}</text>',
                f'<text x="{x+55}" y="328" font-family="Arial" font-size="11" text-anchor="middle">{row["n_success"]}/1580 successful</text>']
    svg += ['<text x="28" y="353" font-family="Arial" font-size="10" fill="#666">The alternative empirical exponent placement is NOT source-verified. Lower error does not imply in-domain validation.</text>','</svg>']
    (out/"htc_mape_log_scale.svg").write_text("\n".join(svg),encoding="utf-8")

    report={
       "models":{n:{
         "flux":{"all":d["model_metrics"]["flux_driven_inverse"]["all"],
                 "held_out":d["model_metrics"]["flux_driven_inverse"]["held_out"]},
         "source_fit_overlap":d["source_fit_overlap"],
         "model_source_interpretation":d["epistemic_warning"],
         "exclusions":d["explicit_exclusions"]}
          for n,d in data.items()},
       "success_gate":"Three fully executed source-aware models, no experimental validation in original fit region",
       "source_model_consistency":"Eq24/Table4 unresolved",
       "independent_original_study_parity":"NOT_DEMONSTRATED",
       "all_Stuttgart_fluxes_outside_original_Kim_range":True,
       "no_model_retraining":True,
       "predictions_may_fail_root_coverage":True,
    }
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print((out/"summary.md").read_text(encoding="utf-8"))
    return report

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-root",type=Path,default=Path("evidence/kim-h1d-collected"))
    parser.add_argument("--out",type=Path,default=Path("evidence/generated/kim-h1d-summary"))
    args=parser.parse_args()
    paths={name:args.input_root/("g35d-kim-"+name)/"kim_report.json" for name in NAMES}
    aggregate(paths,args.out)

if __name__=="__main__":
    main()
