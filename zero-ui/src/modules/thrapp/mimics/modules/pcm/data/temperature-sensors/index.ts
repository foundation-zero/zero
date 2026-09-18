import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ThrsDefinitions } from "@/modules/thrsim/lib/consts";
import { PickKeys, SchemaDefinition, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType.Temperature>): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    componentType: "Temperature sensor",
  });

const createPcmTemperatureSensor = (
  field: PickKeys<
    ThrsDefinitions["pcm"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Temperature>
  >,
) =>
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
      return tooltip(this.source);
    },
  });

const createConsumerTemperatureSensor = (
  field: PickKeys<
    ThrsDefinitions["consumers"]["sensorValues"],
    SchemaDefinition<SensorComponentType.Temperature>
  >,
) =>
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
      return tooltip(this.source);
    },
  });

export const PCM_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-60": createPcmTemperatureSensor("pcmTemperatureModule1"),
    "1038-33": createPcmTemperatureSensor("pcmTemperatureModule2"),
    "1038-34": createPcmTemperatureSensor("pcmTemperatureModule3"),
    "1038-35": createPcmTemperatureSensor("pcmTemperatureModule4"),
    "1038-48": createConsumerTemperatureSensor("consumersTemperatureDhwReturn"),
    "1038-49": createConsumerTemperatureSensor("consumersTemperatureAdsorptionReturn"),
    "1038-53": createConsumerTemperatureSensor("consumersTemperatureDhwSupply"),
    "1038-54": createConsumerTemperatureSensor("consumersTemperatureAdsorptionSupply"),
    "1038-31": createPcmTemperatureSensor("pcmTemperatureProducersReturn"),
    "1038-55": createPcmTemperatureSensor("pcmTemperatureProducersSupply"),
  },
});
