import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { tank2, tooltip } from "./shared";

export default toInstance<MimicComponentType.SwitchValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply"),
  },
  controllerState: {},
  custom: { tank: tank2 },
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwSwitchTank2BoostingSupply"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1067-10",
    technicalName: "dhw-switch-tank-2-boosting-supply",
  }),
});
