import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { pumpFlowController } from "../controllers";
export default toInstance<MimicComponentType.HeatPump>({
  custom: {
    controller: pumpFlowController,
  },
  controls: {
    heatpump: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
  },
  controllerState: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureBoostingSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat pump",
      componentType: "Heat pump",
    });
  },
});
