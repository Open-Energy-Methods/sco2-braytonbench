"""Independent research software for sCO2 Brayton-cycle design and control.

No experimental CARBOSOLA or real-fluid validation claim is made.
"""
from .cycle import CycleInputs, CycleResult, solve_cycle
from .core import PressureLosses
from .properties import CoolPropCO2, DomainError, IdealGasFixture, State
__all__=['CycleInputs','CycleResult','solve_cycle','PressureLosses','CoolPropCO2','DomainError','IdealGasFixture','State']

from .fixed_ua import FixedUAResult, solve_fixed_ua_whr
__all__ += ['FixedUAResult','solve_fixed_ua_whr']

from .streams import LinearCp
from .cooler import CoolerSink, CoolerRating, rate_cooler
from .offdesign import FlowScaling
from .coupled_plant import CoupledPlantResult, solve_coupled_plant
__all__ += ['LinearCp','CoolerSink','CoolerRating','rate_cooler',
            'FlowScaling','CoupledPlantResult','solve_coupled_plant']
