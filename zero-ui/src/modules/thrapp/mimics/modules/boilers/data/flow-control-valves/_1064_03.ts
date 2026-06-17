import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { setpointName, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt2FlowController"),
  },
  custom: {
    controllerName: "LT2_flow_controller",
    setpointName,
  },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt2"),
    measurement: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureLt2Return",
    ),
  },
  tooltip: tooltip({
    yardTag: "1064-03",
    technicalName: "boilers-flowcontrol-lt2",
  }),
});
