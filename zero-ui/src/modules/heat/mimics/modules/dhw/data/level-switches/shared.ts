import { TooltipContent } from "@/modules/heat/components/tooltip";
import { ModuleField } from "@/modules/heat/mimics/providers";
import { SensorComponentType } from "@/modules/heat-simulation/types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Level switch",
    componentType: "Level switch",
  });
