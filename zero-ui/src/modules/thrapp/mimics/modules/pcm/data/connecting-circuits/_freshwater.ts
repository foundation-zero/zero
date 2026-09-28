import { SensorComponentType } from "@/modules/thrsim/types";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getCustomField, getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.ConnectingCircuit>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", { technicalName: "fresh-water" }),
  sensors: {
    flowIn: getField(SensorComponentType.Flow, "pcm", "freshwaterFlowPcm"),
    tIn: getField(SensorComponentType.Temperature, "pcm", "freshwaterTemperaturePcmReturn"),
    flowOut: getField(SensorComponentType.Flow, "pcm", "freshwaterFlowPcm"),
    tOut: getField(SensorComponentType.Temperature, "pcm", "freshwaterTemperaturePcmSupply"),
  },
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Fresh water",
    });
  },
});
