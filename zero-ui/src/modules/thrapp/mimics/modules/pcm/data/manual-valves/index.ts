import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Manual valve",
    componentType: "Manual valve",
  });

const ids = ["1168-23", "1168-24", "1168-25", "1168-26", "1067-09", "1067-10", "??????"] as const;

const manualValve = (yardTag: string) =>
  toInstance<MimicComponentType.ManualValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("pcm", {
      yardTag,
      technicalName: `pcm-manual-valve-${yardTag}`,
    }),
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const PCM_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(ids.map((id) => [id, manualValve(id)])),
});
