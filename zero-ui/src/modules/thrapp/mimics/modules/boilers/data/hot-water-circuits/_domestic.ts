import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HotWaterCircuit>({
  controls: {},
  custom: {},
  parameters: {},
  sensors: {
    flowIn: getField(SensorComponentType.CalculatedFlow, "boilers", "freshwaterFlowSupply"),
    flowOut: getField(SensorComponentType.Flow, "boilers", "freshwaterHotwaterFlow"),
    tIn: getField(SensorComponentType.Temperature, "boilers", "boilersTemperatureFreshwaterSupply"),
    tOut: getField(SensorComponentType.Temperature, "boilers", "freshwaterHotwaterTemperature"),
  },
  tooltip: tooltip({
    title: "Domestic Hot Water",
    technicalName: "domestic-hot-water",
  }),
});
