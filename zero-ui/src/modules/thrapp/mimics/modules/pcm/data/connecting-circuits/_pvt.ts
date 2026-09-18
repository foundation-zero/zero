import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ConnectingCircuit>({
  controls: {},
  controllerState: {},
  custom: {
    modeModule: "pvt",
  },
  parameters: {},
  source: getCustomField("pvt", { technicalName: "pcm-pvt-loop" }),
  sensors: {
    flowIn: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
    flowOut: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtTotalFlow"),
    tOut: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersSupply"),
    tIn: getField(SensorComponentType.CalculatedTemperature, "pvt", "pvtReturnTemperature"),
  },
  get tooltip() {
    return fieldTooltip(this.source, { title: "PVT", componentType: "PVT loop" });
  },
});
