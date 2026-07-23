import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Manual pressure sensor",
    componentType: "Manual pressure sensor",
  });

const pressureGauge = (yardTag: string) =>
  toInstance<MimicComponentType.PressureGauge>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getCustomField("pvt", {
      yardTag: yardTag,
      technicalName: `pvt-pressure-gauge-${yardTag}`,
    }),
    sensors: {},
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const PVT_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: {
    "1095-03": pressureGauge("1095-03"),
    "1095-04": pressureGauge("1095-04"),
    "1095-05": pressureGauge("1095-05"),
  },
});
