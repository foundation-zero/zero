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

const ids = [
  "1169-05",
  "1169-04",
  "1168-12",
  "1168-30",
  "1168-31",
  "1168-32",
  "1069-06",
  "1169-07",
  "1169-08",
  "1169-09",
  "1191-01",
  "1191-02",
  "1170-05",
  "1170-06",
  "1177-01",
  "1177-02",
  "1167-11",
  "1168-19",
];

const manualValve = (yardTag: string) =>
  toInstance<MimicComponentType.ManualValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("pvt", {
      yardTag: yardTag,
      technicalName: `pvt-manual-valve-${yardTag}`,
    }),
    get tooltip() {
      return tooltip(this.source);
    },
  });

export const PVT_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(ids.map((id) => [id, manualValve(id)])),
});
