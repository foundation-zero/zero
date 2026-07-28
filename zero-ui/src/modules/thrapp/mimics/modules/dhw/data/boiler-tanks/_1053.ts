import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField, getField } from "../../../../providers";
import { boostingSupply, controller, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank1State",
  },
  controls: {},
  controllerState: {
    controller,
  },
  parameters: {
    ...parameters,
    disabled: getField(ParametersType.Disabled, "dhw", "tank1Disabled"),
  },
  source: getCustomField("dhw", {
    title: "Tank 1",
    yardTag: "1053",
    technicalName: "hot-water-tank-1",
  }),
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank1"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank1"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Outlet"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
