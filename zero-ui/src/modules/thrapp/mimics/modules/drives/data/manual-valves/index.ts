import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap, toInstance } from "../../..";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Manual valve",
    componentType: "Manual valve",
  });

const ids = [
  "1087-04",
  "1087-05",
  "1087-06",
  "1087-07",
  "1085-04",
  "1085-05",
  "1085-02",
  "1085-03",
  "1086-01",
  "1086-02",
  "1086-09",
  "1086-10",
  "1086-06",
  "1086-05",
  "1086-07",
  "1086-08",
  "1084-02",
  "1087-01",
  "1073-02",
  "1073-01",
] as const;

const manualValve = (yardTag: string) =>
  toInstance<MimicComponentType.ManualValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("drives", {
      yardTag,
      technicalName: `drives-manual-valve-${yardTag}`,
    }),
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const DRIVES_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(ids.map((id) => [id, manualValve(id)])),
});
