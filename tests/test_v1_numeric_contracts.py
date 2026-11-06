"""WP1: numerical contract/fail-closed regression checks.

Synthetic ideal-gas fixture inputs verify input handling only; no claim
about experimental CO2 validity follows from passing these tests.
"""
from dataclasses import replace
from math import isfinite

import pytest

from sco2_braytonbench.core import PressureLosses
from sco2_braytonbench.cycle import CycleInputs, solve_cycle
from sco2_braytonbench.exchangers import (
    _lmtd, segmented_recuperator, waste_gas_heater,
)
from sco2_braytonbench.properties import DomainError, IdealGasFixture

F = IdealGasFixture(cp=1000., gas_constant=200.)


def hx_kwargs():
    return dict(
        props=F, cold=F.tp(2e6, 350.), hot=F.tp(1e6, 700.),
        p_cold_out=2e6, p_hot_out=1e6,
        m_cold=10., m_hot=10., effectiveness=0.4, n=10,
    )


def heater_kwargs():
    return dict(
        props=F, co2_in=F.tp(2e6, 350.), co2_out=F.tp(2e6, 450.),
        m_co2=10., t_gas_in=650., m_gas=20., cp_gas=1100.,
        min_pinch_k=10., n=10,
    )


def test_normal_analytical_heat_transfer_still_produces_finite_output():
    hx = segmented_recuperator(**hx_kwargs())
    heater = waste_gas_heater(**heater_kwargs())
    assert 0 < hx.q_w < hx.qmax_w
    assert hx.required_ua_w_k > 0
    assert heater.q_w == pytest.approx(1e6)
    assert heater.gas_out_k < 650.
    assert all(isfinite(x) for x in (
        hx.required_ua_w_k, hx.min_approach_k,
        heater.required_ua_w_k, heater.min_approach_k,
    ))


@pytest.mark.parametrize("bad", [
    float("nan"), float("inf"), float("-inf"), 0., -1.,
])
@pytest.mark.parametrize("field", ["m_cold", "m_hot", "p_cold_out", "p_hot_out"])
def test_nonphysical_hx_flow_or_pressure_rejected(field, bad):
    kwargs = hx_kwargs()
    kwargs[field] = bad
    with pytest.raises(DomainError):
        segmented_recuperator(**kwargs)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1, 1.1])
def test_nonphysical_effectiveness_rejected(bad):
    kwargs = hx_kwargs()
    kwargs["effectiveness"] = bad
    with pytest.raises(DomainError, match="effectiveness"):
        segmented_recuperator(**kwargs)


@pytest.mark.parametrize("bad", [2, -5, 8.5, True, float("nan")])
def test_invalid_segment_count_rejected_for_recuperator(bad):
    kwargs = hx_kwargs()
    kwargs["n"] = bad
    with pytest.raises(DomainError, match="segment count"):
        segmented_recuperator(**kwargs)


@pytest.mark.parametrize("bad", [2, -5, 8.5, True, float("nan")])
def test_invalid_segment_count_rejected_for_heater(bad):
    kwargs = heater_kwargs()
    kwargs["n"] = bad
    with pytest.raises(DomainError, match="segment count"):
        waste_gas_heater(**kwargs)


@pytest.mark.parametrize("bad", [
    float("nan"), float("inf"), float("-inf"), 0., -1.,
])
@pytest.mark.parametrize("field", ["m_co2", "m_gas", "cp_gas", "t_gas_in"])
def test_nonphysical_heater_source_inputs_rejected(field, bad):
    kwargs = heater_kwargs()
    kwargs[field] = bad
    with pytest.raises(DomainError):
        waste_gas_heater(**kwargs)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1.])
def test_nonphysical_minimum_heater_approach_rejected(bad):
    kwargs = heater_kwargs()
    kwargs["min_pinch_k"] = bad
    with pytest.raises(DomainError):
        waste_gas_heater(**kwargs)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1., 0.])
def test_cycle_rejects_invalid_mass_flow_before_property_solving(bad):
    inputs = CycleInputs(
        p1_pa=8e6, p4_pa=24e6, t1_k=310., t4_k=720.,
        mdot_kg_s=bad, eta_compressor=.89, eta_turbine=.90,
        losses=PressureLosses(100e3, 150e3, 100e3, 50e3),
        recuperator_ua_w_k=15000., segments=10,
    )
    with pytest.raises(DomainError, match="finite positive cycle mass flow"):
        solve_cycle(F, inputs)


@pytest.mark.parametrize("x,y", [(float("nan"), 10.), (10., float("inf"))])
def test_lmtd_rejects_nonfinite_approach(x, y):
    with pytest.raises(DomainError, match="nonfinite"):
        _lmtd(x, y)
