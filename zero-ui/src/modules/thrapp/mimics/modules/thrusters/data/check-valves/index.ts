import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../dhw/data/shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Check valve",
    componentType: "Check valve",
  });

const checkValve = (yardTag: string) =>
  toInstance<MimicComponentType.CheckValve>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {},
    source: getCustomField("thrusters", {
      yardTag: yardTag,
      technicalName: `thrusters-check-valve-${yardTag}`,
    }),
    get tooltip() {
      return tooltip(this.source);
    },
  });

const ids = ["1213-01", "1213-02", "1217-01", "1217-02"];

export const THRUSTERS_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(ids.map((id) => [id, checkValve(id)])),
});
