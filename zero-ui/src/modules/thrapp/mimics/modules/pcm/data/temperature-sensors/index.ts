import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType.Temperature>): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    componentType: "Temperature sensor",
  });

const createTemperatureSensor = (field: ModuleField<SensorComponentType.Temperature>) =>
  toInstance<MimicComponentType.TemperatureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: field,
    sensors: {},
    get tooltip() {
      return fieldTooltip(field, {
        title: "Temperature sensor",
        componentType: "Temperature sensor",
      });
    },
  });

export const PCM_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-60": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule1"),
    ),
    "1038-33": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule2"),
    ),
    "1038-34": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule3"),
    ),
    "1038-35": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule4"),
    ),
    "1038-48": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "consumers", "consumersTemperatureDhwReturn"),
    ),
    "1038-49": createTemperatureSensor(
      getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureAdsorptionReturn",
      ),
    ),
    "1038-53": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "consumers", "consumersTemperatureDhwSupply"),
    ),
    "1038-54": createTemperatureSensor(
      getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureAdsorptionSupply",
      ),
    ),
    "1038-31": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersReturn"),
    ),
    "1038-55": createTemperatureSensor(
      getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersSupply"),
    ),
  },
});
