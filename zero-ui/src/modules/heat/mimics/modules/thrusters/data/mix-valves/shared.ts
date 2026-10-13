import { TooltipContent } from "@/modules/heat/components/tooltip";
import { ModuleField } from "@/modules/heat/mimics/providers";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Mix valve",
    componentType: "Mix valve",
  });
