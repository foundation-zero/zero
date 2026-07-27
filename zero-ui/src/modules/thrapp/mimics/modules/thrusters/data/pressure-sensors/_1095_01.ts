import { getCustomField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../dhw/data/shared";

export default toInstance<MimicComponentType.PressureGauge>({
  controls: {},
  controllerState: {},
  custom: {},
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
