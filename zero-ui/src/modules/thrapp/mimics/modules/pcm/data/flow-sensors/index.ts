import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type PcmFlowField = "pcmFlowModule1" | "pcmFlowModule2" | "pcmFlowModule3" | "pcmFlowModule4";
type PcmTemperatureField =
  | "pcmTemperatureModule1"
  | "pcmTemperatureModule2"
  | "pcmTemperatureModule3"
  | "pcmTemperatureModule4";
type ConsumerFlowField = "consumersFlowDhw" | "consumersFlowBypass";
type ConsumerTemperatureField = "consumersTemperatureDhwSupply" | "consumersTemperatureDhwReturn";

const createFlowSensor = (
  field: PcmFlowField,
  temperatureField: PcmTemperatureField,
  yardTag: string,
) =>
  toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Flow, "pcm", field),
    sensors: {
      temperature: getField(SensorComponentType.Temperature, "pcm", temperatureField),
    },
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Flow sensor",
        yardTag,
        componentType: "Flow sensor",
      });
    },
  });

const createConsumerFlowSensor = (
  field: ConsumerFlowField,
  temperatureField: ConsumerTemperatureField,
  yardTag: string,
) =>
  toInstance<MimicComponentType.FlowSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Flow, "consumers", field),
    sensors: {
      temperature: getField(SensorComponentType.Temperature, "consumers", temperatureField),
    },
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Flow sensor",
        yardTag,
        componentType: "Flow sensor",
      });
    },
  });

export const PCM_FLOW_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.FlowSensor]: {
    "1057-18": createFlowSensor("pcmFlowModule1", "pcmTemperatureModule1", "1057-18"),
    "1057-19": createFlowSensor("pcmFlowModule2", "pcmTemperatureModule2", "1057-19"),
    "1057-20": createFlowSensor("pcmFlowModule3", "pcmTemperatureModule3", "1057-20"),
    "1057-21": createFlowSensor("pcmFlowModule4", "pcmTemperatureModule4", "1057-21"),
    "1058-07-1": createConsumerFlowSensor(
      "consumersFlowDhw",
      "consumersTemperatureDhwSupply",
      "1058-07",
    ),
    "1058-07-2": createConsumerFlowSensor(
      "consumersFlowDhw",
      "consumersTemperatureDhwSupply",
      "1058-07",
    ),
    "1192": createConsumerFlowSensor(
      "consumersFlowBypass",
      "consumersTemperatureDhwReturn",
      "1192",
    ),
  },
});
