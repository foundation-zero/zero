import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { setpointName, toFlowControlValve, tooltip } from ".";
import { getField } from "../../../../providers";

export default toFlowControlValve({
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
