import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

export const PCM_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-60": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule1"),
    }),
    "1038-33": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule2"),
    }),
    "1038-34": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule3"),
    }),
    "1038-35": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureModule4"),
    }),
    "1038-48": toTemperatureSensor({
      source: getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureDhwReturn",
      ),
    }),
    "1038-49": toTemperatureSensor({
      source: getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureAdsorptionReturn",
      ),
    }),
    "1038-53": toTemperatureSensor({
      source: getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureDhwSupply",
      ),
    }),
    "1038-54": toTemperatureSensor({
      source: getField(
        SensorComponentType.Temperature,
        "consumers",
        "consumersTemperatureAdsorptionSupply",
      ),
    }),
    "1038-31": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersReturn"),
    }),
    "1038-55": toTemperatureSensor({
      source: getField(SensorComponentType.Temperature, "pcm", "pcmTemperatureProducersSupply"),
    }),
  },
});
