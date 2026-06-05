from thrs.control.base import ModuleDescription
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.orchestration.module import CombinedModule


class HighTemperatureModule(
    CombinedModule[HighTemperatureSimulationInputs, HighTemperatureSimulationOutputs]
):
    def __init__(self, control_topic_suffix: str | None = None):
        modules: dict[str, ModuleDescription] = {
            "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            "pvt": PVT_MODULE_DESCRIPTION,
            "pcm": PCM_MODULE_DESCRIPTION,
            "consumers": CONSUMERS_MODULE_DESCRIPTION,
        }

        super().__init__(
            modules,
            HighTemperatureSimulationInputs,
            HighTemperatureSimulationOutputs,
            control_topic_suffix=control_topic_suffix,
        )
