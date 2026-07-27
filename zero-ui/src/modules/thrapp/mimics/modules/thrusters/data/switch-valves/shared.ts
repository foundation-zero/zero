import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../dhw/data/shared";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Switch valve",
    componentType: "2 way valve DN 25",
  });
