import { SensorComponentType } from "@/modules/thrsim/types";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

// Supply and return temperatures of the PVT owners strings.
export const PVT_OWNERS_TEMPERATURE_SENSORS = {
  "9005-34": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString1Return"),
  }),
  "9005-35": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString2Return"),
  }),
  "9005-36": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString3Return"),
  }),
  "9005-37": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString4Return"),
  }),
  "9005-38": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString5Return"),
  }),
  "9005-39": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString6Return"),
  }),
  "9005-40": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString1Supply"),
  }),
  "9005-41": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString2Supply"),
  }),
  "9005-42": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString3Supply"),
  }),
  "9005-43": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString4Supply"),
  }),
  "9005-44": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString5Supply"),
  }),
  "9005-45": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureOwnersString6Supply"),
  }),
};
