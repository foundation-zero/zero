import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.PressureGauge>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: undefined,
  sensors: {},
  tooltip: tooltip({
    yardTag: "1095-01",
    technicalName: "manual-pressure-sensor-1095-01",
    title: "Manual Pressure Sensor",
  }),
});
