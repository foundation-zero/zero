from dataclasses import dataclass
from typing import Dict

from src.thrs.cli.config.default_simulation_inputs import (
    SIMULATION_PARAMETER_START_VALUES,
)
from src.thrs.control.base import ModuleDescription
from src.thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from src.thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from src.thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from src.thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from src.thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from src.thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.cli.config.modes import ControlMode, SimulationMode
from thrs.input_output.base import ThrsValues
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationOutputs,
)
from thrs.simulation.models import fmu_paths


@dataclass
class ModuleDefinition:
    topic_base: str


@dataclass
class SimulationModuleDefinition(ModuleDefinition):
    input_values: ThrsValues
    output_values_type: type[ThrsValues]
    control_values: type[ThrsValues]
    sensor_values_type: type[ThrsValues]
    fmu_path: str


@dataclass
class ControlModuleDefinition(ModuleDefinition):
    module_description: ModuleDescription


control_module_definitions: Dict[ControlMode, ControlModuleDefinition] = {
    ControlMode.ADSORPTION: ControlModuleDefinition(
        module_description=ADSORPTION_MODULE_DESCRIPTION,
        topic_base="/thrs/control/adsorption/",
    ),
    ControlMode.CONSUMERS: ControlModuleDefinition(
        module_description=CONSUMERS_MODULE_DESCRIPTION,
        topic_base="/thrs/control/consumers/",
    ),
    ControlMode.PCM: ControlModuleDefinition(
        module_description=PCM_MODULE_DESCRIPTION, topic_base="/thrs/control/pcm/"
    ),
    ControlMode.PVT: ControlModuleDefinition(
        module_description=PVT_MODULE_DESCRIPTION, topic_base="/thrs/control/pvt/"
    ),
    ControlMode.DHW: ControlModuleDefinition(
        module_description=DHW_MODULE_DESCRIPTION, topic_base="/thrs/control/dhw/"
    ),
    ControlMode.THRUSTER: ControlModuleDefinition(
        module_description=THRUSTERS_MODULE_DESCRIPTION,
        topic_base="/thrs/control/thrusters/",
    ),
    # TODO Maapater: Unused?
    # ControlMode.CONVERTERS: ControlModuleDefinition(CONVERTERS_MODULE_DESCRIPTION),
    # ControlMode.DC: ControlModuleDefinition(DC_MODULE_DESCRIPTION),
    # ControlMode.DRIVERS: ControlModuleDefinition(DRIVERS_MODULE_DESCRIPTION),
    # ControlMode.PVT_GROUP: ControlModuleDefinition(PVT_GROUP_MODULE_DESCRIPTION),
}


simulation_module_definitions: Dict[SimulationMode, SimulationModuleDefinition] = {
    # Used?
    SimulationMode.CONSUMERS: SimulationModuleDefinition(
        "/thrs/simulation/consumers/",
        SIMULATION_PARAMETER_START_VALUES[SimulationMode.CONSUMERS],
        ConsumersSimulationOutputs,
        ConsumersControlValues,
        ConsumersSensorValues,
        fmu_paths.consumers_path,
    ),
    SimulationMode.DHW: SimulationModuleDefinition(
        "/thrs/simulation/dhw/",
        SIMULATION_PARAMETER_START_VALUES[SimulationMode.DHW],
        DhwSimulationOutputs,
        DhwControlValues,
        DhwSensorValues,
        fmu_paths.dhw_path,
    ),
    # SimulationMode.HT: SimulationModuleDefinition(
    # topic_base="/thrs/simulation/ht/",
    #     SIMULATION_PARAMETER_START_VALUES[SimulationMode.HT],
    #     HighTemperatureSimulationOutputs,
    #     HighTemperatureControlValues, # TODO Maapater: Where are these defined? Do we need them?
    #     HighTemperatureSensorValues, # TODO Maapater: Where are these defined? Do we need them?
    #     fmu_paths.high_temperature_path,
    # ),
    SimulationMode.PCM: SimulationModuleDefinition(
        "/thrs/simulation/pcm/",
        SIMULATION_PARAMETER_START_VALUES[SimulationMode.PCM],
        PcmSimulationOutputs,
        PcmControlValues,
        PcmSensorValues,
        fmu_paths.pcm_path,
    ),
    SimulationMode.PVT: SimulationModuleDefinition(
        "/thrs/simulation/pvt/",
        SIMULATION_PARAMETER_START_VALUES[SimulationMode.PVT],
        PvtSimulationOutputs,
        PvtControlValues,
        PvtSensorValues,
        fmu_paths.pvt_path,
    ),
    SimulationMode.THRUSTER: SimulationModuleDefinition(
        "/thrs/simulation/thrusters/",
        SIMULATION_PARAMETER_START_VALUES[SimulationMode.THRUSTER],
        ThrustersSimulationOutputs,
        ThrustersControlValues,
        ThrustersSensorValues,
        fmu_paths.thrusters_path,
    ),
    # # TODO Maapater Unused?
    # SimulationMode.ADSORPTION: SimulationModuleDefinition(
    #     [],
    #     [],
    #     fmu_paths.adsorption_path,
    #     "/../../",  # settings.mqtt_control_topic_suffix?
    # ),
    # SimulationMode.DC: SimulationModuleDefinition(
    #     [],
    #     [],
    #     fmu_paths.dc_path,
    #     "/../../",  # settings.mqtt_control_topic_suffix?
    # ),
    # SimulationMode.DRIVERS: SimulationModuleDefinition(
    #     [],
    #     [],
    #     fmu_paths.drives_path,
    #     "/../../",  # settings.mqtt_control_topic_suffix?
    # ),
}
