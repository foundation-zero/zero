import { getCustomField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { fieldTooltip } from "../../../shared";

const pressureGauge = (yardTag: string) =>
  toInstance<MimicComponentType.PressureGauge>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("drives", {
      yardTag,
      technicalName: `drives-pressure-gauge-${yardTag}`,
    }),
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "Manual pressure sensor",
        componentType: "Manual pressure sensor",
      });
    },
  });

export const DRIVES_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: {
    "1096-05": pressureGauge("1096-05"),
    "1095-13": pressureGauge("1095-13"),
  },
});
