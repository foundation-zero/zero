import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.HVAC>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHvacExchanger"),
  sensors: {
    flow: getField(SensorComponentType.Flow, "dhw", "dhwFlowDc"),
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "HVAC",
      componentType: "HVAC Exchanger",
    });
  },
});
