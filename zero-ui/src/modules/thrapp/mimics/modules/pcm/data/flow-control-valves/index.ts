import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type PcmFlowControlField =
  | "pcmFlowcontrolModule1"
  | "pcmFlowcontrolModule2"
  | "pcmFlowcontrolModule3"
  | "pcmFlowcontrolModule4"
  | "placeholder";

const createFlowControlValve = (field: PcmFlowControlField, yardTag: string) =>
  toInstance<MimicComponentType.FlowControlValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "pcm", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Valve, "pcm", field),
    sensors: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Flow control valve",
        yardTag,
        componentType: "Flow control valve",
      });
    },
  });

export const PCM_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1064-04": createFlowControlValve("pcmFlowcontrolModule1", "1064-04"),
    "1064-05": createFlowControlValve("pcmFlowcontrolModule2", "1064-05"),
    "1064-06": createFlowControlValve("pcmFlowcontrolModule3", "1064-06"),
    "1064-07": createFlowControlValve("pcmFlowcontrolModule4", "1064-07"),
    "1065-01": createFlowControlValve("placeholder", "1065-01"),
    "1061": createFlowControlValve("placeholder", "1061"),
    "1062-01": createFlowControlValve("placeholder", "1062-01"),
  },
});
