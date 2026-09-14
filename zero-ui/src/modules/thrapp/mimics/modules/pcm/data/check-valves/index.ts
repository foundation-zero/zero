import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getCustomField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

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
    source: getCustomField("pcm", {
      yardTag,
      technicalName: `pcm-check-valve-${yardTag}`,
    }),
    sensors: {},
    get tooltip() {
      return tooltip(this.source);
    },
  });

const ids = ["1078-01", "1085-02"] as const;

export const PCM_CHECK_VALVE_DATA = toFieldsMap({
  [MimicComponentType.CheckValve]: Object.fromEntries(ids.map((id) => [id, checkValve(id)])),
});
