import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { pumpFlowController } from "../controllers";
import { fieldTooltip } from "../shared";

export default toInstance<MimicComponentType.HeatPump>({
  controls: {
    heatpump: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
  },
  controllerState: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHeatpump"),
  custom: { controller: pumpFlowController },
  parameters: {},
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
