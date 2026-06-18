import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
    controller: getField(ControlComponentType.PIDController, "boilers", "boilersLt1FlowController"),
  },
  custom: {},
  parameters: {
    flow: getField(ParametersType.Flow, "boilers", "lt1FlowcontrolMinimumSetpoint"),
  },
  sensors: {
    flow: getField(SensorComponentType.Flow, "boilers", "boilersFlowLt1"),
    temperature: getField(
      SensorComponentType.Temperature,
      "boilers",
      "boilersTemperatureFreshwaterSupply",
    ),
  },
  tooltip: tooltip({
    yardTag: "1057-24",
    technicalName: "boilers-flow-lt1",
  }),
});
