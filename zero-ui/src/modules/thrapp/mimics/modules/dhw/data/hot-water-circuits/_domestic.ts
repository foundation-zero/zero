import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
  controls: {},
  custom: {},
  parameters: {},
  source: undefined,
  sensors: {
    flowIn: getField(SensorComponentType.CalculatedFlow, "dhw", "freshwaterFlowSupply"),
    flowOut: getField(SensorComponentType.Flow, "dhw", "freshwaterHotwaterFlow"),
    tIn: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureFreshwaterSupply"),
    tOut: getField(SensorComponentType.Temperature, "dhw", "freshwaterHotwaterTemperature"),
  },
  tooltip: tooltip({
    title: "Fresh Water System",
    technicalName: "domestic-hot-water",
  }),
});
