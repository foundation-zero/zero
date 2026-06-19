import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { boostingSupply, controller, parameters } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank3State",
  },
  controls: {
    controller,
  },
  parameters,
  source: undefined,
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank3"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank3"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Outlet"),
  },
  tooltip: {
    title: "Tank 3",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-3",
    yardTag: "1055",
  },
});
