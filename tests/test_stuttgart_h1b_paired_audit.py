"""Pure paired-audit checks with synthetic data and fixed grouping rules."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import pytest

def audit():
    p=Path(__file__).resolve().parents[1]/"scripts"/"stuttgart_h1b_paired_audit.py"
    sp=spec_from_file_location("h1b_paired_audit",p)
    mod=module_from_spec(sp);sp.loader.exec_module(mod)
    return mod

def test_all_original_18_nominal_families_required():
    m=audit()
    # Audit rejects changing the number of original nominal families,
    # even when a pair of models have a mathematical output.
    pair=lambda model:dict(experiment_id="example",axial_position_m="0.4",
        model=model,relative_residual_pct="5",
        split="held_out",nominal_family="changed",orientation="HB",
        input_heat_flux_w_m2="50000",measured_wall_temperature_k_diagnostic_only="320",
        bulk_temperature_k="310",measured_derived_htc_w_m2_k="5000")
    with pytest.raises(ValueError,match="nominal family"):
        m.compute([pair("bishop_flux_inverted"),pair("jackson_flux_inverted")])

def test_duplicate_model_station_rejected():
    m=audit()
    r=dict(experiment_id="a",axial_position_m="0.5",model="bishop_flux_inverted")
    with pytest.raises(ValueError,match="duplicate"):
        m.compute([r,r])
