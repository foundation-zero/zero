import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { getField } from "../../../providers";
import { toTemperatureSensor } from "../../helpers";

// Supply and return temperatures of the PVT AFT strings.
export const PVT_AFT_TEMPERATURE_SENSORS = {
  "9005-01": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString1_1Return"),
  }),
  "9005-02": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString1_2Return"),
  }),
  "9005-03": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString2_1Return"),
  }),
  "9005-04": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString2_2Return"),
  }),
  "9005-05": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString3Return"),
  }),
  "9005-06": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString4Return"),
  }),
  "9005-07": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString5_1Return"),
  }),
  "9005-08": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString5_2Return"),
  }),
  "9005-09": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString6_1Return"),
  }),
  "9005-10": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString6_2Return"),
  }),
  "9005-11": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString7_1Return"),
  }),
  "9005-12": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString7_2Return"),
  }),
  "9005-13": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString8_1Return"),
  }),
  "9005-14": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString8_2Return"),
  }),
  "9005-15": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString9Return"),
  }),
  "9005-16": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString10Return"),
  }),
  "9005-17": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString11_1Return"),
  }),
  "9005-18": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString11_2Return"),
  }),
  "9005-19": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString12Return"),
  }),
  "9005-20": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString13Return"),
  }),
  "9005-21": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString6Supply"),
  }),
  "9005-22": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString5Supply"),
  }),
  "9005-23": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString4Supply"),
  }),
  "9005-24": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString3Supply"),
  }),
  "9005-25": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString2Supply"),
  }),
  "9005-26": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString1Supply"),
  }),
  "9005-27": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString7Supply"),
  }),
  "9005-28": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString8Supply"),
  }),
  "9005-29": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString9Supply"),
  }),
  "9005-30": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString10Supply"),
  }),
  "9005-31": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString11Supply"),
  }),
  "9005-32": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString12Supply"),
  }),
  "9005-33": toTemperatureSensor({
    source: getField(SensorComponentType.Temperature, "pvt", "pvtTemperatureMainString13Supply"),
  }),
};
