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
    level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank3"),
    temperature: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureTank3"),
    boostSupplyValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank3BoostingSupply",
    ),
    boostReturnValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank3BoostingReturn",
    ),
    supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Fill"),
    dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank3Empty"),
  },
  tooltip: {
    title: "Tank 3",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-3",
    yardTag: "1055",
  },
});
