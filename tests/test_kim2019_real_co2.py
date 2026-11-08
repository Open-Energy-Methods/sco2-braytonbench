"""Real-CoolProp CO2 transport quadrature sensitivity.

It is a small thermophysical numerical check, not a Stuttgart
experimental-validation test. Requires pinned CoolProp in CI.
"""
import pytest
pytest.importorskip("CoolProp")
from sco2_braytonbench.kim2019 import CoolPropCO2Transport,integral_means

@pytest.mark.parametrize("p,tb,tw",[
    (7.75e6,303.,309.),
    (7.75e6,307.,325.),
    (7.75e6,315.,350.),
    (8.50e6,310.,360.),
])
def test_integrated_transport_refines_at_pseudocritical_states(p,tb,tw):
    props=CoolPropCO2Transport()
    coarse=integral_means(props,p,tb,tw,steps_per_8k=1,max_subintervals=48)
    fine=integral_means(props,p,tb,tw,steps_per_8k=2,max_subintervals=96)
    assert fine[-1]>=coarse[-1]
    for key in range(4):
        assert abs(fine[key]-coarse[key])/max(abs(fine[key]),1e-12)<.03
    # Isobaric cp mean derived from h(Tw)-h(Tb), independent of quadrature.
    assert fine[3]==pytest.approx(coarse[3],rel=1e-13)
