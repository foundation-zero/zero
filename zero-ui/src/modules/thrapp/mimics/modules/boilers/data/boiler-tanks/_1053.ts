import { SensorComponentType } from "@/modules/thrs/types";

import { boostingSupply, controller, parameters, toBoilerTank } from ".";
import { getField } from "../../../../providers";

export default toBoilerTank({
  custom: {
    tankStateField: "tank1State",
  },
  controls: {
    controller,
  },
  parameters,
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
