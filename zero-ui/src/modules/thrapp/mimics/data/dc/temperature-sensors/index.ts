import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { measuredTemperatureFields, toTemperatureSensor } from "../../helpers";

export const DC_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-15": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAftSupply"),
      ),
    ),
    "1038-17": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureRecoveryMix"),
      ),
    ),
    "1038-18": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureSupply"),
      ),
    ),
    "1038-19": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureFwdReturn"),
      ),
    ),
    "1038-20": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAftReturn"),
      ),
    ),
    "1038-52": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureRecovery"),
      ),
    ),
    "1038-58": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureRecoveryReturn"),
      ),
    ),
    "1038-69": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureFwdSupply"),
      ),
    ),
    "1038-70": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureUgridSupply"),
      ),
    ),
    "1038-71": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureUgridReturn"),
      ),
    ),
  },
});
