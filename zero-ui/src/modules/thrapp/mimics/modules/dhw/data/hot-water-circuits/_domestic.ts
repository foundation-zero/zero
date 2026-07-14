import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: undefined,
  sensors: {
    flowOut: getField(SensorComponentType.CalculatedFlow, "dhw", "dhwFreshwaterFlowSupply"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
    flowIn: getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow"),
    tIn: getField(SensorComponentType.Temperature, "dhw", "freshwaterHotwaterTemperature"),
  },
  tooltip: tooltip({
    title: "Fresh Water",
    technicalName: "Fresh-water",
  }),
});
