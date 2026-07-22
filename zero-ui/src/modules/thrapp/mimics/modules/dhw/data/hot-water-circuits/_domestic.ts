import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", "Fresh-water"),
  sensors: {
    flowOut: getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "freshwaterHotwaterTemperature"),
    flowIn: getField(SensorComponentType.CalculatedFlow, "dhw", "dhwFreshwaterFlowSupply"),
    tIn: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
  },
  tooltip: tooltip({
    title: "Fresh water",
    technicalName: "fresh-water",
  }),
});
