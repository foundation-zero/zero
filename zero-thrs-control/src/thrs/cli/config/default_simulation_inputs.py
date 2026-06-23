from typing import (
    Literal,
)

from thrs.cli.config.modes import SimulationMode
from thrs.control.modules.consumers import (
    ConsumersAlarms,
    ConsumersControl,
    ConsumersControlMode,
    ConsumersParameters,
)
from thrs.control.modules.dhw import (
    DhwAlarms,
    DhwControl,
    DhwControlMode,
    DhwParameters,
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
from thrs.input_output.base import (
    Stamped,
)
from thrs.input_output.definitions.simulation import (
    Boundary,
    HeatSource,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
)
from thrs.input_output.modules.dhw import (
    DhwControlValues,
    DhwSensorValues,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
)
from thrs.orchestration.config import Config
from thrs.orchestration.module import ModuleDescription

SEAWATER_TEMPERATURE = 20.0


SIMULATION_PARAMETER_START_VALUES = {
    SimulationMode.THRUSTER: ThrustersSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(4300.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        thrusters_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(40.0)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    ),
    SimulationMode.PVT: PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
    ),
    # pcm_producers_supply: simulation.Boundary #TODO: make into pcm_pvt_supply
    SimulationMode.PCM: PcmSimulationInputs(
        pcm_thrusters_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(30)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    ),
    SimulationMode.CONSUMERS: ConsumersSimulationInputs(
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_pcm_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
    SimulationMode.HT: HighTemperatureSimulationInputs(
        thrusters_thruster_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_thruster_fwd=Thruster(
            heat_flow=Stamped.stamp(0.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE),
            flow=Stamped.stamp(64.0),
        ),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
    ),
    # TODO Maapater: HACK HACK TODO I needed to be able to compile, but original is not compatible with what I could find
     SimulationMode.DHW: ConsumersSimulationInputs(
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_pcm_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),),

    # TODO: Maapater: Really off Dataclass construct
    # SimulationMode.DHW: DhwSimulationInputs(
    #     dhw_lt1_supply=Boundary(
    #         temperature=Stamped.stamp(50),
    #         flow=Stamped.stamp(35),
    #     ),
    #     dhw_lt2_supply=Boundary(
    #         temperature=Stamped.stamp(60),
    #         flow=Stamped.stamp(60),
    #     ),
    #     dhw_fahrenheit_supply=Boundary(
    #         temperature=Stamped.stamp(40),
    #         flow=Stamped.stamp(45),
    #     ),
    #     dhw_ht_supply=Boundary(
    #         temperature=Stamped.stamp(60),
    #         flow=Stamped.stamp(60),
    #     ),
    #     dhw_freshwater_supply=OverpressureTemperatureBoundary(
    #         temperature=Stamped.stamp(20),
    #         overpressure=Stamped.stamp(3),
    #     ),
    #     dhw_hvac_exchanger=HvacExchanger(
    #         heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(36)
    #     ),
    #     dhw_seawater_supply=TemperatureBoundary(
    #         temperature=Stamped.stamp(SEAWATER_TEMPERATURE)
    #     ),
    #     dhw_hotwater_demand=FlowBoundary(flow=Stamped.stamp(30)),
    # ),

}


CONTROL_PARAMS = {
    "thrusters": ThrustersParameters(),
    "pvt": PvtParameters(),
    "pcm": PcmParameters(),
    "consumers": ConsumersParameters(),
    "dhw": DhwParameters(),
}

CONTROLS = {
    "thrusters": ThrustersControl,
    "pvt": PvtControl,
    "pcm": PcmControl,
    "consumers": ConsumersControl,
    "dhw": DhwControl,
}

THRUSTERS_MODULE_DESCRIPTION = ModuleDescription(
    ThrustersSensorValues,
    ThrustersControlValues,
    ThrustersParameters,
    ThrustersControl,
    ThrustersControlMode,
    ThrustersAlarms,
)

PVT_MODULE_DESCRIPTION = ModuleDescription(
    PvtSensorValues,
    PvtControlValues,
    PvtParameters,
    PvtControl,
    PvtControlMode,
    PvtAlarms,
)

PCM_MODULE_DESCRIPTION = ModuleDescription(
    PcmSensorValues,
    PcmControlValues,
    PcmParameters,
    PcmControl,
    PcmControlMode,
    PcmAlarms,
)
CONSUMERS_MODULE_DESCRIPTION = ModuleDescription(
    ConsumersSensorValues,
    ConsumersControlValues,
    ConsumersParameters,
    ConsumersControl,
    ConsumersControlMode,
    ConsumersAlarms,
)

BOILERS_MODULE_DESCRIPTION = ModuleDescription(
    DhwSensorValues,
    DhwControlValues,
    DhwParameters,
    DhwControl,
    DhwControlMode,
    DhwAlarms,
)

settings = Config()  # type: ignore

# MODES: dict[str, tuple[str, CombinedModule]] = {
#     "thrusters": (
#         thrusters_path,
#         CombinedModule(
#             {
#                 "thrusters": THRUSTERS_MODULE_DESCRIPTION,
#             },
#             ThrustersSimulationInputs,
#             ThrustersSimulationOutputs,
#             control_topic_suffix=settings.mqtt_control_topic_suffix,
#         ),
#     ),
#     "pvt": (
#         pvt_path,
#         CombinedModule(
#             {"pvt": PVT_MODULE_DESCRIPTION},
#             PvtSimulationInputs,
#             PvtSimulationOutputs,
#             control_topic_suffix=settings.mqtt_control_topic_suffix,
#         ),
#     ),
#     "pcm": (
#         pcm_path,
#         CombinedModule(
#             {"pcm": PCM_MODULE_DESCRIPTION},
#             PcmSimulationInputs,
#             PcmSimulationOutputs,
#             control_topic_suffix=settings.mqtt_control_topic_suffix,
#         ),
#     ),
#     "consumers": (
#         consumers_path,
#         CombinedModule(
#             {"consumers": CONSUMERS_MODULE_DESCRIPTION},
#             ConsumersSimulationInputs,
#             ConsumersSimulationOutputs,
#             control_topic_suffix=settings.mqtt_control_topic_suffix,
#         ),
#     ),
#     # "high_temperature": (
#     #     high_temperature_path,
#     #     HighTemperatureModule(control_topic_suffix=settings.mqtt_control_topic_suffix),
#     # ),
#     "dhw": (
#         dhw_path,
#         CombinedModule(
#             {"dhw": DHW_MODULE_DESCRIPTION},
#             DhwSimulationInputs,
#             DhwSimulationOutputs,
#             control_topic_suffix=settings.mqtt_control_topic_suffix,
#         ),
#     ),
# }

SimulationModes = Literal[
    "thrusters", "pvt", "pcm", "consumers", "high_temperature", "dhw"
]
