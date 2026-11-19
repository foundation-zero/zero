import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
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
    "1038-05": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAft4Return"),
      ),
    ),
    "1038-06": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAft3Return"),
      ),
    ),
    "1038-07": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAft2Return"),
      ),
    ),
    "1038-08": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureAft1Return"),
      ),
    ),
    "1038-09": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureUgrid2Return"),
      ),
    ),
    "1038-10": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureUgrid1Return"),
      ),
    ),
    "1038-12": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureFwd2Return"),
      ),
    ),
    "1038-13": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "dc", "dcTemperatureFwd1Return"),
      ),
    ),
  },
});
