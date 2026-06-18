import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { boostingSupply, controller, parameters } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank1State",
  },
  controls: {
    controller,
  },
  parameters,
  source: undefined,
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank1"),
    temperature: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureTank1"),
    boostSupplyValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank1BoostingSupply",
    ),
    boostReturnValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank1BoostingReturn",
    ),
    supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Fill"),
    dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank1Empty"),
  },
  tooltip: {
    title: "Tank 1",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-1",
    yardTag: "1053",
  },
});
