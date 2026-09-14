import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

type PcmTemperatureField =
  | "pcmTemperatureModule1"
  | "pcmTemperatureModule2"
  | "pcmTemperatureModule3"
  | "pcmTemperatureModule4"
  | "pcmTemperatureProducersSupply"
  | "pcmTemperatureProducersReturn";
type ConsumerTemperatureField =
  | "consumersTemperatureDhwSupply"
  | "consumersTemperatureDhwReturn"
  | "consumersTemperatureAdsorptionSupply"
  | "consumersTemperatureAdsorptionReturn";

const createPcmTemperatureSensor = (field: PcmTemperatureField, yardTag: string) =>
  toInstance<MimicComponentType.TemperatureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Temperature, "pcm", field),
    sensors: {
      measurement: getField(SensorComponentType.Temperature, "pcm", field),
    },
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Temperature sensor",
        yardTag,
        componentType: "Temperature sensor",
      });
    },
  });

const createConsumerTemperatureSensor = (field: ConsumerTemperatureField, yardTag: string) =>
  toInstance<MimicComponentType.TemperatureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getField(SensorComponentType.Temperature, "consumers", field),
    sensors: {
      measurement: getField(SensorComponentType.Temperature, "consumers", field),
    },
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Temperature sensor",
        yardTag,
        componentType: "Temperature sensor",
      });
    },
  });

export const PCM_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-60": createPcmTemperatureSensor("pcmTemperatureModule1", "1038-60"),
    "1038-33": createPcmTemperatureSensor("pcmTemperatureModule2", "1038-33"),
    "1038-34": createPcmTemperatureSensor("pcmTemperatureModule3", "1038-34"),
    "1038-35": createPcmTemperatureSensor("pcmTemperatureModule4", "1038-35"),
    "1038-48": createConsumerTemperatureSensor("consumersTemperatureDhwReturn", "1038-48"),
    "1038-49": createConsumerTemperatureSensor("consumersTemperatureAdsorptionReturn", "1038-49"),
    "1038-53": createConsumerTemperatureSensor("consumersTemperatureDhwSupply", "1038-53"),
    "1038-54": createConsumerTemperatureSensor("consumersTemperatureAdsorptionSupply", "1038-54"),
    "1038-31": createPcmTemperatureSensor("pcmTemperatureProducersReturn", "1038-31"),
    "1038-55": createPcmTemperatureSensor("pcmTemperatureProducersSupply", "1038-55"),
  },
});
