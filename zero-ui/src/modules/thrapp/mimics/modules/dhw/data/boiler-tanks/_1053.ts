import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { boostingSupply, controller, parameters } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank1State",
  },
  controls: {},
  controllerState: {
    controller,
  },
  parameters,
  source: undefined,
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank1"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Outlet"),
  },
  tooltip: {
    title: "Tank 1",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-1",
    yardTag: "1053",
  },
});
