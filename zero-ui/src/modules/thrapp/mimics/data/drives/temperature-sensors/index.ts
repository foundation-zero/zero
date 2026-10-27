import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { measuredTemperatureFields, toTemperatureSensor } from "../../helpers";

export const DRIVES_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-64": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdriveAft2Return"),
      ),
    ),
    "1038-32": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdriveAft1Return"),
      ),
    ),
    "1038-72": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdriveFwd2Return"),
      ),
    ),
    "1038-61": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdriveFwd1Return"),
      ),
    ),
    "1038-63": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdrivesAftSupply"),
      ),
    ),
    "1038-62": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperaturePropdrivesFwdSupply"),
      ),
    ),
    "1038-11": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperatureShorepowerReturn"),
      ),
    ),
    "1038-16": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperatureRecovery"),
      ),
    ),
    "1038-14": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperatureSupply"),
      ),
    ),
    "1038-59": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperatureRecoveryReturn"),
      ),
    ),
    "1038-57": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "drives", "drivesTemperatureRecoveryMix"),
      ),
    ),
  },
});
