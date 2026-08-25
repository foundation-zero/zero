import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getField, getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.FreshwaterCircuit>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("dhw", {
      technicalName: "fresh-water",
    }),
  sensors: {
    flowIn: getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow"),
    flowOut: getField(SensorComponentType.CalculatedFlow, "dhw", "dhwFreshwaterFlowSupply"),
    tIn: getField(SensorComponentType.Temperature, "dhw", "freshwaterHotwaterTemperature"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Fresh water",
      technicalName: "fresh-water",
    });
  },
});
