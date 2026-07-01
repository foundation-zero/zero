from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import (
    Callable,
    Literal,
)

from thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
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
from thrs.input_output.modules.adsorption import (
    AdsorptionSensorValues,
    AdsorptionSimulationOutputs,
)
from thrs.input_output.modules.consumers import (
    ConsumersSensorValues,
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dc import (
    DcSensorValues,
    DcSimulationOutputs,
)
from thrs.input_output.modules.dhw import (
    DhwSensorValues,
    DhwSimulationInputs,
    DhwSimulationOutputs,
)
from thrs.input_output.modules.drives import (
    DrivesSensorValues,
    DrivesSimulationOutputs,
)
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import (
    PcmSensorValues,
    PcmSimulationInputs,
    PcmSimulationOutputs,
)
from thrs.input_output.modules.pvt import (
    PvtSensorValues,
    PvtSimulationInputs,
    PvtSimulationOutputs,
)
from thrs.input_output.modules.thrusters import (
    ThrustersSensorValues,
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.module import CombinedModule
from thrs.orchestration.simulation import Simulation
from thrs.simulation.fmu import Fmu
from thrs.simulation.models.fmu_paths import (
    adsorption_path,
    consumers_path,
    dc_path,
    dhw_path,
    drives_path,
    high_temperature_path,
    pcm_path,
    pvt_path,
    thrusters_path,
)

SEAWATER_TEMPERATURE = 20.0

SIMULATION_INPUTS = {
    "thrusters": ThrustersSimulationInputs(
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
    "pvt": PvtSimulationInputs(
        pvt_main_fwd=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_main_aft=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_owners=HeatSource(heat_flow=Stamped.stamp(0)),
        pvt_pcm_supply=TemperatureBoundary(temperature=Stamped.stamp(50)),
        pvt_seawater_supply=Boundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE), flow=Stamped.stamp(50)
        ),
    ),
    "pcm": PcmSimulationInputs(
        pcm_thrusters_supply=Boundary(
            temperature=Stamped.stamp(70), flow=Stamped.stamp(80)
        ),
        pcm_consumers_supply=TemperatureBoundary(temperature=Stamped.stamp(30)),
        pcm_freshwater_supply=Boundary(
            temperature=Stamped.stamp(40), flow=Stamped.stamp(0)
        ),
    ),
    "consumers": ConsumersSimulationInputs(
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(10.0),
        ),
        consumers_pcm_supply=Boundary(
            temperature=Stamped.stamp(60.0), flow=Stamped.stamp(10.0)
        ),
    ),
    "high_temperature": HighTemperatureSimulationInputs(
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
        consumers_adsorption_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
        consumers_dhw_supply=Boundary(
            temperature=Stamped.stamp(30.0),
            flow=Stamped.stamp(0.0),
        ),
    ),
    "dhw": DhwSimulationInputs(
        dhw_drives_supply=Boundary(
            temperature=Stamped.stamp(50),
            flow=Stamped.stamp(35),
        ),
        dhw_dc_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_adsorption_supply=Boundary(
            temperature=Stamped.stamp(40),
            flow=Stamped.stamp(45),
        ),
        dhw_ht_supply=Boundary(
            temperature=Stamped.stamp(60),
            flow=Stamped.stamp(60),
        ),
        dhw_freshwater_supply=OverpressureTemperatureBoundary(
            temperature=Stamped.stamp(20),
            overpressure=Stamped.stamp(3),
        ),
        dhw_hvac_exchanger=HvacExchanger(
            heat_flow=Stamped.stamp(300), maximum_temperature=Stamped.stamp(36)
        ),
        dhw_seawater_supply=TemperatureBoundary(
            temperature=Stamped.stamp(SEAWATER_TEMPERATURE)
        ),
        dhw_hotwater_demand=FlowBoundary(flow=Stamped.stamp(30)),
    ),
}


type Modes = Literal[
    "thrusters",
    "pvt",
    "pcm",
    "consumers",
    "adsorption",
    "drives",
    "dc",
    "high_temperature",
    "dhw",
    "boat",
]


@dataclass
class Mode:
    name: Modes
    control_module: CombinedModule
    setup_simulation: Callable[[], Simulation | None]


MODES: list[Mode] = [
    Mode(
        name="thrusters",
        control_module=CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            },
        ),
        setup_simulation=lambda: Simulation(
            {"thrusters": ThrustersSensorValues},
            ThrustersSimulationOutputs,
            Fmu(thrusters_path),
            SIMULATION_INPUTS["thrusters"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="pvt",
        control_module=CombinedModule(
            {"pvt": PVT_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"pvt": PvtSensorValues},
            PvtSimulationOutputs,
            Fmu(pvt_path),
            SIMULATION_INPUTS["pvt"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="pcm",
        control_module=CombinedModule(
            {"pcm": PCM_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"pcm": PcmSensorValues},
            PcmSimulationOutputs,
            Fmu(pcm_path),
            SIMULATION_INPUTS["pcm"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="consumers",
        control_module=CombinedModule(
            {"consumers": CONSUMERS_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"consumers": ConsumersSensorValues},
            ConsumersSimulationOutputs,
            Fmu(consumers_path),
            SIMULATION_INPUTS["consumers"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="adsorption",
        control_module=CombinedModule(
            {"adsorption": ADSORPTION_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"adsorption": AdsorptionSensorValues},
            AdsorptionSimulationOutputs,
            Fmu(adsorption_path),
            SIMULATION_INPUTS["adsorption"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="drives",
        control_module=CombinedModule(
            {"drives": DRIVES_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"drives": DrivesSensorValues},
            DrivesSimulationOutputs,
            Fmu(drives_path),
            SIMULATION_INPUTS["drives"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="dc",
        control_module=CombinedModule(
            {"dc": DC_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"dc": DcSensorValues},
            DcSimulationOutputs,
            Fmu(dc_path),
            SIMULATION_INPUTS["dc"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="dhw",
        control_module=CombinedModule(
            {"dhw": DHW_MODULE_DESCRIPTION},
        ),
        setup_simulation=lambda: Simulation(
            {"dhw": DhwSensorValues},
            DhwSimulationOutputs,
            Fmu(dhw_path),
            SIMULATION_INPUTS["dhw"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="high_temperature",
        control_module=CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
                "pvt": PVT_MODULE_DESCRIPTION,
                "pcm": PCM_MODULE_DESCRIPTION,
                "consumers": CONSUMERS_MODULE_DESCRIPTION,
            },
        ),
        setup_simulation=lambda: Simulation(
            {"high_temperature": HighTemperatureSimulationInputs},
            HighTemperatureSimulationOutputs,
            Fmu(high_temperature_path),
            SIMULATION_INPUTS["high_temperature"],
            datetime.now(),
            timedelta(seconds=1),
        ),
    ),
    Mode(
        name="boat",
        control_module=CombinedModule(
            {
                "thrusters": THRUSTERS_MODULE_DESCRIPTION,
                "pvt": PVT_MODULE_DESCRIPTION,
                "pcm": PCM_MODULE_DESCRIPTION,
                "consumers": CONSUMERS_MODULE_DESCRIPTION,
                "adsorption": ADSORPTION_MODULE_DESCRIPTION,
                "drives": DRIVES_MODULE_DESCRIPTION,
                "dc": DC_MODULE_DESCRIPTION,
                "dhw": DHW_MODULE_DESCRIPTION,
            }
        ),
        setup_simulation=lambda: None,
    ),
]
