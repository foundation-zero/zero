import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";

import { setpointName, toFlowControlValve, tooltip } from ".";
import { getField } from "../../../../providers";

export default toFlowControlValve({
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
