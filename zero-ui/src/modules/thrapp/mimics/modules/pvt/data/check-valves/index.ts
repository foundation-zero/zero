import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Check valve",
    componentType: "3 way valve DN 25",
  });

const checkValve = (yardTag: string) =>
  toInstance<MimicComponentType.CheckValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: getCustomField("pvt", {
      yardTag: yardTag,
      technicalName: `pvt-check-valve-${yardTag}`,
    }),
    sensors: {},
    get tooltip() {
      return tooltip(this.source);
    },
  });

const ids = ["1077-01", "1077-02", "1076-01", "1188-01", "1188-02", "1188-03", "1085-01"];
export const PVT_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(ids.map((id) => [id, checkValve(id)])),
});
