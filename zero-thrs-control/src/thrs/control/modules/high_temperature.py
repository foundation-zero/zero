from thrs.control.modules.consumers import (
    ConsumersAlarms,
    ConsumersControl,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.control.modules.pcm import (
    PcmAlarms,
    PcmControl,
    PcmControlMode,
    PcmParameters,
)
from thrs.control.modules.pvt import (
    PvtAlarms,
    PvtControl,
    PvtControlMode,
    PvtParameters,
)
from thrs.control.modules.thrusters import (
    ThrustersAlarms,
    ThrustersControl,
    ThrustersControlMode,
    ThrustersParameters,
)
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmControlValues, PcmSensorValues
from thrs.input_output.modules.pvt import PvtControlValues, PvtSensorValues
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
)
from thrs.orchestration.module import CombinedModule, ModuleDescription


class HighTemperatureModule(
    CombinedModule[HighTemperatureSimulationInputs, HighTemperatureSimulationOutputs]
):
    def __init__(self, control_topic_suffix: str | None = None):
        super().__init__(
            {
                "thrusters": ModuleDescription(
                    ThrustersSensorValues,
                    ThrustersControlValues,
                    ThrustersParameters,
                    ThrustersControl,
                    ThrustersControlMode,
                    ThrustersAlarms,
                ),
                "pvt": ModuleDescription(
                    PvtSensorValues,
                    PvtControlValues,
                    PvtParameters,
                    PvtControl,
                    PvtControlMode,
                    PvtAlarms,
                ),
                "pcm": ModuleDescription(
                    PcmSensorValues,
                    PcmControlValues,
                    PcmParameters,
                    PcmControl,
                    PcmControlMode,
                    PcmAlarms,
                ),
                "consumers": ModuleDescription(
                    ConsumersSensorValues,
                    ConsumersControlValues,
                    ConsumersParameters,
                    ConsumersControl,
                    ConsumersControlMode,
                    ConsumersAlarms,
                ),
            },
            HighTemperatureSimulationInputs,
            HighTemperatureSimulationOutputs,
            control_topic_suffix=control_topic_suffix,
        )
