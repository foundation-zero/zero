from dataclasses import dataclass
from typing import Literal

from thrs.control.modules.adsorption import ADSORPTION_MODULE_DESCRIPTION
from thrs.control.modules.consumers import CONSUMERS_MODULE_DESCRIPTION
from thrs.control.modules.dc import DC_MODULE_DESCRIPTION
from thrs.control.modules.dhw import DHW_MODULE_DESCRIPTION
from thrs.control.modules.drives import DRIVES_MODULE_DESCRIPTION
from thrs.control.modules.pcm import PCM_MODULE_DESCRIPTION
from thrs.control.modules.pvt import PVT_MODULE_DESCRIPTION
from thrs.control.modules.thrusters import THRUSTERS_MODULE_DESCRIPTION
from thrs.input_output.base import Stamped
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
from thrs.input_output.modules.adsorption import AdsorptionSimulationOutputs
from thrs.input_output.modules.consumers import (
    ConsumersSimulationInputs,
    ConsumersSimulationOutputs,
)
from thrs.input_output.modules.dc import DcSimulationOutputs
from thrs.input_output.modules.dhw import DhwSimulationInputs, DhwSimulationOutputs
from thrs.input_output.modules.drives import DrivesSimulationOutputs
from thrs.input_output.modules.high_temperature import (
    HighTemperatureSimulationInputs,
    HighTemperatureSimulationOutputs,
)
from thrs.input_output.modules.pcm import PcmSimulationInputs, PcmSimulationOutputs
from thrs.input_output.modules.pvt import PvtSimulationInputs, PvtSimulationOutputs
from thrs.input_output.modules.thrusters import (
    ThrustersSimulationInputs,
    ThrustersSimulationOutputs,
)
from thrs.orchestration.module import ModuleDescription
from thrs.orchestration.simulation import SimulationDescription
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
            temperature=Stamped.stamp(70), flow=Stamped.stamp(40)
        ),
        pcm_pvt_supply=Boundary(temperature=Stamped.stamp(70), flow=Stamped.stamp(50)),
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
        dhw_consumers_supply=Boundary(
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
    "adsorption": None,  # TODO Fill in  # type: ignore
    "drives": None,  # TODO Fill in  # type: ignore
    "dc": None,  # TODO Fill in  # type: ignore
}


type ModeName = Literal[
    "thrusters",
    "pvt",
    "pcm",
    "consumers",
    "adsorption",
    "drives",
    "dc",
    "high_temperature",
    "dhw",
    "thrs",
]


@dataclass
class Mode:
    name: ModeName
    control_modules: dict[str, ModuleDescription]
    simulation_description: SimulationDescription | None


def lookup_mode(mode_name: ModeName) -> Mode:
    return next((m for m in MODES if m.name == mode_name))


MODES: list[Mode] = [
    Mode(
        name="thrusters",
        control_modules={"thrusters": THRUSTERS_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            ThrustersSimulationOutputs,
            Fmu(thrusters_path),
            SIMULATION_INPUTS["thrusters"],
        ),
    ),
    Mode(
        name="pvt",
        control_modules={"pvt": PVT_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            PvtSimulationOutputs,
            Fmu(pvt_path),
            SIMULATION_INPUTS["pvt"],
        ),
    ),
    Mode(
        name="pcm",
        control_modules={"pcm": PCM_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            PcmSimulationOutputs,
            Fmu(pcm_path),
            SIMULATION_INPUTS["pcm"],
        ),
    ),
    Mode(
        name="consumers",
        control_modules={"consumers": CONSUMERS_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            ConsumersSimulationOutputs,
            Fmu(consumers_path),
            SIMULATION_INPUTS["consumers"],
        ),
    ),
    Mode(
        name="adsorption",
        control_modules={"adsorption": ADSORPTION_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            AdsorptionSimulationOutputs,
            Fmu(adsorption_path),
            SIMULATION_INPUTS["adsorption"],
        ),
    ),
    Mode(
        name="drives",
        control_modules={"drives": DRIVES_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            DrivesSimulationOutputs,
            Fmu(drives_path),
            SIMULATION_INPUTS["drives"],
        ),
    ),
    Mode(
        name="dc",
        control_modules={"dc": DC_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            DcSimulationOutputs,
            Fmu(dc_path),
            SIMULATION_INPUTS["dc"],
        ),
    ),
    Mode(
        name="dhw",
        control_modules={"dhw": DHW_MODULE_DESCRIPTION},
        simulation_description=SimulationDescription(
            DhwSimulationOutputs,
            Fmu(dhw_path),
            SIMULATION_INPUTS["dhw"],
        ),
    ),
    Mode(
        name="high_temperature",
        control_modules={
            "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            "pvt": PVT_MODULE_DESCRIPTION,
            "pcm": PCM_MODULE_DESCRIPTION,
            "consumers": CONSUMERS_MODULE_DESCRIPTION,
        },
        simulation_description=SimulationDescription(
            HighTemperatureSimulationOutputs,
            Fmu(high_temperature_path),
            SIMULATION_INPUTS["high_temperature"],
        ),
    ),
    Mode(
        name="thrs",
        control_modules={
            "thrusters": THRUSTERS_MODULE_DESCRIPTION,
            "pvt": PVT_MODULE_DESCRIPTION,
            "pcm": PCM_MODULE_DESCRIPTION,
            "consumers": CONSUMERS_MODULE_DESCRIPTION,
            "adsorption": ADSORPTION_MODULE_DESCRIPTION,
            "drives": DRIVES_MODULE_DESCRIPTION,
            "dc": DC_MODULE_DESCRIPTION,
            "dhw": DHW_MODULE_DESCRIPTION,
        },
        simulation_description=None,
    ),
]
