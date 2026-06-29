import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { boostingSupply, controller, parameters } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank2State",
  },
  controls: {},
  controllerState: {
    controller,
  },
  parameters,
  source: undefined,
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank2"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank2"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Outlet"),
  },
  tooltip: {
    title: "Tank 2",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-2",
    yardTag: "1054",
  },
});
