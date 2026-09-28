import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import {
  ControlComponentType,
  PickKeys,
  SchemaDefinition,
  SensorComponentType,
} from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const createPcmFlowControlValve = (
  field: PickKeys<
    ThrsDefinitions["pcm"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Valve>
  >,
) =>
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
        componentType: "Flow control valve",
      });
    },
  });

const createConsumersFlowControlValve = (
  field: PickKeys<
    ThrsDefinitions["consumers"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Valve>
  >,
) =>
  toInstance<MimicComponentType.FlowControlValve>({
    controls: {
      valve: getField(ControlComponentType.Valve, "consumers", field),
    },
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Valve, "consumers", field),
    sensors: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Flow control valve",
        componentType: "Flow control valve",
      });
    },
  });

export const PCM_FLOW_CONTROL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.FlowControlValve]: {
    "1064-04": createPcmFlowControlValve("pcmFlowcontrolModule1"),
    "1064-05": createPcmFlowControlValve("pcmFlowcontrolModule2"),
    "1064-06": createPcmFlowControlValve("pcmFlowcontrolModule3"),
    "1064-07": createPcmFlowControlValve("pcmFlowcontrolModule4"),
    "1065-01": createConsumersFlowControlValve("consumersFlowcontrolDhw"),
    "1061": createConsumersFlowControlValve("consumersFlowcontrolAdsorption"),
    "1062-01": createConsumersFlowControlValve("consumersFlowcontrolBypass"),
  },
});
