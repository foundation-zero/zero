import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { dcFlowController } from "../controllers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  },
  controllerState: {},
  custom: {
    controller: dcFlowController,
  },
  parameters: {},
  source: getField(SensorComponentType.Valve, "dhw", "dhwFlowcontrolDc"),
  sensors: {},
  tooltip: tooltip({
    yardTag: "1064-03",
    technicalName: "dhw-flowcontrol-dc",
  }),
});
