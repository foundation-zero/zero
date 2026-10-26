import { ParametersType, SensorComponentType } from "@/modules/thrsim/types";
import { toFlowSensor } from "../../helpers";

import { getField } from "../../../providers";
import { pump } from "./shared";

export default toFlowSensor({
  controls: {
    pump,
  },
  parameters: {
    flow: getField(ParametersType.FlowControl, "dhw", "drivesFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
});
