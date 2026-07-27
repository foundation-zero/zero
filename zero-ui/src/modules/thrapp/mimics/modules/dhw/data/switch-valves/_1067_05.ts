import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank3, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank3Outlet"),
  },
  controllerState: {},
  custom: tank3,
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank3Outlet"),
  sensors: {},
  get tooltip() {
    return tooltip(this.source);
  },
});
