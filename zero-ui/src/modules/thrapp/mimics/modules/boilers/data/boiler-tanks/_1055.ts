import { SensorComponentType } from "@/modules/thrs/types";

import { boostingSupply, controller, parameters, toBoilerTank } from ".";
import { getField } from "../../../../providers";

export default toBoilerTank({
  custom: {
    tankStateField: "tank3State",
  },
  controls: {
    controller,
  },
  parameters,
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
