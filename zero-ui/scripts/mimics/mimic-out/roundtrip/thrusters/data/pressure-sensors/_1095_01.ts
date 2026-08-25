import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

import { getCustomField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
export default toInstance<MimicComponentType.PressureGauge>({
  custom: {},
  controls: {},
  controllerState: {},
  parameters: {},
  source: getCustomField("thrusters", {
      yardTag: "1095-01",
      technicalName: "manual-pressure-sensor-1095-01",
    }),
  sensors: {},
  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Manual Pressure Sensor",
    });
  },
});
