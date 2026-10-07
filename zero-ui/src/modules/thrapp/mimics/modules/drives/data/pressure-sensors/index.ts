import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const pressureSensor = () => {
  const source = getField(SensorComponentType.Pressure, "drives", "drivesPressure");
  return toInstance<MimicComponentType.PressureSensor>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source,
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Pressure sensor",
        componentType: "Pressure sensor",
      });
    },
  });
};

export const DRIVES_PRESSURE_SENSOR_DATA = toFieldsMap({
  [MimicComponentType.PressureSensor]: {
    "1097-10": pressureSensor(),
  },
});
