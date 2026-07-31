import { getCustomField } from "@/modules/thrapp/mimics/providers";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

export default toInstance<MimicComponentType.PressureGauge>({
  controls: {},
  controllerState: {},
  custom: {},
  parameters: {},
  source: getCustomField("dhw", {
    technicalName: "dhw-manual-pressure-sensor-1095-14",
    yardTag: "1095-14",
  }),
  sensors: {},

  get tooltip() {
    return fieldTooltip(this.source, {
      title: "Manual pressure sensor",
      componentType: "Manual pressure sensor",
    });
  },
});
