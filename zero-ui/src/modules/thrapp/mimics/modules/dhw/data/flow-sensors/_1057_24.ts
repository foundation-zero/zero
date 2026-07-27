import { ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { pump, tooltip } from "./shared";

export default toInstance<MimicComponentType.FlowSensor>({
  controls: {
    pump,
  },
  controllerState: {},
  custom: {},
  parameters: {
    flow: getField(ParametersType.FlowControl, "dhw", "drivesFlowcontrolMinimumSetpoint"),
  },
  source: getField(SensorComponentType.Flow, "dhw", "dhwFlowDrives"),
  sensors: {
    temperature: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  get tooltip() {
    return tooltip(this.source);
  },
});
