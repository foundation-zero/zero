import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { setpointName, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowControlValve>({
  controls: {
    valve: getField(ControlComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt1FlowController"),
  },
  custom: {
    controllerName: "LT1_flow_controller",
    setpointName,
  },
  parameters: {},
  sensors: {
    valve: getField(SensorComponentType.Valve, "boilers", "boilersFlowcontrolLt1"),
    measurement: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureLt1Return",
    ),
  },
  tooltip: tooltip({
    yardTag: "1064-08",
    technicalName: "boilers-flowcontrol-lt1",
  }),
});
