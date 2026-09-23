import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import { pumpFlowController } from "../controllers";

export default toInstance<MimicComponentType.HeatPump>({
  controls: {
    heatpump: getField(ControlComponentType.Heatpump, "dhw", "dhwHeatpump"),
  },
  controllerState: {},
  source: getField(SensorComponentType.HeatPump, "dhw", "placeholder"),
  custom: { controller: pumpFlowController },
  parameters: {},
  sensors: {
    heatTransfer: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwHeatpump"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Heat pump",
      componentType: "Heat pump",
    });
  },
});
