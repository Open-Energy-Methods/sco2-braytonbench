"""TES-v0.4 schedules: physics, sign, hold and energy metrics."""
import math

import pytest

from sco2_braytonbench.thermal_storage import PackedBedSpec, PackedBedState
from sco2_braytonbench.tes_cycles import StorageStage, run_storage_schedule


def plant(n=24):
    return PackedBedSpec(
        length_m=1., area_m2=1., porosity=.4,
        fluid_density_kg_m3=1000., fluid_cp_j_kg_k=1000.,
        solid_density_kg_m3=2600., solid_cp_j_kg_k=800.,
        interphase_hv_w_m3_k=80000., n_cells=n
    )


def test_charge_hold_reverse_discharge_is_conservative_and_honestly_incomplete():
    s = plant()
    initial = PackedBedState.uniform(s, 350, 350)
    stages = (
        StorageStage("heat", "charge", 50, 650, 40),
        StorageStage("closed-hold", "hold", 10, 350, 0),
        StorageStage("cold-return", "discharge", 65, 350, -40),
    )
    r = run_storage_schedule(s, initial, stages, cold_k=350, hot_k=650)
    assert len(r.records) == 3
    assert r.records[0].energy_boundary_j > 0
    assert r.records[1].energy_boundary_j == 0
    assert r.records[2].energy_boundary_j < 0
    assert r.charged_energy_j > 0 and r.recovered_energy_j > 0
    assert r.charged_energy_j - r.recovered_energy_j == pytest.approx(
        r.stored_energy_change_j, abs=1e-4)
    assert abs(r.conservation_residual_j) < 1e-4
    assert r.solid_usable_capacity_j == pytest.approx(374400000.0)
    assert r.final_solid_soc >= 0.0
    assert r.complete_cycle is False
    assert r.gross_energy_efficiency is None  # incomplete cycle != round-trip efficiency
    assert r.records[2].t_end_s == pytest.approx(125)
    assert r.records[2].solid_soc < r.records[1].solid_soc


def test_hold_has_zero_boundary_flux_but_equilibrates_internal_fluid():
    s = plant(n=1)
    initial = PackedBedState.uniform(s, 600, 400)
    r = run_storage_schedule(
        s, initial, (StorageStage("hold", "hold", 10, 500, 0),),
        cold_k=350, hot_k=650, max_step_s=.05
    )
    assert r.records[0].energy_boundary_j == 0
    assert r.state.fluid_k[0] < 600
    assert r.state.solid_k[0] > 400
    assert r.gross_energy_efficiency is None
    assert abs(r.conservation_residual_j) < 1e-4


def test_discharge_without_earlier_charge_does_not_claim_roundtrip():
    s = plant(8)
    r = run_storage_schedule(
        s, PackedBedState.uniform(s, 650, 650),
        (StorageStage("discharge", "discharge", 20, 350, 40),),
        cold_k=350, hot_k=650
    )
    assert r.recovered_energy_j > 0
    assert r.charged_energy_j == 0
    assert r.gross_energy_efficiency is None
    assert r.complete_cycle is False


def test_wrong_operating_mode_rejected_instead_of_mislabelled():
    s = plant(8)
    with pytest.raises(ValueError, match="charge stage extracted"):
        run_storage_schedule(
            s, PackedBedState.uniform(s, 650, 650),
            (StorageStage("mislabel", "charge", 10, 350, 40),),
            cold_k=350, hot_k=650
        )
    with pytest.raises(ValueError, match="discharge stage added"):
        run_storage_schedule(
            s, PackedBedState.uniform(s, 350, 350),
            (StorageStage("mislabel", "discharge", 10, 650, 40),),
            cold_k=350, hot_k=650
        )


@pytest.mark.parametrize("stage", [
    ("x", "hold", 1, 350, 1),
    ("x", "charge", 1, 650, 0),
    ("x", "discharge", 1, 350, 0),
    ("", "hold", 1, 350, 0),
    ("x", "hold", -1, 350, 0),
    ("x", "hold", 1, float("nan"), 0),
    ("x", "unknown", 1, 350, 0),
])
def test_stage_rejects_invalid_boundary_or_mode(stage):
    with pytest.raises(ValueError):
        StorageStage(*stage)


def test_stage_name_uniqueness_and_valid_soc_domain():
    s = plant(4)
    st = PackedBedState.uniform(s, 350, 350)
    with pytest.raises(ValueError, match="unique"):
        run_storage_schedule(s, st, (
            StorageStage("same", "hold", 1, 350, 0),
            StorageStage("same", "hold", 1, 350, 0)
        ), cold_k=350, hot_k=650)
    with pytest.raises(ValueError):
        run_storage_schedule(s, st, (), cold_k=350, hot_k=650)
    with pytest.raises(ValueError):
        run_storage_schedule(s, st, (StorageStage("x", "hold", 1, 350, 0),),
                             cold_k=650, hot_k=350)


def test_complete_cycle_requires_full_state_return_not_just_net_joules():
    s = plant(4)
    init = PackedBedState.uniform(s, 350, 350)
    r = run_storage_schedule(s, init, (
        StorageStage("charge", "charge", 10, 650, 40),
        StorageStage("discharge", "discharge", 10, 350, -40)
    ), cold_k=350, hot_k=650, state_return_tolerance_k=0.01)
    assert r.max_cell_return_error_k > 0.01
    assert r.gross_energy_efficiency is None
    assert math.isfinite(r.stored_energy_change_j)
