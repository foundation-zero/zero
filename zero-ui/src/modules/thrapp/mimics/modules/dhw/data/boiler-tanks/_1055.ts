import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField, getField } from "../../../../providers";
import { boostingSupply, controller, parameters, tooltip } from "./shared";

export default toInstance<MimicComponentType.BoilerTank>({
  custom: {
    tankStateField: "tank3State",
  },
  controls: {},
  controllerState: {
    controller,
  },
  parameters: {
    ...parameters,
    disabled: getField(ParametersType.Disabled, "dhw", "tank3Disabled"),
  },
  source: getCustomField("dhw", {
    title: "Tank 3",
    yardTag: "1055",
    technicalName: "hot-water-tank-3",
  }),
  sensors: {
    boostingSupply,
    level: getField(SensorComponentType.Level, "dhw", "dhwLevelTank3"),
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureTank3"),
    boostSupplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingSupply"),
    boostReturnValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3BoostingReturn"),
    supplyValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Inlet"),
    dischargeValve: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Outlet"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
