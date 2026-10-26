import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

export default toInstance<MimicComponentType.HVAC>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwHvacExchanger"),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "HVAC",
      componentType: "HVAC Exchanger",
    });
  },
});
