import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { measuredTemperatureFields, toTemperatureSensor } from "../../helpers";

export const ADSORPTION_TEMPERATURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.TemperatureSensor]: {
    "1038-36": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureHotReturn"),
      ),
    ),
    "1038-37": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureHotSupply"),
      ),
    ),
    "1038-39": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureWasteSupply"),
      ),
    ),
    "1038-41": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureHtReturn"),
      ),
    ),
    "1038-50": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureHtSupply"),
      ),
    ),
    "1038-56": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "adsorptionTemperatureDhwReturn"),
      ),
    ),
    // The design tags this sensor 9005-01/02; it has no thrsim field yet.
    "9005-01/02": toTemperatureSensor(
      measuredTemperatureFields(
        getField(SensorComponentType.Temperature, "adsorption", "placeholder"),
      ),
      { yardTag: "9005-01/02" },
    ),
  },
});
