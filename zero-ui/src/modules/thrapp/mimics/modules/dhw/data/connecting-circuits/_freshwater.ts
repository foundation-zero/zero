import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.FreshwaterCircuit>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", { technicalName: "fresh-water" }),
  sensors: {
    flowIn: getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow"),
    tIn: getField(SensorComponentType.Temperature, "dhw", "freshwaterHotwaterTemperature"),
    flowOut: getField(SensorComponentType.CalculatedFlow, "dhw", "dhwFreshwaterFlowSupply"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Fresh water",
      technicalName: "fresh-water",
    });
  },
});
