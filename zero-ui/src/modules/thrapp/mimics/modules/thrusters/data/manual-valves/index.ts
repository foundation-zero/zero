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

const manualValve = (yardTag: string) =>
  toInstance<MimicComponentType.ManualValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("pvt", {
      yardTag: yardTag,
      technicalName: `thrusters-manual-valve-${yardTag}`,
    }),
    get tooltip() {
      return tooltip(this.source);
    },
  });

const ids = [
  "1084-01",
  "1087-08",
  "1212-01",
  "1212-02",
  "1212-03",
  "1212-04",
  "1212-05",
  "1212-06",
  "1212-07",
  "1087-03",
];

export const THRUSTERS_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(ids.map((id) => [id, manualValve(id)])),
});
