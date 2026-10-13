import { TooltipContent } from "@/modules/heat-system/components/tooltip";
import { ModuleField } from "@/modules/heat-system/mimics/providers";
import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow control valve",
    componentType: "Flow control valve DN 20",
  });
