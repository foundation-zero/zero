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
    source: getCustomField("pcm", {
      yardTag,
      technicalName: `pcm-manual-pressure-sensor-${yardTag}`,
    }),
    sensors: {},
    get tooltip() {
      return tooltip(this.source);
    },
  });

const ids = ["1095-06", "1096-09"] as const;

export const PCM_PRESSURE_GAUGE_DATA = toFieldsMap({
  [MimicComponentType.PressureGauge]: Object.fromEntries(ids.map((id) => [id, pressureGauge(id)])),
});
