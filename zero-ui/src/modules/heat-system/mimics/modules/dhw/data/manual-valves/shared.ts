import { TooltipContent } from "@/modules/heat-system/components/tooltip";
import { ModuleField } from "@/modules/heat-system/mimics/providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Manual valve",
    componentType: "Manual valve",
  });
