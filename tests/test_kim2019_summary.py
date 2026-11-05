"""Research-artifact aggregation cannot hide missing source fit or coverage."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json

def module():
    file=Path(__file__).resolve().parents[1]/"scripts"/"kim_h1d_summary.py"
    spec=spec_from_file_location("kim_h1d_summary",file)
    m=module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_three_variant_summary_with_source_gates(tmp_path):
    m=module()
    source={}
    for variant in m.NAMES:
        x=tmp_path/variant/"kim_report.json"
        x.parent.mkdir()
        model={}
        for name in ("flux_driven_inverse","measured_wall_conditioned"):
            record={"n":100,"mape_pct":60.,
                    "signed_bias_pct":20.,"family_macro_mape_pct":50.}
            model[name]={
                "all":record,
                "held_out":{"n":25,"mape_pct":45.},
                "orientation":{"HB":{"mape_pct":55.},"HT":{"mape_pct":65.}},
                "worst_heat_balance_relative":.0002 if name=="flux_driven_inverse" else None,
            }
        x.write_text(json.dumps({
            "variant":variant,
            "original_eligible_source_stations":2318,
            "HM_excluded_by_definition":738,
            "whole_anomalous_run_quarantined":True,
            "no_coefficient_fit":True,
            "source_fit_overlap":{"source_flux_exceeds_max":1580},
            "model_metrics":model,
            "epistemic_warning":"hypothesis" if variant=="empirical_hypothesis" else "literal",
            "explicit_exclusions":[{"mode":"flux_driven_inverse","reason":"root","n":1480}]
        }))
        source[variant]=x
    d=m.aggregate(source,tmp_path/"result")
    assert (tmp_path/"result"/"summary.csv").exists()
    assert (tmp_path/"result"/"htc_mape_log_scale.svg").exists()
    assert (tmp_path/"result"/"summary.md").exists()
    assert d["independent_original_study_parity"]=="NOT_DEMONSTRATED"
    assert d["all_Stuttgart_fluxes_outside_original_Kim_range"] is True
    assert "unverified sign hypothesis" in (tmp_path/"result"/"summary.md").read_text().lower()
