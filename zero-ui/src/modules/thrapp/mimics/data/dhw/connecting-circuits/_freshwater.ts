import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getCustomField, getField } from "../../../providers";

export default toInstance<MimicComponentType.FreshwaterCircuit>({
  controls: {},
  controllerState: {},
  custom: { circuitName: "Fresh water" },
  parameters: {},
  source: getCustomField("dhw", {}),
  sensors: {
    flowIn: getField(SensorComponentType.FlowOnly, "freshWaterHot", "hotFlowFromTank"),
    tIn: getField(SensorComponentType.Temperature, "freshWaterHot", "hotTemperatureFromTank"),
    flowOut: getField(SensorComponentType.CalculatedFlow, "dhw", "dhwFreshwaterFlowSupply"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Connecting Circuit",
    });
  },
});
