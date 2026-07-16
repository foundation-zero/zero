import { SensorComponentType } from "@/modules/thrs/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.HVAC>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getField(SensorComponentType.HeatExchanger, "dhw", "dhwHvacExchanger"),
  sensors: {
    incoming: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureAdsorptionReturn"),
    outgoing: getField(SensorComponentType.Temperature, "dhw", "dhwTemperatureHvacExchangerReturn"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "dhw-hvac-exchanger",
  }),
});
