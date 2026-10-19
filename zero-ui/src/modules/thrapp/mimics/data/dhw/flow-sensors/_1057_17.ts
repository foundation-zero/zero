import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFlowSensor } from "../../helpers";

import { getField } from "../../../providers";
import { pump } from "./shared";

export default toFlowSensor({
  controls: {
    pump,
  },
  parameters: {
    flow: getField(ParametersType.FlowControl, "dhw", "dcFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
});
