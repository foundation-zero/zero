import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { SensorComponentType } from "@/modules/thrs/types";
import { fieldTooltip } from "../shared";

export const tooltip = (
  field: ModuleField<SensorComponentType>,
  content?: Partial<TooltipContent>,
): TooltipContent =>
  fieldTooltip(field, {
    title: "Pressure sensor",
    componentType: "Pressure sensor",
    ...content,
  });
