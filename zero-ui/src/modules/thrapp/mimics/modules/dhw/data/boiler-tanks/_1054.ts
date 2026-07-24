import { ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField, getField } from "../../../../providers";
import { boostingSupply, controller, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank2State",
  },
  controls: {},
  controllerState: {
    controller,
  },
  parameters: {
    ...parameters,
    disabled: getField(ParametersType.Disabled, "dhw", "tank2Disabled"),
  },
  source: getCustomField("dhw", {
    title: "Tank 2",
    yardTag: "1054",
    technicalName: "hot-water-tank-2",
  }),
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank2"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank2"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2Outlet"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
