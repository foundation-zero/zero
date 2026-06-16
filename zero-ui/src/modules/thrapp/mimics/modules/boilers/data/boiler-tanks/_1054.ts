import { SensorComponentType } from "@/modules/thrs/types";

import { boostingSupply, controller, parameters, toBoilerTank } from ".";
import { getField } from "../../../../providers";

export default toBoilerTank({
  custom: {
    tankStateField: "tank2State",
  },
  controls: {
    controller,
  },
  parameters,
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "boilers", "boilersLevelTank2"),
    temperature: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureTank2"),
    boostSupplyValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank2BoostingSupply",
    ),
    boostReturnValve: getField(
      SensorComponentType.Valve,
      "boilers",
      "boilersSwitchTank2BoostingReturn",
    ),
    supplyValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Fill"),
    dischargeValve: getField(SensorComponentType.Valve, "boilers", "boilersSwitchTank2Empty"),
  },
  tooltip: {
    title: "Tank 2",
    itemName: "Hot water tank",
    technicalName: "hot-water-tank-2",
    yardTag: "1054",
  },
});
