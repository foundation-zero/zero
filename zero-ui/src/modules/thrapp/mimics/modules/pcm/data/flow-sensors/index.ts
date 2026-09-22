import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const createFlowSensor = (field: ModuleField<SensorComponentType.Flow>) =>
  toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: field,
    sensors: {},
    get tooltip() {
      return fieldTooltip(field, {
        title: "Flow sensor",
        componentType: "Flow sensor",
      });
    },
  });

export const PCM_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-18": createFlowSensor(getField(SensorComponentType.Flow, "pcm", "pcmFlowModule1")),
    "1057-19": createFlowSensor(getField(SensorComponentType.Flow, "pcm", "pcmFlowModule2")),
    "1057-20": createFlowSensor(getField(SensorComponentType.Flow, "pcm", "pcmFlowModule3")),
    "1057-21": createFlowSensor(getField(SensorComponentType.Flow, "pcm", "pcmFlowModule4")),
    "1058-07": createFlowSensor(
      getField(SensorComponentType.Flow, "consumers", "consumersFlowDhw"),
    ),
    "1058-08": createFlowSensor(
      getField(SensorComponentType.Flow, "consumers", "consumersFlowAdsorption"),
    ),
    "1192": createFlowSensor(
      getField(SensorComponentType.Flow, "consumers", "consumersFlowBypass"),
    ),
  },
});
