from typing import (
    Literal,
)
from thrs.orchestration.config import Config

from thrs.control.modules.boilers import (
    BoilersAlarms,
    BoilersControl,
    BoilersControlMode,
    BoilersParameters,
)
from thrs.control.modules.high_temperature import HighTemperatureModule
from thrs.input_output.modules.boilers import (
    BoilersControlValues,
    BoilersSensorValues,
    BoilersSimulationInputs,
    BoilersSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import HighTemperatureSimulationInputs
from thrs.orchestration.module import ModuleDescription, CombinedModule
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
from thrs.input_output.base import (
    Stamped,
)
from thrs.input_output.definitions.simulation import (
    Boundary,
    FlowBoundary,
    HeatSource,
    HvacExchanger,
    OverpressureTemperatureBoundary,
    Pcs,
    TemperatureBoundary,
    Thruster,
)
from thrs.input_output.definitions.units import PcsMode
from thrs.input_output.modules.consumers import (
    ConsumersControlValues,
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmControlValues,
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtControlValues,
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersControlValues,
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.simulation.models.fmu_paths import (
    thrusters_path,
    pvt_path,
    pcm_path,
    consumers_path,
    high_temperature_path,
    boilers_path,
)


SEAWATER_TEMPERATURE = 20.0

INPUTS = {
    "thrusters": ThrustersSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
            heat_flow=Stamped.stamp(4300.0), active=Stamped.stamp(True)
        ),
        thrusters_seawater_supply=Boundary(
            temperature=Stamped.stamp(32.0), flow=Stamped.stamp(64.0)
        ),
        thrusters_module_supply=TemperatureBoundary(temperature=Stamped.stamp(40.0)),
        thrusters_pcs=Pcs(mode=Stamped.stamp(PcsMode.PROPULSION)),
    ),
    "pvt": PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_module_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
    ),
    "pcm": PcmSimulationInputs(
        pcm_producers_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(30)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    ),
    "consumers": ConsumersSimulationInputs(
        consumers_boosting_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_module_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
    "high_temperature": HighTemperatureSimulationInputs(
        thrusters_aft=Thruster(
            heat_flow=Stamped.stamp(9000.0), active=Stamped.stamp(True)
        ),
        thrusters_fwd=Thruster(
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
        consumers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_boosting_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
    ),
    "boilers": BoilersSimulationInputs(
        boilers_lt1_supply=Boundary(
            temperature=Stamped.stamp(50),
            flow=Stamped.stamp(35),
        ),
        boilers_lt2_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        boilers_fahrenheit_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(45),
        ),
        boilers_ht_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        boilers_freshwater_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20),
            overpressure=Stamped.stamp(3),
        ),
        boilers_hvac_exchanger=HvacExchanger(
            heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(36)
        ),
        boilers_seawater_supply=TemperatureBoundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE)
        ),
        boilers_hotwater_demand=FlowBoundary(flow=Stamped.stamp(30)),
    ),
}


CONTROL_PARAMS = {
    "thrusters": ThrustersParameters(),
    "pvt": PvtParameters(),
    "pcm": PcmParameters(),
    "consumers": ConsumersParameters(),
    "boilers": BoilersParameters(),
}

CONTROLS = {
    "thrusters": ThrustersControl,
    "pvt": PvtControl,
    "pcm": PcmControl,
    "consumers": ConsumersControl,
    "boilers": BoilersControl,
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
    BoilersSensorValues,
    BoilersControlValues,
    BoilersParameters,
    BoilersControl,
    BoilersControlMode,
    BoilersAlarms,
)

settings = Config()  # type: ignore

MODES: dict[str, tuple[str, CombinedModule]] = {
    "thrusters": (
        thrusters_path,
        CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            },
            ThrustersSimulationInputs,
            ThrustersSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "pvt": (
        pvt_path,
        CombinedModule(
            {"pvt": PVT_MODULE_DESCRIPTION},
            PvtSimulationInputs,
            PvtSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "pcm": (
        pcm_path,
        CombinedModule(
            {"pcm": PCM_MODULE_DESCRIPTION},
            PcmSimulationInputs,
            PcmSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "consumers": (
        consumers_path,
        CombinedModule(
            {"consumers": CONSUMERS_MODULE_DESCRIPTION},
            ConsumersSimulationInputs,
            ConsumersSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
    "high_temperature": (
        high_temperature_path,
        HighTemperatureModule(control_topic_suffix=settings.mqtt_control_topic_suffix),
    ),
    "boilers": (
        boilers_path,
        CombinedModule(
            {"boilers": BOILERS_MODULE_DESCRIPTION},
            BoilersSimulationInputs,
            BoilersSimulationOutputs,
            control_topic_suffix=settings.mqtt_control_topic_suffix,
        ),
    ),
}

SimulationModes = Literal[
    "thrusters", "pvt", "pcm", "consumers", "high_temperature", "boilers"
]
