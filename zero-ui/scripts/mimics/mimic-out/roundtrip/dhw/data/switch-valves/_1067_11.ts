import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { DHW_TANK_DATA } from "../boiler-tanks";
export default toInstance<MimicComponentType.SwitchValve>({
  custom: {
    get tankController() {
      return DHW_TANK_DATA[MimicComponentType.BoilerTank]["1053"];
    },
  },
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank1Inlet"),
  },
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank1Inlet"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Switch valve",
      componentType: "2 way valve DN 25",
    });
  },
});
