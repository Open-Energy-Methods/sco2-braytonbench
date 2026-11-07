#!/usr/bin/env python3
"""TES-v0.9 deterministic replay from clean installed wheel/sdist environments.

Software compatibility evidence only. Nothing here fits or evaluates the
sealed TES-v0.7 test/OOD dataset, accesses facility data, or validates a plant.
"""
from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import math
from pathlib import Path
import sys

from sco2_braytonbench import CoolPropCO2, CycleInputs, IdealGasFixture, PressureLosses
from sco2_braytonbench import thermal_storage as core
from sco2_braytonbench.tes_schumann import schumann_inlet_step
from sco2_braytonbench.tes_cycles import StorageStage, run_storage_schedule
from sco2_braytonbench.tes_metrics import evaluate_tes_performance
from sco2_braytonbench.tes_coupling import advance_storage_to_cycle_snapshot
from sco2_braytonbench.tes_operating_window import OperatingInputs, run_operating_case
from sco2_braytonbench.tes_surrogate import (
    FEATURE_NAMES, TARGET_NAMES, features, normalized_targets, denormalize,
    clip_with_flag,
)

def insist(ok, reason):
    if not ok:
        raise AssertionError(reason)

def bed(n=16, hv=80000):
    return core.PackedBedSpec(1., 1., .4, 1000., 1000., 2600., 800., hv, n)

def grid():
    spec = bed(32)
    initial = core.PackedBedState.uniform(spec, 350, 350)
    result = core.step_packed_bed(spec, initial, inlet_k=650, mdot_kg_s=40,
                                  duration_s=30, max_step_s=.05)
    exact = schumann_inlet_step(spec, x_m=1, t_s=30, mdot_kg_s=40,
                               initial_k=350, inlet_k=650)
    insist(abs(result.conservation_residual_j) < 1e-4, "grid first law")
    insist(abs(result.outlet_k-exact.fluid_k) < 40, "Schumann discrepancy")
    return {"outlet_k": result.outlet_k, "analytic_outlet_k": exact.fluid_k,
            "energy_boundary_j": result.energy_boundary_j,
            "first_law_residual_j": result.conservation_residual_j,
            "substeps": result.n_substeps}

def schedule():
    spec = bed(12)
    result = run_storage_schedule(spec, core.PackedBedState.uniform(spec,350,350), (
        StorageStage("charge","charge",40,650,40),
        StorageStage("hold","hold",8,350,0),
        StorageStage("discharge","discharge",60,350,-40)),
        cold_k=350, hot_k=650)
    insist(abs(result.conservation_residual_j) < 1e-4, "schedule first law")
    insist(result.charged_energy_j > 0 and result.recovered_energy_j > 0,
           "staged energy mode")
    insist(not result.complete_cycle and result.gross_energy_efficiency is None,
           "incomplete cycle must not report roundtrip")
    return {"charged_energy_j": result.charged_energy_j,
            "recovered_energy_j": result.recovered_energy_j,
            "first_law_residual_j": result.conservation_residual_j,
            "final_solid_soc": result.final_solid_soc,
            "full_state_return_error_k": result.max_cell_return_error_k,
            "complete_cycle": result.complete_cycle,
            "gross_efficiency": result.gross_energy_efficiency,
            "outlet_k": [x.outlet_k for x in result.records]}

def coupling(real):
    spec = core.PackedBedSpec(1.,1.,.4,10.,1100.,2600.,800.,
                               10000. if real else 30000.,10 if real else 16)
    if real:
        props = CoolPropCO2()
        cycle = CycleInputs(8.5e6,24e6,310.,600.,20.,.89,.90,
                            PressureLosses(100e3,150e3,100e3,50e3),recuperator_ua_w_k=500e3,segments=12)
        initial,inlet,flow,dt,stack,ua,seg = 800.,750.,100.,.1,350.,1e6,12
    else:
        props = IdealGasFixture(cp=1000.,gas_constant=200.)
        cycle = CycleInputs(8e6,24e6,310.,670.,10.,.89,.90,
                            PressureLosses(100e3,150e3,100e3,50e3),recuperator_ua_w_k=0.,segments=6)
        initial,inlet,flow,dt,stack,ua,seg = 850.,650.,30.,.5,600.,200000.,6
    x=advance_storage_to_cycle_snapshot(
        props,cycle,spec,core.PackedBedState.uniform(spec,initial,initial),
        bed_inlet_k=inlet,mass_flow_kg_s=flow,duration_s=dt,
        minimum_gas_heater_exit_k=stack,maximum_heater_ua_w_k=ua,
        heater_segments=seg)
    insist(x.heater_to_co2_rate_w > 0, "coupling heater")
    insist(abs(x.combined_instantaneous_residual_w)
           < max(1.,abs(x.heater_to_co2_rate_w))*1e-7,"coupling first law")
    return {"bed_outlet_k":x.bed_outlet_temperature_k,
            "heater_exit_k":x.heater_gas_exit_temperature_k,
            "heater_w":x.heater_to_co2_rate_w,
            "shaft_w":x.shaft_rate_w,"cooler_w":x.cooler_rate_w,
            "combined_residual_w":x.combined_instantaneous_residual_w,
            "bed_interval_j":x.bed_step.energy_boundary_j,
            "time_basis":x.instantaneous_stage_time}

def operating():
    s=core.PackedBedSpec(1.,.1,.5,5.,1000.,1000.,700.,500.,12)
    r=run_operating_case(s,OperatingInputs(observations_per_stage=12))
    m=evaluate_tes_performance(s,core.PackedBedState.uniform(s,500,500),
                               cold_k=350,hot_k=650,ambient_k=300)
    insist(r.first_law_relative_residual < 1e-9,"grade first law")
    insist(r.useful_discharge_energy_j <= r.recovered_energy_j,"grade bound")
    return {"recovered_j":r.recovered_energy_j,
            "useful_above_500k_j":r.useful_discharge_energy_j,
            "first_law_relative_residual":r.first_law_relative_residual,
            "observed_discharge_bias_j":r.observation_quadrature_error_j,
            "solid_soc":r.charged_solid_soc,
            "complete_cycle":r.complete_cycle,
            "gross_efficiency":r.gross_round_trip_efficiency,
            "solid_capacity_j":m.design_solid_capacity_j,
            "fluid_capacity_j":m.design_fluid_capacity_j,
            "ambient_reversible_exergy_j":m.total_reversible_exergy_j,
            "thermocline_width_m":m.thermocline_width_m}

def surrogate_smoke(work):
    """Toy installed inference ABI, NEVER v0.7 sealed train/test/OOD."""
    import joblib
    import numpy as np
    from sklearn.ensemble import HistGradientBoostingRegressor
    X,YS=[],[[],[]]
    for flow in (.02,.05,.08):
        for hv in (300.,900.):
            s=core.PackedBedSpec(1.,.1,.5,5.,1000.,1000.,700.,hv,8)
            state=core.PackedBedState.uniform(s,350,350)
            turnover=(s.total_fluid_capacity_j_k+s.total_solid_capacity_j_k)/(flow*1000)
            for phase,inlet,signed,turn in (("charge",650.,flow,1.),
                                            ("discharge",350.,-flow,1.2)):
                for k in range(1,9):
                    step=core.step_packed_bed(s,state,inlet_k=inlet,
                        mdot_kg_s=signed,duration_s=turn*turnover/8)
                    state=step.state
                    row={"phase":phase,"phase_fraction":k/8,
                         "charge_turnovers":1.,"discharge_turnovers":1.2,
                         "flow_kg_s":flow,"hv_w_m3_k":hv,
                         "initial_k":350.,"hot_inlet_k":650.,
                         "fluid_outlet_k":step.outlet_k,
                         "solid_soc":sum(state.solid_k)/8/300 - 350/300}
                    X.append(features(row))
                    for arr,y in zip(YS,normalized_targets(row)):
                        arr.append(y)
    insist(len(X)==96 and len(X[0])==len(FEATURE_NAMES),"ML features")
    data=np.asarray(X,dtype="float64")
    models=tuple(HistGradientBoostingRegressor(
        max_iter=30,max_leaf_nodes=7,min_samples_leaf=4,
        learning_rate=.09,random_state=20261107,early_stopping=False
    ).fit(data,np.asarray(y,dtype="float64")) for y in YS)
    local=work/"v09_trusted_toy_smoke.joblib"
    joblib.dump(models,local,compress=3)
    restored=joblib.load(local)  # Only this process's own trusted payload.
    pred=[clip_with_flag(float(m.predict(data[[7]])[0])) for m in restored]
    insist(len(TARGET_NAMES)==2 and all(not p[1] for p in pred),"ML bounds")
    return {"toy_rows":len(X),"feature_names":list(FEATURE_NAMES),
            "target_names":list(TARGET_NAMES),
            "toy_predict_outlet_k":denormalize(
                {"initial_k":350.,"hot_inlet_k":650.},pred[0][0]),
            "toy_predict_soc":pred[1][0],
            "joblib_trusted_local_roundtrip":True,
            "sealed_test_or_ood_accessed":False,
            "full_v07_quality_claim":False}

def run(out,expected_prefix):
    origin=Path(core.__file__).resolve()
    insist(origin.is_relative_to(expected_prefix.resolve()),
           "installed package shadowed by checkout")
    insist(Path(sys.prefix).resolve()==expected_prefix.resolve(),
           "wrong venv selected")
    insist(md.version("sco2-braytonbench")=="0.5.0a0","package version drift")
    out.parent.mkdir(parents=True,exist_ok=True)
    result={
        "schema":"tes-v09-isolated-installed-replay-1",
        "evidence_class":"synthetic_software_replay_no_facility_validation",
        "parent_package":"0.5.0a0",
        "dependency_versions":{n:md.version(n) for n in
            ("CoolProp","numpy","scikit-learn","joblib")},
        "sealed_v07_evaluation_repeated":False,
        "scenarios":{
            "schumann_grid":grid(),
            "charge_hold_reverse_discharge":schedule(),
            "open_stream_ideal":coupling(False),
            "open_stream_real_co2":coupling(True),
            "temperature_grade":operating(),
            "surrogate_local_toy":surrogate_smoke(out.parent),
        }}
    def finite(x):
        if isinstance(x,float): insist(math.isfinite(x),"nonfinite replay")
        elif isinstance(x,dict):
            for value in x.values():finite(value)
        elif isinstance(x,(tuple,list)):
            for value in x:finite(value)
    finite(result)
    out.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",
                   encoding="utf-8")
    print(json.dumps({"gate":"TES_V09_INSTALLED_REPLAY_PASS",
                      "scenarios":sorted(result["scenarios"])}))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--expect-prefix",type=Path,required=True)
    a=p.parse_args()
    run(a.out,a.expect_prefix)

if __name__=="__main__":
    main()
