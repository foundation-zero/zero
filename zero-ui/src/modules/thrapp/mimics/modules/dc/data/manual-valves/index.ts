import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const placeholderField = <Type extends SensorComponentType>(type: Type) =>
  getField(type, "dc", "placeholder") as unknown as ModuleField<"custom", "dc">;

const tooltip = (field: ModuleField<"custom", "dc">, yardTag: string): TooltipContent =>
  fieldTooltip(field, {
    title: "Manual valve",
    componentType: "Manual valve",
    yardTag,
  });

const manualValve = (yardTag: string) =>
  toInstance<MimicComponentType.ManualValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: placeholderField(SensorComponentType.Valve),
    get tooltip() {
      return tooltip(this.source, yardTag);
    },
  });

const manualValveTags = [
  "1168-27",
  "1168-28",
  "1168-29",
  "1168-15",
  "1168-16",
  "1169-17",
  "1069-18",
  "1067-08",
  "1067-07",
  "1172-05",
  "1172-06",
  "1170-04",
  "1170-03",
  "1167-13",
  "1068-22",
];

export const DC_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    manualValveTags.map((tag) => [tag, manualValve(tag)]),
  ),
});
